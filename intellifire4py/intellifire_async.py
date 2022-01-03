import aiohttp
import asyncio
import logging

from intellifire4py.model import IntellifirePollData

LOGGER = logging.getLogger("__name__")


class IntellifireAsync:

    def __init__(self, ip) -> None:
        self.ip = ip

        self.__data: IntellifirePollData = None

    async def poll(self, logging_level: int = logging.DEBUG):

        async with aiohttp.ClientSession() as session:
            url = f"http://{self.ip}/poll"

            LOGGER.log(level=logging_level, msg=f"--Intellifire:: Querying {url}")

            async with session.get(url) as response:

                try:
                    if response.status == 404:
                        # Valid address - but poll endpoint not found
                        LOGGER.log(level=logging_level, msg=f"--Intellifire:: Error accessing {url} - 404")
                        raise ConnectionError("Fireplace Endpoint Not Found - 404")

                    json_data = await response.json()
                    LOGGER.log(level=logging_level, msg=f"--Intellifire:: {json_data}")

                    self.__data = IntellifirePollData(**json_data)
                except ConnectionError as e:
                    LOGGER.log(level=logging_level, msg=f"--Intellifire:: Connection Error accessing {url}")
                    raise ConnectionError("ConnectionError - host not found")

    @property
    def data(self) -> IntellifirePollData:
        return self.__data


async def main():
    fire = IntellifireAsync("127.0.0.1")
    await fire.poll(logging_level=logging.WARN)

    # Poll the fire
    print(f"{fire.data.temperature_c} c")
    print(f"{fire.data.temperature_f} f")

    fire = IntellifireAsync("192.168.1.1")
    await fire.poll(logging_level=logging.WARN)
    # Poll the fire
    print(f"{fire.data.temperature_c} c")
    print(f"{fire.data.temperature_f} f")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
