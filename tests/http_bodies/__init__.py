"""HTTP request/response bodies for tests."""

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


def get_http_body(name: str) -> bytes:
    """Get server/client response/request body from JSON file."""

    return pack_server_response(resources.read_text(__package__, f"{name}.json"))
