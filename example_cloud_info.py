"""Example showing stuff found in the cloud."""
import asyncio
import logging
import os

import rich
from rich import print
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from intellifire4py import IntelliFireAPICloud


FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


def parse_env_file():
    """Parse .env file."""
    with open(".env") as f:
        for line in f:
            try:
                key, value = line.strip().split("=")
                os.environ[key] = value
            except FileNotFoundError:
                print("-- Could not find a .env file")
                pass
            except ValueError:
                pass


def get_creds() -> None:
    """Get credentials."""
    parse_env_file()
    username = os.environ.get("IFT_USER", None)
    password = os.environ.get("IFT_PASS", None)

    if username is None:
        print("Please set the env var IFT_USER with your username")
        exit(1)

    if password is None:
        print("Please set the env var IFT_PASS with your password")
        exit(1)

    return (username, password)


async def main() -> None:
    """Define main function."""
    username, password = get_creds()

    cloud_api = IntelliFireAPICloud(use_http=True, verify_ssl=False)

    await cloud_api.login(username=username, password=password)

    table = Table(title="IFT Info")
    table.add_column("auth element")
    table.add_column("value")
    table.add_row("username", username)
    table.add_row("password", "xxxxxxx")
    table.add_row("user_id", cloud_api.get_user_id())
    table.add_row(
        "api_key", cloud_api.get_fireplace_api_key(cloud_api.default_fireplace)
    )
    console = Console()
    console.print(table)

    await cloud_api.poll()
    await cloud_api.long_poll()
    await asyncio.sleep(70)
    rich.inspect(cloud_api.data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
