"""Load responses from JSON files."""

import base64
import gzip
from importlib import resources
import json


def pack_server_response(response_body: str) -> bytes:
    """Pack API response into string to simulate actual server response."""

    response_bytes = bytes(response_body, "utf-8")

    gzipped_as_bytes = gzip.compress(response_bytes)

    encoded_as_bytes = str(base64.standard_b64encode(gzipped_as_bytes), "utf-8")

    return bytes(json.dumps({"Response": encoded_as_bytes}), "utf-8")


ADDITIONAL_INFORMATION_REQUEST_BODY = pack_server_response(
    resources.read_text(
        __package__,
        "additional_information_request.json",
    )
)

ADDITIONAL_INFORMATION_OK_RESPONSE_BODY = pack_server_response(
    resources.read_text(
        __package__,
        "additional_information_response.json",
    )
)

AUTHENTICATION_OK_RESPONSE_BODY = pack_server_response(
    resources.read_text(
        __package__,
        "authentication_response.json",
    )
)

AUTHENTICATION_INCORRECT_CREDS_RESPONSE_BODY = pack_server_response(
    resources.read_text(
        __package__,
        "authentication_incorrect_credentials_response.json",
    )
)

CONSOLIDATED_REFRESH_REQUEST_BODY = pack_server_response(
    resources.read_text(
        __package__,
        "consolidated_refresh_request.json",
    )
)

CONSOLIDATED_REFRESH_OK_RESPONSE_BODY = pack_server_response(
    resources.read_text(
        __package__,
        "consolidated_refresh_response.json",
    )
)

INCORRECT_PACKING_ERROR_RESPONSE_BODY = pack_server_response(
    resources.read_text(
        __package__,
        "incorrect_packing_error_response.json",
    )
)
