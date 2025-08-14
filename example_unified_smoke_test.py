"""Smoke test."""

import asyncio
import os

from rich import print

from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireApiMode

import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("aiohttp").setLevel(logging.DEBUG)


def parse_env_file() -> None:
    """Parse .env file."""
    with open(".env") as f:
        for line in f:
            try:
                key, value = line.strip().split("=")
                print("Writing key", key)
                os.environ[key] = value
            except FileNotFoundError:
                print("-- Could not find a .env file")
                pass
            except ValueError:
                pass


async def main() -> None:
    """Main smoketest."""
    parse_env_file()

    username = os.environ["IFT_USER"]  # noqa: F841
    password = os.environ["IFT_PASS"]  # noqa: F841

    # Make cloud interface
    cloud_interface = IntelliFireCloudInterface(use_http=True)

    # Load in user data
    user_json: str = os.getenv("USER_JSON")  # type: ignore
    user_data = cloud_interface.load_user_data(user_json)

    fp = (
        await UnifiedFireplace.build_fireplaces_from_user_data(
            user_data, use_http=True, verify_ssl=False
        )
    )[0]

    await fp.set_read_mode(IntelliFireApiMode.NONE)
    await fp.async_validate_connectivity(timeout=30)

    print(f"Local [{fp.local_connectivity}] Cloud [{fp.cloud_connectivity}]")

    print(fp.get_user_data_as_json())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
