"""Log in, pull data, dump to console."""
from __future__ import annotations

import asyncio

import aiohttp

from .pylaundry import Laundry

USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"


async def main() -> None:
    """Log in, pull data, dump to console."""

    async with aiohttp.ClientSession() as session:
        laundry = Laundry(session)
        await laundry.async_login(USERNAME, PASSWORD)

        print(laundry.profile)
        print(laundry.machines)

        await laundry.async_get_encryption_keys()

        print(laundry.encryption_keys)

        await laundry.async_refresh()

        print(laundry.machines)

    await session.close()


asyncio.run(main())
