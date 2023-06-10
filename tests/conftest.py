"""Global fixture functions."""

# pylint: disable = redefined-outer-name

from collections.abc import AsyncGenerator, Generator

import aiohttp
import pytest
from aioresponses import aioresponses

from pylaundry import Laundry
from pylaundry.const import API_ENDPOINT_URL

from .http_bodies import get_http_body

#
# Meta Fixtures
#


@pytest.fixture
def response_mocker() -> Generator:
    """Yield aioresponses."""
    with aioresponses() as mocker:
        yield mocker


@pytest.fixture
@pytest.mark.asyncio
async def laundry() -> AsyncGenerator:
    """Build and return dummy controller for testing without Alarm.com API."""

    async with aiohttp.ClientSession() as websession:
        yield Laundry(websession=websession)


#
# Response Fixtures
#


@pytest.fixture
def additional_information__response__success(response_mocker: aioresponses) -> None:
    """Success response for additional information."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("additional_information__response__success"),
    )


@pytest.fixture
def authentication__response__success(response_mocker: aioresponses) -> None:
    """Success response for authentication."""

    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("authentication__response__success"),
        headers={"CP_AUTH_TOKEN": "e94eca12-854f-409e-b32f-302805ed12d9"},
    )


@pytest.fixture
def authentication__response__incorrect_credentials(
    response_mocker: aioresponses,
) -> None:
    """Incorrect credentials response for authentication."""

    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("authentication__response__incorrect_credentials"),
        headers={"CP_AUTH_TOKEN": "e94eca12-854f-409e-b32f-302805ed12d9"},
    )


@pytest.fixture
def consolidated_refresh__response__success(response_mocker: aioresponses) -> None:
    """Success response for consolidated refresh."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("consolidated_refresh__response__success"),
    )


@pytest.fixture
def general__response__incorrect_packing(response_mocker: aioresponses) -> None:
    """Incorrect packing response for any request."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("general__response__incorrect_packing"),
    )


@pytest.fixture
def get_vend_price__response__success(response_mocker: aioresponses) -> None:
    """Success response for get vend price."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("get_vend_price__response__success"),
    )


@pytest.fixture
def vend_log_topoff__response__success(response_mocker: aioresponses) -> None:
    """Success response for vend log."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("vend_log_topoff__response__success"),
    )


@pytest.fixture
def virtual_vend_topoff__response__success(response_mocker: aioresponses) -> None:
    """Success response for virtual vend topoff."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("virtual_vend_topoff__response__success"),
    )


#
# Request Fixtures
#

# TODO: Test request objects.


@pytest.fixture
def additional_information__request(response_mocker: aioresponses) -> None:
    """Request for additional information."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("additional_information__request"),
    )


@pytest.fixture
def authentication__request(response_mocker: aioresponses) -> None:
    """Request for authentication."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("authentication__request"),
    )


@pytest.fixture
def consolidated_refresh__request(response_mocker: aioresponses) -> None:
    """Request for consolidated refresh."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("consolidated_refresh__request"),
    )


@pytest.fixture
def get_vend_price__request(response_mocker: aioresponses) -> None:
    """Request for get vend price."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("get_vend_price__request"),
    )


@pytest.fixture
def vend_log__request(response_mocker: aioresponses) -> None:
    """Request for vend log."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("vend_log__request"),
    )


@pytest.fixture
def virtual_vend__request(response_mocker: aioresponses) -> None:
    """Request for virtual vend."""

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=get_http_body("virtual_vend__request"),
    )
