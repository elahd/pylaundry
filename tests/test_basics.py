"""Tests for basic functions."""

# pylint: disable=protected-access, missing-class-docstring, no-self-use

import uuid

import aiohttp
from pylaundry import Laundry
from pylaundry import LaundryMachine
from pylaundry.const import EMPTY_AUTH_TOKEN
from pylaundry.exceptions import AuthenticationError
import pytest

# import json

# from deepdiff import DeepDiff


def test_property__initial_state(laundry: Laundry) -> None:
    """Ensure that login data is ingested correctly."""

    assert not laundry._password
    assert not laundry._username
    assert not laundry._first_request_id

    with pytest.raises(AttributeError):
        assert getattr(laundry, "encryption_keys")

    with pytest.raises(AttributeError):
        assert getattr(laundry, "profile")

    with pytest.raises(AttributeError):
        assert getattr(laundry, "machines")

    assert isinstance(laundry._websession, aiohttp.ClientSession)

    assert uuid.UUID(laundry.installation_token)

    assert laundry._auth_token == EMPTY_AUTH_TOKEN


@pytest.mark.asyncio  # type: ignore
async def test__async_login__success__basic_info(
    laundry: Laundry, authentication__response__success: pytest.fixture
) -> None:
    """Test authentication success."""

    await laundry.async_login(username="test@example.com", password="hunter2")

    assert laundry._username == "test@example.com"
    assert laundry._password == "hunter2"

    assert uuid.UUID(laundry._first_request_id)
    assert uuid.UUID(laundry._auth_token)
    assert uuid.UUID(laundry.installation_token)
    assert laundry.machines
    assert laundry.profile


@pytest.mark.asyncio  # type: ignore
async def test__async_login__response__incorrect_credentials(
    laundry: Laundry, authentication__response__incorrect_credentials: pytest.fixture
) -> None:
    """Test authentication failure."""

    with pytest.raises(AuthenticationError):
        await laundry.async_login(
            username="incorrect@example.com", password="incorrect"
        )


@pytest.mark.asyncio  # type: ignore
async def test__async_login__success__profile(
    laundry: Laundry, authentication__response__success: pytest.fixture
) -> None:
    """Test authentication success."""

    await laundry.async_login(username="test@example.com", password="hunter2")

    assert laundry.profile.card_balance == 1.75
    assert (
        laundry.profile.location_address
        == "270 Commerce Dr., Fort Washington, PA 19034"
    )
    assert laundry.profile.location_id == "dd240cf3-7702-5101-8b5b-6dbcdda95d07"
    assert laundry.profile.user_id == "4e353d4d-a9c9-5867-9324-99dbe26d9c35"


@pytest.mark.asyncio  # type: ignore
async def test__async_login__success__machines(
    laundry: Laundry, authentication__response__success: pytest.fixture
) -> None:
    """Test authentication success."""

    # Login
    await laundry.async_login(username="test@example.com", password="hunter2")

    assert isinstance(laundry.machines, dict)

    assert isinstance(
        test_machine := laundry.machines.get("a312b4b7-5110-5775-9966-ed9a6e087e3a"),
        LaundryMachine,
    )

    assert test_machine.minutes_remaining == 0
    assert test_machine.number == "03"
    assert test_machine.busy is False
    assert test_machine.online is True
    assert test_machine.base_price == 1.5


@pytest.mark.asyncio  # type: ignore
async def test__consolidated_refresh__succcess(
    laundry: Laundry,
    authentication__response__success: pytest.fixture,
    consolidated_refresh__response__success: pytest.fixture,
) -> None:
    """Test that consolidated refresh updates macine states."""

    # Login
    await laundry.async_login(username="test@example.com", password="hunter2")

    # Consolidated refresh
    await laundry.async_refresh()

    assert isinstance(laundry.machines, dict)

    assert isinstance(
        test_machine := laundry.machines.get("a312b4b7-5110-5775-9966-ed9a6e087e3a"),
        LaundryMachine,
    )

    assert test_machine.base_price == 200


@pytest.mark.asyncio  # type: ignore
async def test__virtual_vend_topoff__success(
    laundry: Laundry,
    authentication__response__success: pytest.fixture,
    virtual_vend_topoff__response__success: pytest.fixture,
    vend_log_topoff__response__success: pytest.fixture,
) -> None:
    """Test that vend function doesn't raise exception."""

    # Login
    await laundry.async_login(username="test@example.com", password="hunter2")

    # Vend Machine
    await laundry.async_vend("a312b4b7-5110-5775-9966-ed9a6e087e3a")


@pytest.mark.asyncio  # type: ignore
async def test__vend_log_topoff__success(
    laundry: Laundry,
    authentication__response__success: pytest.fixture,
    vend_log_topoff__response__success: pytest.fixture,
) -> None:
    """Test that vend log function doesn't raise exception."""

    # Login
    await laundry.async_login(username="test@example.com", password="hunter2")

    # Log Vend
    await laundry._async_log_vend("a312b4b7-5110-5775-9966-ed9a6e087e3a", 1, True)
