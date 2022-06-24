"""Global fixture functions."""

# pylint: disable = redefined-outer-name

from collections.abc import AsyncGenerator
from collections.abc import Generator

import aiohttp
from aioresponses import aioresponses
from pylaundry import Laundry
from pylaundry.const import API_ENDPOINT_URL
import pytest
from tests import responses


@pytest.fixture  # type: ignore
def response_mocker() -> Generator:
    """Yield aioresponses."""
    with aioresponses() as mocker:
        yield mocker


@pytest.fixture  # type: ignore
@pytest.mark.asyncio  # type: ignore
async def laundry() -> AsyncGenerator:
    """Build and return dummy controller for testing without Alarm.com API."""

    async with aiohttp.ClientSession() as websession:
        yield Laundry(websession=websession)


@pytest.fixture  # type: ignore
def authentication_ok_response(response_mocker: aioresponses) -> None:
    """Shortcut for including all mocked success responses."""

    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=responses.AUTHENTICATION_OK_RESPONSE_BODY,
        headers={"CP_AUTH_TOKEN": "e94eca12-854f-409e-b32f-302805ed12d9"},
    )


@pytest.fixture  # type: ignore
def authentication_incorrect_creds_response(response_mocker: aioresponses) -> None:
    """Shortcut for including all mocked success responses."""

    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=responses.AUTHENTICATION_INCORRECT_CREDS_RESPONSE_BODY,
        headers={"CP_AUTH_TOKEN": "e94eca12-854f-409e-b32f-302805ed12d9"},
    )


@pytest.fixture  # type: ignore
def consolidated_refresh_success(response_mocker: aioresponses) -> None:
    """Responses for consolidated refresh."""

    # TODO: Test request object.

    # Refresh Response
    response_mocker.post(
        url=API_ENDPOINT_URL,
        status=200,
        body=responses.CONSOLIDATED_REFRESH_OK_RESPONSE_BODY,
    )
