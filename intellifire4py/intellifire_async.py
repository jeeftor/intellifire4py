"""Intellifire Async local polling module."""
import logging

import aiohttp

from intellifire4py.model import IntellifirePollData

LOGGER = logging.getLogger("__name__")


class IntellifireAsync:
    """Async enabled intellifire parsing class."""

    def __init__(self, ip: str) -> None:
        """Initialize the class with an ip."""
        self.ip = ip

        self.__data: IntellifirePollData = None  # type: ignore

    async def poll(self, logging_level: int = logging.DEBUG) -> None:
        """Poll the IFT module for data."""
        async with aiohttp.ClientSession() as session:
            url = f"http://{self.ip}/poll"

            LOGGER.log(level=logging_level, msg=f"--Intellifire:: Querying {url}")

            async with session.get(url) as response:

                try:
                    if response.status == 404:
                        # Valid address - but poll endpoint not found
                        LOGGER.log(
                            level=logging_level,
                            msg=f"--Intellifire:: Error accessing {url} - 404",
                        )
                        raise ConnectionError("Fireplace Endpoint Not Found - 404")

                    json_data = await response.json(content_type=None)
                    LOGGER.log(level=logging_level, msg=f"--Intellifire:: {json_data}")

                    self.__data = IntellifirePollData(**json_data)
                except ConnectionError:
                    LOGGER.log(
                        level=logging_level,
                        msg=f"--Intellifire:: Connection Error accessing {url}",
                    )
                    raise ConnectionError("ConnectionError - host not found")

    @property
    def data(self) -> IntellifirePollData:
        """Return current intellifire data."""
        return self.__data
