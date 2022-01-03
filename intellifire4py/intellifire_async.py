import aiohttp
import asyncio

from intellifire4py.model import IntellifirePollData


class IntellifireAsync:

    def __init__(self, ip) -> None:
        self.ip = ip

        self.__data: IntellifirePollData = None

    async def poll(self):

        async with aiohttp.ClientSession() as session:
            async with session.get("http://" + self.ip + "/poll") as response:

                try:
                    if response.status == 404:
                        # Valid address - but poll endpoint not found
                        raise ConnectionError("Fireplace Endpoint Not Found - 404")

                    self.__data = IntellifirePollData(**(await response.json()))
                except ConnectionError as e:
                    raise ConnectionError("ConnectionError - host not found")

    @property
    def data(self) -> IntellifirePollData:
        return self.__data



async def main():

    fire = IntellifireAsync("127.0.0.1")
    await fire.poll()
    # Poll the fire
    print(f"{fire.data.temperature_c} c")
    print(f"{fire.data.temperature_f} f")

    fire = IntellifireAsync("192.168.1.1")
    await fire.poll()
    # Poll the fire
    print(f"{fire.data.temperature_c} c")
    print(f"{fire.data.temperature_f} f")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

