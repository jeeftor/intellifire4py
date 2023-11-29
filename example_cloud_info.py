"""Example showing stuff found in the cloud."""
# noqa F401
import asyncio
import logging
import os

from rich import print
from rich.logging import RichHandler

from intellifire4py import UnifiedFireplace
from intellifire4py.cloud_interface import IntelliFireCloudInterface
from intellifire4py.const import IntelliFireApiMode

FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


def parse_env_file() -> None:
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


def get_creds() -> tuple[str, str]:
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

    cloud_api_interface = IntelliFireCloudInterface(use_http=True, verify_ssl=False)

    user_json: str = os.getenv("USER_JSON")  # type: ignore

    cloud_api_interface.load_user_data(json_str=user_json)

    # await cloud_api_interface.login(username=username, password=password)

    user_data = cloud_api_interface.user_data
    print(user_data.model_dump_json(indent=2))

    fireplaces: UnifiedFireplace = (
        await UnifiedFireplace.build_fireplaces_from_user_data(user_data)
    )
    fireplace = fireplaces[0]

    await fireplace.set_read_mode(IntelliFireApiMode.LOCAL)
    await fireplace.set_control_mode(IntelliFireApiMode.CLOUD)

    print(fireplace.user_data_json)
    exit(0)

    # fireplace[0].debug()
    # await asyncio.sleep(10)
    # print(fireplace[0].data)
    # cloud_api_interface.build_fireplaces()

    # cloud_api.load_user_data(json_str=user_json)
    #
    # await cloud_api.login(username=username, password=password)
    #
    # await cloud_api.poll(cloud_api.fireplaces[0])
    # rich.inspect(cloud_api._data)
    # await asyncio.sleep(70)
    # await cloud_api.poll()
    # rich.inspect(cloud_api._user_data)
    #
    # table = Table(title="IFT Info")
    # table.add_column("auth element")
    # table.add_column("value")
    # table.add_row("username", username)
    # table.add_row("password", "xxxxxxx")
    # table.add_row("user_id", cloud_api.get_user_id())
    # table.add_row(
    #     "api_key", cloud_api.get_fireplace_api_key(cloud_api.default_fireplace)
    # )
    # console = Console()
    # console.print(table)

    # await cloud_api.poll()

    # await cloud_api.set_flame_height(height=1)
    # await cloud_api.poll()
    # rich.inspect(cloud_api.data)

    # await cloud_api.start_background_polling()
    #
    # await cloud_api.set_flame_height(height=1)
    # await asyncio.sleep(10)
    # await cloud_api.set_flame_height(height=2)
    # await asyncio.sleep(10)
    # rich.inspect(cloud_api.data)
    # await cloud_api.long_poll()
    print("Sleeping 70")
    await asyncio.sleep(70)
    # rich.inspect(cloud_api.data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
