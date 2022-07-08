"""Intellifire Async local polling module."""
from json import JSONDecodeError

import aiohttp
from aiohttp import ClientConnectorError, ServerDisconnectedError

from intellifire4py.model import IntellifirePollData

from .const import _log


class IntellifireAsync:
    """Async enabled intellifire parsing class."""

    def __init__(self, ip: str) -> None:
        """Initialize the class with an ip."""
        _log.info("Instantiating an IntellifireAsync with ip [%s]", ip)
        self.ip = ip
        self.__data: IntellifirePollData = None  # type: ignore

    async def poll(self, suppress_warnings: bool = False) -> None:
        """Poll the IFT module for data."""
        async with aiohttp.ClientSession() as session:
            url = f"http://{self.ip}/poll"

            _log.debug(f"--Intellifire:: Querying {url}")
            try:
                async with session.get(url) as response:

                    try:
                        if response.status == 404:
                            # Valid address - but poll endpoint not found

                            if not suppress_warnings:
                                # During DHCP Auto discovery may want to suppress error messages
                                _log.warning(
                                    "--Intellifire:: Error accessing %s - 404", url
                                )
                            raise ConnectionError("Fireplace Endpoint Not Found - 404")
                        try:
                            json_data = await response.json(content_type=None)
                            _log.debug("Received: %s", json_data)
                        except JSONDecodeError:
                            _log.warning("Error decoding JSON: [%s]", response.text)

                        self.__data = IntellifirePollData(**json_data)
                    except ConnectionError:
                        if not suppress_warnings:
                            _log.warning("Connection Error accessing", url)
                        raise ConnectionError("ConnectionError - host not found")
            except (ServerDisconnectedError, ClientConnectorError):
                raise ConnectionError()
            except Exception as ex:
                print("Generic Exception ", type(ex))

    @property
    def data(self) -> IntellifirePollData:
        """Return current intellifire data."""
        return self.__data
