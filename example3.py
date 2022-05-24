"""Example 3 using a better lib."""
import asyncio
import logging
import os

# import time
# from contextlib import suppress
from intellifire4py.intellifire import IntellifireAPILocal

logging.basicConfig(level=logging.DEBUG)


fireplace_ip = "192.168.1.65"
username = os.environ["IFT_USER"]
password = os.environ["IFT_PASS"]
user_id = os.environ["IFT_USER_ID"]
api_key = os.environ["IFT_API_KEY"]

# async def bg_poll(api: IntellifireAPILocal, minimum_wait_in_seconds: int = 10):
#     while True:
#         start = time.time()
#         await api.poll()
#         end = time.time()
#         print(api.data)
#         print("Poll Duration: ", (end - start))
#         await asyncio.sleep(minimum_wait_in_seconds - (end - start))


async def main() -> None:
    """Run main function."""

    api = IntellifireAPILocal(
        fireplace_ip=fireplace_ip,
        api_key=api_key,
        user_id=user_id,
    )

    print("Start BG Actions")
    await api.start_background_polling()
    await asyncio.sleep(10)

    api.log_status()
    await asyncio.sleep(1)
    api.log_status()
    await asyncio.sleep(1)
    api.log_status()
    await asyncio.sleep(1)
    api.log_status()
    await asyncio.sleep(1)
    api.log_status()
    await asyncio.sleep(1)
    api.log_status()
    await asyncio.sleep(1)
    api.log_status()
    await asyncio.sleep(1)

    # print("Pilot on")
    # await api.pilot_on()

    api.log_status()

    # # asyncio.ensure_future(bg_poll(api))  # fire and forget
    #
    # print('Do some actions 1 - Sleep', api._bg_task)
    # await asyncio.sleep(30)
    # await api.pilot_on()
    # api.stop_background_polling()
    #
    # print('Do some actions 2 - Sleep', api._bg_task)
    # await asyncio.sleep(30)
    # print('Do some actions 3 - Sleep', api._bg_task)
    print("Sleepy time")
    await asyncio.sleep(60)
    print("Done sleepy")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    # Let's also finish all running tasks:
    # pending = asyncio.Task.all_tasks()
    # loop.run_until_complete(asyncio.gather(*pending))
