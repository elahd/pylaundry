"""Functions for packing and unpacking messages."""

from __future__ import annotations

import base64
import gzip
import json
import logging
import urllib.parse
import uuid

from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import modes

from .const import AES_IV
from .const import AES_SUFFIX_PREAUTH
from .const import LOG_LEVEL_TRACE
from .exceptions import MessagePackerError

log = logging.getLogger(__name__)


class MessagePacker:
    """Functions for packing and unpacking client <-> server messages."""

    @staticmethod
    def unpack_server_response(response_body: bytes) -> dict | None:
        """Unpack API response into string."""

        # Unpacking Steps:
        #     1. Base64 decode.
        #     2. gzip decompress.

        log.log(
            LOG_LEVEL_TRACE, "==============[ UNPACKING RESPONSE BEGIN ]=============="
        )

        decoded_as_bytes = base64.standard_b64decode(response_body)

        log.log(
            LOG_LEVEL_TRACE,
            "Base64Decode Bytes -> Bytes:\n%s\n\n",
            decoded_as_bytes.hex(),
        )

        gunzipped_as_bytes = gzip.decompress(decoded_as_bytes)

        log.log(
            LOG_LEVEL_TRACE, "gunzip Bytes -> Bytes:\n%s\n\n", decoded_as_bytes.hex()
        )

        try:
            json_response = json.loads(str(gunzipped_as_bytes, "utf-8"))
        except ValueError as err:
            raise err

        log.log(LOG_LEVEL_TRACE, "UNPACKED RESPONSE:\n%s\n\n", json_response)

        log.log(
            LOG_LEVEL_TRACE, "==============[ UNPACKING RESPONSE END ]=============="
        )

        return json_response if isinstance(json_response, dict) else None

    @staticmethod
    def pack_client_request(
        request_body: str | list | dict,
        first_request_id: str | None = None,
        new_request_id: str | None = None,
    ) -> tuple[str, str]:
        """Pack request body for transmission to server."""

        # https://gist.github.com/brysontyrrell/7cebfb05105c25d00e84ed35bd821dfe

        # new_request_id generated automatically. If debugging intercepted communications, provide actual new_request_id

        # Packing Steps:
        #     1. Apply PKCS #7 padding.
        #     2. Encrypt using 128-bit AES/CBC.
        #     3. Base64 encode.
        #     4. Base64 encode, again.
        #     5. URL encode.

        log.log(
            LOG_LEVEL_TRACE, "==============[ PACKING REQUEST BEGIN ]=============="
        )

        log.log(LOG_LEVEL_TRACE, "Original Request Body:\n%s\n\n", request_body)

        if not new_request_id:
            new_request_id = str(uuid.uuid4())

        log.log(LOG_LEVEL_TRACE, "New Request ID: %s", new_request_id)

        key = MessagePacker._generate_aes_key(
            new_request_id=new_request_id, first_request_id=first_request_id
        )

        # PKCS#7 Pad
        padded_request = MessagePacker._pkcs7_pad(bytes(str(request_body), "utf-8"))

        log.log(LOG_LEVEL_TRACE, "Padded Request:\n%s\n\n", padded_request)

        # AES Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(AES_IV))
        encryptor = cipher.encryptor()
        encrypted_request = (
            encryptor.update(bytes(padded_request)) + encryptor.finalize()
        )

        log.log(
            LOG_LEVEL_TRACE,
            "Encrypted Request:\n%s\n\n",
            MessagePacker._format_hex(encrypted_request),
        )

        # 2x Base 64
        b64_encoded_request = base64.urlsafe_b64encode(
            base64.b64encode(encrypted_request)
        )

        log.log(LOG_LEVEL_TRACE, "Base64 Encoded Request:\n%s\n\n", b64_encoded_request)

        # URL Encode
        url_encoded_request = urllib.parse.quote(b64_encoded_request)

        log.log(LOG_LEVEL_TRACE, "URL Encoded Request:\n%s\n\n", url_encoded_request)

        log.log(LOG_LEVEL_TRACE, "==============[ PACKING REQUEST END ]==============")

        return (str(new_request_id), url_encoded_request)

    @staticmethod
    def unpack_client_request(
        request_body: str,
        new_request_id: str,
        first_request_id: str | None = None,
    ) -> str:
        """Unack request body for message transmitted to server. This helps debug manually intercepted communications and would not typically be used when building an interface for this API."""

        # Packing Steps: Reverse of pack_client_request.

        key = MessagePacker._generate_aes_key(
            new_request_id=new_request_id, first_request_id=first_request_id
        )

        # URL Decode
        url_decoded_request = urllib.parse.unquote(request_body)

        log.log(
            LOG_LEVEL_TRACE,
            "[unpack_client_request] URL Decoded Request:\n%s\n\n",
            url_decoded_request,
        )

        # 2x Base 64 Decode
        b64_decoded_request = base64.b64decode(base64.b64decode(url_decoded_request))

        log.log(
            LOG_LEVEL_TRACE,
            "[unpack_client_request] First Base64 Decoded Request:\n%s\n\n",
            base64.b64decode(url_decoded_request),
        )

        log.log(
            LOG_LEVEL_TRACE,
            "[unpack_client_request] Second Base64 Decoded Request:\n%s\n\n",
            MessagePacker._format_hex(b64_decoded_request),
        )

        # AES Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(AES_IV))
        decryptor = cipher.decryptor()
        decrypted_request = decryptor.update(b64_decoded_request) + decryptor.finalize()

        log.log(
            LOG_LEVEL_TRACE,
            "[unpack_client_request] Decrypted Request:\n%s\n\n",
            decrypted_request.hex(),
        )

        # Unpad PKCS#7
        try:
            unpadded_request = MessagePacker._pkcs7_unpad(decrypted_request)
        except UnicodeDecodeError as err:
            raise MessagePackerError("Error unpadding message.") from err

        log.log(
            LOG_LEVEL_TRACE,
            "[unpack_client_request] Unpadded Request:\n%s\n\n",
            unpadded_request,
        )

        return str(unpadded_request, "utf-8")

    @staticmethod
    def _generate_aes_key(
        new_request_id: str, first_request_id: str | None = None
    ) -> bytes:
        """Generate AES encryption key."""

        key_str = ""
        key_bytes = bytes()

        if not first_request_id:

            #
            # Generate key for authentication request. Authentication requests identified by missing first_request_id.
            #

            key_base = ""

            length = len(new_request_id) - 1
            while length >= 0 and len(key_base) < 8:
                key_base = key_base + str(new_request_id[length])
                length -= 2

            key_str = key_base + AES_SUFFIX_PREAUTH
            key_bytes = bytes(key_str, "utf-8")

        else:

            # Generate key for all non-authentication requests by weaving together backwards last and second to last request IDs.

            new_req_id_length = len(str(new_request_id)) - 1
            while new_req_id_length >= 0 and len(key_str) < 8:
                key_str = key_str + str(new_request_id)[new_req_id_length]
                new_req_id_length -= 2

            original_uuid_length = len(str(first_request_id)) - 1
            while original_uuid_length >= 0 and len(key_str) < 16:
                key_str = key_str + str(first_request_id)[original_uuid_length]
                original_uuid_length -= 2

            key_bytes = bytes(key_str, "utf-8")

        log.log(
            LOG_LEVEL_TRACE,
            "Encryption Key: %s (%s)",
            key_str,
            MessagePacker._format_hex(key_bytes),
        )

        return key_bytes

    @staticmethod
    def _pkcs7_pad(message: bytes) -> bytes:
        """Add PKCS #7 padding to a string."""
        return message + bytes(
            chr(16 - len(message) % 16) * (16 - len(message) % 16), "utf-8"
        )

    @staticmethod
    def _pkcs7_unpad(message: bytes) -> bytes:
        """Strip PKCS #7 padding from a string."""
        return message[: -message[-1]]

    @staticmethod
    def _format_hex(hex_input: bytes) -> str:
        """Format hex number grouped by bytes."""

        return hex_input.hex(" ").upper()
