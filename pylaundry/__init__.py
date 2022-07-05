"""pylaundry library."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from enum import Enum
import hashlib
import json
import logging
import uuid

import aiohttp
import dateutil.parser

from .const import API_ENDPOINT_URL
from .const import APPKEY
from .const import AUTH_TOKEN_KEY
from .const import EMPTY_AUTH_TOKEN
from .const import LOG_LEVEL_TRACE
from .const import REFRESH_REQUEST_PREHASH_SUFFIX
from .const import RESULT_CODE_KEY
from .const import RESULT_TEXT_KEY
from .const import ServerResponseCodes
from .exceptions import AuthenticationError
from .exceptions import CommunicationError
from .exceptions import MachineNotFound
from .exceptions import NotLoggedIn
from .exceptions import Rejected
from .exceptions import ResponseFormatError
from .exceptions import UnexpectedError
from .exceptions import VendFailure
from .exceptions import VendLogFailure
from .helpers import MessagePacker

__version__ = "v0.1.3"

log = logging.getLogger(__name__)


class MachineType(Enum):
    """Laundry machine types."""

    WASHER = "Washer"
    DRYER = "Dryer"
    UNKNOWN = "Unknown"


@dataclass
class LaundryMachine:
    """Representation of a washer or dryer."""

    id_: str
    type: MachineType
    number: str
    busy: bool | None
    minutes_remaining: int | None
    base_price: float | None
    topoff_price: float | None
    online: bool | None
    reader_serial: str | None


@dataclass
class LaundryProfile:
    """Metadata for location and user's virtual card."""

    location_address: str
    card_balance: float
    user_id: str
    user_token: str
    location_id: str
    database_id: str | None
    card_serial: str | None


class Laundry:
    """pylaundry's controller."""

    profile: LaundryProfile
    machines: dict
    encryption_keys: list[str]

    def __init__(self, websession: aiohttp.ClientSession) -> None:
        """Initialize pylaundry."""

        self._websession: aiohttp.ClientSession = websession
        self._first_request_id: str | None = None
        self._auth_token: str = EMPTY_AUTH_TOKEN

        self._username: str | None = None
        self._password: str | None = None

        self.installation_token = str(uuid.uuid4())

    async def async_login(self, username: str, password: str) -> None:
        """Log in to Laundry Link."""

        # We need to store these for error recovery in _send_request().
        self._username = username
        self._password = password

        try:
            request_data = [
                "Authenticate2",
                APPKEY,
                username,
                password,
                self.installation_token,
                '{"droidDisplay":"LMY47E","droidBrand":"Android","droidProduct":"sdk_phone_x86","droidDevice":"shamu","droidManufacturer":"motorola","droidModel":"Nexus'
                ' 6","droidHardware":"ranchu","droidSDK":28,"droidVersionRelease":"9","droidVersionIncremental":"4923214","droidVersionCodeName":"REL","droidIsRooted":false,"droidAppVersion":"4.09","droidAppBundleID":"com.esd.laundrylink.hercules"}',
            ]

            response = await self._send_request(json.dumps(request_data))

        except (
            CommunicationError,
            ResponseFormatError,
            Rejected,
            AuthenticationError,
        ) as err:
            raise err

        self._process_machine_data(
            response.get("Bundle", {}).get("MachinesInformation", {})
        )

        # Assemble user token
        user_token_raw = (
            f"{(user_id := response['UserID'])}{REFRESH_REQUEST_PREHASH_SUFFIX}"
        )

        log.log(LOG_LEVEL_TRACE, "Secret Raw:\n%s\n\n", user_token_raw)

        userhash_md5 = hashlib.md5(bytes(user_token_raw, "utf-8"))  # nosec

        user_token = userhash_md5.hexdigest()

        # Assemble profile
        self.profile = LaundryProfile(
            location_address=response["LocationAddress"],
            card_balance=response.get("Bundle", {})
            .get("CardInformation", {})
            .get("Balance"),
            user_id=user_id,
            location_id=response["LocationID"],
            database_id=response["DatabaseID"],
            card_serial=response.get("Bundle", {})
            .get("CardInformation", {})
            .get("AccountNumber"),
            user_token=user_token,
        )

    async def async_get_encryption_keys(self) -> None:
        """Get encryption keys from server."""

        # Purpose of these keys is TBD. Presumably, they're used for dispense / reload transactions.

        if self._auth_token == EMPTY_AUTH_TOKEN:
            raise NotLoggedIn

        request_data = ["GetAdditionalInformation", APPKEY]

        response = await self._send_request(json.dumps(request_data))

        if len(values := response.get("Values", [])) > 0 and isinstance(values, list):
            self.encryption_keys = values
        else:
            log.error("Failed to retrieve encryption keys.")

    async def async_refresh(self) -> None:
        """Get updated machine status."""

        if self._auth_token == EMPTY_AUTH_TOKEN:
            raise NotLoggedIn

        request_data = [
            "ConsolidatedRefresh",
            self.profile.user_token,
            self.profile.user_id,
        ]

        response = await self._send_request(json.dumps(request_data))

        # Refresh card balance.
        self.profile.card_balance = (
            balance
            if (balance := response.get("CardInformation", {}).get("Balance"))
            else None
        )

        # Refresh machine status.
        self._process_machine_data(response.get("MachinesInformation", {}))

    async def async_get_topoff_price(self, machine_id: str) -> None:
        """Get topoff price for single machine, then update machine with price."""

        if self._auth_token == EMPTY_AUTH_TOKEN:
            raise NotLoggedIn

        machine: LaundryMachine = self.machines[machine_id]

        request_data = [
            "GetVendPrice",
            self.profile.user_token,
            self.profile.database_id,
            machine.reader_serial,
        ]

        response = await self._send_request(json.dumps(request_data))

        if isinstance(machine := self.machines[machine_id], LaundryMachine):
            machine.topoff_price = response.get("TopoffPrice")

    async def _async_log_vend(
        self, machine_id: str, error_code: int, vend_success: bool
    ) -> None:
        """Log vend for a single machine."""

        # CyclePay logs each vend using this request, but this doesn't seem to be necessary to adding value to a machine.
        # Just using async_vend() is sufficient to vend and update the user-facing activity log.

        if self._auth_token == EMPTY_AUTH_TOKEN:
            raise NotLoggedIn

        try:
            machine = self.machines[machine_id]
        except AttributeError as err:
            raise MachineNotFound(machine_id) from err

        if not isinstance(machine, LaundryMachine):
            raise MachineNotFound(machine_id)

        request_data = [
            "CreateVendLogEntry",
            self.profile.user_token,
            self.profile.user_id,
            str(datetime.now(timezone.utc)),
            self.profile.card_serial,
            machine.reader_serial,
            machine.number,
            error_code,
            vend_success,
            False,
            machine.base_price,  # Always base price, even when topping off
        ]

        response = await self._send_request(json.dumps(request_data))

        if response.get("ResultCode") != 1:
            log.error("Failed to log vend. Response: %s", response)
            raise VendLogFailure

    async def async_vend(self, machine_id: str) -> None:
        """Vend a single machine and log result."""

        if self._auth_token == EMPTY_AUTH_TOKEN:
            raise NotLoggedIn

        machine: LaundryMachine = self.machines[machine_id]

        request_data = [
            "VirtualVend",
            self.profile.user_token,
            self.profile.database_id,
            machine.reader_serial,
            self.profile.card_serial,
        ]

        try:
            response = await self._send_request(json.dumps(request_data))
        except (
            UnexpectedError,
            ResponseFormatError,
            Rejected,
            CommunicationError,
        ) as err:
            log.error("Communication error while vending.")
            raise VendFailure from err

        if response.get("ResultCode") not in [1, 161]:
            log.error("Failed to vend machine. Response: %s", response)
            raise VendFailure

        log.debug("Vend successful.")

        # Bypassing log. See note in _async_log_vend() for details.

        # try:
        #     await self._async_log_vend(
        #         machine_id=machine_id,
        #         error_code=response["ResultCode"],
        #         vend_success=True,
        #     )
        # except (
        #     UnexpectedError,
        #     ResponseFormatError,
        #     Rejected,
        #     CommunicationError,
        #     VendLogFailure,
        # ) as err:
        #     log.error("Error logging vend.")
        #     raise VendLogFailure from err

    def _process_machine_data(self, machines_info_object: dict) -> None:
        """Update machine data from API MachinesInformation object."""

        if machines_info_object.get(RESULT_CODE_KEY) != 1:
            log.error("Problem with machines response: %s", machines_info_object)

        machines: dict = {}

        machine: dict
        for machine in machines_info_object.get("Machines", []):

            try:
                machine_id = machine["ReaderID"]

                machine_type = MachineType.UNKNOWN
                if (setup_type := machine.get("SetupType")) == "Dryer":
                    machine_type = MachineType.DRYER
                elif setup_type == "Washer":
                    machine_type = MachineType.WASHER

                # Determine how long ago state was reported.
                state_age_min = (
                    datetime.now(timezone.utc)
                    - dateutil.parser.isoparse(machine["StateDateTimeUtc"])
                ).total_seconds() / 60

                # Adjust minutes remaining by state age.
                minutes_remaining = max(
                    0, round(machine.get("MinutesRemaining", 0) - state_age_min)
                )

                machines[machine_id] = LaundryMachine(
                    id_=machine["ReaderID"],
                    type=machine_type,
                    number=machine["Label"],
                    busy=minutes_remaining > 0,
                    minutes_remaining=minutes_remaining,
                    base_price=machine.get("BasePrice"),
                    online=bool(is_online)
                    if (is_online := machine.get("IsOnline")) in [True, False]
                    else None,
                    reader_serial=machine.get("SerialNumber"),
                    topoff_price=None,
                )

            except KeyError:
                log.error("Failed to retrieve data for a machine: %s", machine)

        self.machines = machines

    async def _send_request(self, request_json: str, no_retry: bool = False) -> dict:
        """Send submitted request body to server. Handles body formatting and headers and updates session objects."""

        request_id, packed_request_data = MessagePacker.pack_client_request(
            request_body=request_json,
            first_request_id=self._first_request_id,
        )

        if self._first_request_id is None:
            self._first_request_id = request_id

        request_headers = {
            "CP_REQ_ID": request_id,
            AUTH_TOKEN_KEY: self._auth_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        log.log(
            LOG_LEVEL_TRACE, "==============[ BUILDING REQUEST BEGIN ]=============="
        )
        log.log(LOG_LEVEL_TRACE, "** REQUEST HEADERS **")
        log.log(LOG_LEVEL_TRACE, request_headers)

        request_body = f"CP_REQ_DATA={packed_request_data}"

        log.log(LOG_LEVEL_TRACE, "** REQUEST BODY **")
        log.log(LOG_LEVEL_TRACE, request_body)

        log.log(LOG_LEVEL_TRACE, "==============[ BUILDING REQUEST END ]==============")

        try:
            async with self._websession.post(
                url=API_ENDPOINT_URL, data=request_body, headers=request_headers
            ) as resp:

                # We can't use resp.json() because server returns JSON object in response with incorrect mimetype. This causes aiohttp to raise an aiohttp.client_exceptions.ContentTypeError exception.
                raw_response = await resp.text()
        except (
            asyncio.TimeoutError,
            aiohttp.ClientError,
            asyncio.exceptions.CancelledError,
        ) as err:
            log.error("Failed to send request.")

            raise CommunicationError from err

        log.log(LOG_LEVEL_TRACE, "RAW SERVER RESPONSE:\n%s\n\n", raw_response)

        #
        # Validate response format.
        #

        # Expected response format is {"Response": PACKED_RESPONSE_CONTENT}

        try:
            raw_response_json = dict(json.loads(raw_response))
        except (json.JSONDecodeError, TypeError) as err:
            raise ResponseFormatError("Server response not a JSON dict.") from err

        # If auth token is returned, update local.
        if auth_token := resp.headers.get(AUTH_TOKEN_KEY):
            self._auth_token = auth_token

        # Isolate response content

        if not (response_content := raw_response_json.get("Response")):
            raise UnexpectedError("Couldn't find response content.")

        # Unpack response

        unpacked_content = MessagePacker.unpack_server_response(response_content)

        if not unpacked_content:
            raise UnexpectedError("Missing unpacked content.")

        log.log(LOG_LEVEL_TRACE, "UNPACKED RESPONSE CONTENT:\n%s\n\n", unpacked_content)

        response_code = unpacked_content.get(RESULT_CODE_KEY)

        # Check response code (in body).

        if (
            not response_code
            or (
                (response_code := unpacked_content.get(RESULT_CODE_KEY))
                == ServerResponseCodes.INVALID_REQUEST
            )
            or (response_code == ServerResponseCodes.INPUT_MALFORMED and no_retry)
        ):
            log.debug("UNPACKED RESPONSE CONTENT:\n%s\n\n", unpacked_content)
            raise Rejected

        if response_code == ServerResponseCodes.INPUT_MALFORMED:
            # This error may occur if the server doesn't like the submitted first_request_id. We should retry once after clearing tokens and logging back in.

            self._first_request_id = None
            self._auth_token = EMPTY_AUTH_TOKEN

            try:
                if not self._username or not self._password:
                    raise AuthenticationError

                await self.async_login(username=self._username, password=self._password)
            except Exception as err:
                raise Rejected("Request failed even after re-trying login.") from err

            return await self._send_request(request_json=request_json, no_retry=True)

        if response_code == ServerResponseCodes.INVALID_CREDENTIALS:
            raise AuthenticationError

        if response_code == ServerResponseCodes.TRY_AGAIN_LATER_BAD_REQUEST:
            raise CommunicationError

        if response_code == ServerResponseCodes.TRY_AGAIN_LATER_SWIPE_FAILED:
            log.error(msg := "Swipe failed. Machine is probably offline.")
            raise VendFailure(msg)

        if response_code != ServerResponseCodes.SUCCESS:
            log.error(
                "Got unexpected response code %s (%s).",
                response_code,
                unpacked_content.get(RESULT_TEXT_KEY),
            )
            raise UnexpectedError

        log.log(
            LOG_LEVEL_TRACE, "EXTRACTED RESPONSE CONTENT:\n%s\n\n", unpacked_content
        )

        return unpacked_content
