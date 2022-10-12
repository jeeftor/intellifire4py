"""Example usage of the Library."""
import asyncio
import os
import time

from intellifire4py import (
    AsyncUDPFireplaceFinder,
    IntellifireControlAsync,
    IntellifireFireplace,
    UDPFireplaceFinder,
)
from intellifire4py.control_async import IntellifireSendMode
from intellifire4py.exceptions import LoginException


async def main() -> None:
    """Run main function."""

    print("----- Find Fire Places - Sync Mode  (waiting 3 seconds)-----")
    finder = UDPFireplaceFinder()
    print(finder.search_fireplace(timeout=3))

    print("----- Find Fire Places - Aync Mode  (waiting 3 seconds)-----")
    af = AsyncUDPFireplaceFinder()
    print(await af.search_fireplace(timeout=3))

    ip = af.ips[0]
    print(f"-- Found fireplace at [{ip}] --")

    """Run main function."""
    print(
        """
    Accessing IFTAPI Username and Password via Environment Variables
    - if these aren't set please do so, also
    you will see some errors probably

      export IFT_USER=<username>
      export IFT_PASS=<password>

    """
    )
    username = os.environ["IFT_USER"]
    password = os.environ["IFT_PASS"]

    print("--- Creating Fireplace Controller ---")
    ift_control = IntellifireControlAsync(
        fireplace_ip=ip, use_http=True, verify_ssl=False
    )

    try:
        try:
            print(" -- Purposefully trying a bad password!")
            await ift_control.login(username=username, password="assword")
        except LoginException:
            print(" -- Now trying again correctly.")
            try:
                await ift_control.login(username=username, password=password)
            except LoginException:
                print(
                    "-- Could not login - make sure the login vars are correct ... bye --"
                )
                exit(1)

        print("Logged in:", ift_control.is_logged_in)

        # Get location list
        locations = await ift_control.get_locations()
        location_id = locations[0]["location_id"]
        print(" -- Using location_id: ", location_id)

        username = await ift_control.get_username()
        print(" -- Accessing Username Cookie: ", username)

        # Extract a fireplace
        fireplaces = await ift_control.get_fireplaces(location_id=location_id)
        fireplace: IntellifireFireplace = fireplaces[0]
        default_fireplace = ift_control.default_fireplace

        print("Closing Session")
        await ift_control.close()
        fireplaces = await ift_control.get_fireplaces(location_id=location_id)
        username = await ift_control.get_username()
        print("username", username)

        print("Serial:", default_fireplace.serial)
        print("APIKey:", default_fireplace.apikey)

        # Send a soft reset command?
        ift_control.send_mode = IntellifireSendMode.CLOUD
        await ift_control.soft_reset(fireplace=default_fireplace)
        await ift_control.flame_on(fireplace=fireplace)

        # print('await ift_control.set_flame_height(fireplace=default_fireplace, height=4)')
        # await ift_control.set_flame_height(fireplace=default_fireplace, height=4)

        # time.sleep(10)
        # ift_control.send_mode = IntellifireSendMode.CLOUD
        # print('await ift_control.set_flame_height(fireplace=default_fireplace, height=0)')
        # await ift_control.set_flame_height(fireplace=default_fireplace, height=0)

        # sleep_time = 5
        # await ift_control.flame_on(fireplace=fireplace)
        # await ift_control.set_fan_speed(fireplace=fireplace, speed=0)
        # time.sleep(sleep_time)
        # await ift_control.set_fan_speed(fireplace=fireplace, speed=1)
        # time.sleep(sleep_time)
        # await ift_control.set_fan_speed(fireplace=fireplace, speed=2)
        # time.sleep(sleep_time)
        # await ift_control.set_fan_speed(fireplace=fireplace, speed=3)
        # await ift_control.flame_off(fireplace=fireplace)
        # exit(0)
        for control in [IntellifireSendMode.LOCAL, IntellifireSendMode.CLOUD]:
            print("Using çontrol Møde: ", control)
            ift_control.send_mode = control
            sleep_time = 5
            await ift_control.flame_off(fireplace=default_fireplace)
            time.sleep(sleep_time)
            await ift_control.flame_on(fireplace=fireplace)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=default_fireplace, height=1)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=2)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=3)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=4)
            time.sleep(sleep_time)
            # await ift_control.set_flame_height(fireplace=fireplace, height=5)
            # time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=1)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=0)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=2)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=3)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=4)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=1)
            time.sleep(sleep_time)
            await ift_control.beep(fireplace=fireplace)
            time.sleep(sleep_time)
            await ift_control.flame_off(fireplace=fireplace)
    finally:
        await ift_control.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
