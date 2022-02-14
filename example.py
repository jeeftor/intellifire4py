import asyncio
import os
import time

from intellifire4py import UDPFireplaceFinder, AsyncUDPFireplaceFinder, IntellifireControlAsync, IntellifireFireplace
from intellifire4py.control import LoginException
from intellifire4py.control_async import IntellifireSendMode


async def main() -> None:
    """Run main function."""
    """Run main function."""
    print("----- Running Sync Mode -----")
    finder = UDPFireplaceFinder()
    print(finder.search_fireplace(timeout=15))

    print("----- Running Async Mode -----")
    af = AsyncUDPFireplaceFinder()
    await af.search_fireplace(timeout=15)
    print(af.ips)


    """Run main function."""
    username = os.environ["IFT_USER"]
    password = os.environ["IFT_PASS"]
    ip = os.environ["IFT_IP"]
    ift_control = IntellifireControlAsync(
        fireplace_ip=ip, use_http=True, verify_ssl=False
    )

    try:
        try:
            await ift_control.login(username=username, password="assword")
        except LoginException:
            print("Bad password!")
            await ift_control.login(username=username, password=password)

        print("Logged in:", ift_control.is_logged_in)

        # Get location list
        locations = await ift_control.get_locations()
        location_id = locations[0]["location_id"]
        print("location_id:", location_id)

        username = await ift_control.get_username()
        print("username", username)

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




        print('await ift_control.set_flame_height(fireplace=default_fireplace, height=4)')
        await ift_control.set_flame_height(fireplace=default_fireplace, height=4)

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
        exit(0)
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
