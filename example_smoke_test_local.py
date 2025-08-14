"""Example usage of the Library."""

import asyncio
import logging
import os

from rich import print
from rich.logging import RichHandler
from intellifire4py.local_api import IntelliFireAPILocal

from intellifire4py.udp import UDPFireplaceFinder


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
                print("Writing key", key)
                os.environ[key] = value
            except FileNotFoundError:
                print("-- Could not find a .env file")
                pass
            except ValueError:
                pass


async def main() -> None:
    """Run main function."""
    parse_env_file()
    fireplace_ip = os.getenv("IFT_IP", None)
    user_id = os.environ["IFT_USER_ID"]
    api_key = os.environ["IFT_API_KEY"]

    if fireplace_ip is None:
        print("Env variable IFT_IP was not set - will try to search for fireplace")
        af = UDPFireplaceFinder()
        ips = await af.search_fireplace(timeout=1)
        if len(ips) > 1:
            print("IP detected")
            fireplace_ip = ips[0]
        else:
            print(
                "Could not detect a fireplace - please set IFT_IP environment variable and run again"
            )
            exit(1)

    print("Creating a local fireplace instance")
    api = IntelliFireAPILocal(
        fireplace_ip=fireplace_ip, user_id=user_id, api_key=api_key
    )

    print("Starting a background polling task")
    await api.start_background_polling(minimum_wait_in_seconds=5)
    print("sleeping 15 seconds")

    await api.flame_on()

    await asyncio.sleep(5)
    await api.poll()
    # await asyncio.sleep(3)
    # assert api.data.is_on  # noqa: S101
    # await api.poll()
    # await asyncio.sleep(3)
    # await api.set_flame_height(height=0)
    # await api.poll()
    # await asyncio.sleep(3)
    # await api.set_flame_height(height=1)
    # await api.poll()
    # await asyncio.sleep(3)
    # await api.set_flame_height(height=2)
    # await api.poll()
    # await asyncio.sleep(3)
    # await api.set_flame_height(height=3)
    # await api.poll()
    # await asyncio.sleep(3)
    # await api.set_flame_height(height=4)
    # await api.poll()
    # await asyncio.sleep(3)
    # await api.set_flame_height(height=0)
    # await asyncio.sleep(3)
    # await api.flame_off()
    # await api.poll()
    # await asyncio.sleep(300)
    # print("SHUTTING DOWN")


# print(f"-- Found fireplace at [{ip}] --")
#
# """Run main function."""
# print(
#     """
# Accessing IFTAPI Username and Password via Environment Variables
# - if these aren't set please do so, also
# you will see some errors probably
#
#   export IFT_USER=<username>
#   export IFT_PASS=<password>
#
# """
# )
# username = os.environ["IFT_USER"]
# password = os.environ["IFT_PASS"]
#
# print("--- Creating Fireplace Controller ---")
# ift_control = IntellifireControlAsync(
#     fireplace_ip=ip, use_http=True, verify_ssl=False
# )
#
# try:
#     try:
#         print(" -- Purposefully trying a bad password!")
#         await ift_control.login(username=username, password="assword")
#     except LoginError:
#         print(" -- Now trying again correctly.")
#         try:
#             await ift_control.login(username=username, password=password)
#         except LoginError:
#             print(
#                 "-- Could not login - make sure the login vars are correct ... bye --"
#             )
#             exit(1)
#
#     print("Logged in:", ift_control.is_logged_in)
#
#     # Get location list
#     locations = await ift_control.get_locations()
#     location_id = locations[0]["location_id"]
#     print(" -- Using location_id: ", location_id)
#
#     username = await ift_control.get_username()
#     print(" -- Accessing Username Cookie: ", username)
#
#     # Extract a fireplace
#     fireplaces = await ift_control.get_fireplaces(location_id=location_id)
#     fireplace: IntellifireFireplace = fireplaces[0]
#     default_fireplace = ift_control.default_fireplace
#
#     print("Closing Session")
#     await ift_control.close()
#     fireplaces = await ift_control.get_fireplaces(location_id=location_id)
#     username = await ift_control.get_username()
#     print("username", username)
#
#     print("Serial:", default_fireplace.serial)
#     print("APIKey:", default_fireplace.apikey)
#
#     # Send a soft reset command?
#     ift_control.send_mode = IntellifireSendMode.CLOUD
#     await ift_control.soft_reset(fireplace=default_fireplace)
#     await ift_control.flame_on(fireplace=fireplace)
#
#     # print('await ift_control.set_flame_height(fireplace=default_fireplace, height=4)')
#     # await ift_control.set_flame_height(fireplace=default_fireplace, height=4)
#
#     # time.sleep(10)
#     # ift_control.send_mode = IntellifireSendMode.CLOUD
#     # print('await ift_control.set_flame_height(fireplace=default_fireplace, height=0)')
#     # await ift_control.set_flame_height(fireplace=default_fireplace, height=0)
#
#     # sleep_time = 5
#     # await ift_control.flame_on(fireplace=fireplace)
#     # await ift_control.set_fan_speed(fireplace=fireplace, speed=0)
#     # time.sleep(sleep_time)
#     # await ift_control.set_fan_speed(fireplace=fireplace, speed=1)
#     # time.sleep(sleep_time)
#     # await ift_control.set_fan_speed(fireplace=fireplace, speed=2)
#     # time.sleep(sleep_time)
#     # await ift_control.set_fan_speed(fireplace=fireplace, speed=3)
#     # await ift_control.flame_off(fireplace=fireplace)
#     # exit(0)
#     for control in [IntellifireSendMode.LOCAL, IntellifireSendMode.CLOUD]:
#         print("Using çontrol Møde: ", control)
#         ift_control.send_mode = control
#         sleep_time = 5
#         await ift_control.flame_off(fireplace=default_fireplace)
#         time.sleep(sleep_time)
#         await ift_control.flame_on(fireplace=fireplace)
#         time.sleep(sleep_time)
#         await ift_control.set_flame_height(fireplace=default_fireplace, height=1)
#         time.sleep(sleep_time)
#         await ift_control.set_flame_height(fireplace=fireplace, height=2)
#         time.sleep(sleep_time)
#         await ift_control.set_flame_height(fireplace=fireplace, height=3)
#         time.sleep(sleep_time)
#         await ift_control.set_flame_height(fireplace=fireplace, height=4)
#         time.sleep(sleep_time)
#         # await ift_control.set_flame_height(fireplace=fireplace, height=5)
#         # time.sleep(sleep_time)
#         await ift_control.set_flame_height(fireplace=fireplace, height=1)
#         time.sleep(sleep_time)
#         await ift_control.set_fan_speed(fireplace=fireplace, speed=0)
#         time.sleep(sleep_time)
#         await ift_control.set_fan_speed(fireplace=fireplace, speed=2)
#         time.sleep(sleep_time)
#         await ift_control.set_fan_speed(fireplace=fireplace, speed=3)
#         time.sleep(sleep_time)
#         await ift_control.set_fan_speed(fireplace=fireplace, speed=4)
#         time.sleep(sleep_time)
#         await ift_control.set_fan_speed(fireplace=fireplace, speed=1)
#         time.sleep(sleep_time)
#         await ift_control.beep(fireplace=fireplace)
#         time.sleep(sleep_time)
#         await ift_control.flame_off(fireplace=fireplace)
# finally:
#     await ift_control.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
