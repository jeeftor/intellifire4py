"""Intellifire Async local polling module."""
from json import JSONDecodeError

import aiohttp

from intellifire4py.model import IntellifirePollData

from .const import _log


class IntellifireAsync:
    """Async enabled intellifire parsing class."""

    def __init__(self, ip: str) -> None:
        """Initialize the class with an ip."""
        _log.info(f"Instantiating an IntellifireAsync with ip {ip}")
        self.ip = ip
        self.__data: IntellifirePollData = None  # type: ignore

    async def poll(self) -> None:
        """Poll the IFT module for data."""
        async with aiohttp.ClientSession() as session:
            url = f"http://{self.ip}/poll"

            _log.debug(f"--Intellifire:: Querying {url}")

            async with session.get(url) as response:

                try:
                    if response.status == 404:
                        # Valid address - but poll endpoint not found
                        _log.warning(
                            msg=f"--Intellifire:: Error accessing {url} - 404",
                        )
                        raise ConnectionError("Fireplace Endpoint Not Found - 404")
                    try:
                        json_data = await response.json(content_type=None)
                        _log.debug(msg=f"Received: {json_data}")
                    except JSONDecodeError:
                        _log.warning(f"Error decoding JSON: {response.text}")

                    self.__data = IntellifirePollData(**json_data)
                except ConnectionError:
                    _log.warning(msg=f"Connection Error accessing {url}")
                    raise ConnectionError("ConnectionError - host not found")

    @property
    def data(self) -> IntellifirePollData:
        """Return current intellifire data."""
        return self.__data
