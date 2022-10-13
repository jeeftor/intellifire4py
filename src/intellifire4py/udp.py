"""Asyncio Based UDP Discovery."""
import asyncio
import json
import socket
from typing import Any
from typing import Union

from .const import _log


class IFTDiscoveryReaderProtocol(asyncio.DatagramProtocol):
    """UPD Reader protocol for IFT Discovery.

    When testing this you can fire off a data packet similer to this with socat to stimulate the response
    echo -n '{"mac":"58:8E:81:92:52:7B","bssid":"B6:B9:8A:62:3C:E9","channel":1,"ip":"192.168.1.125","ssid":"chomperExtreme","rssi":-40,"remote_terminal_port":2000,"time":1665662949795,"version":"BBBBBBB-SOMECODE-0.0.0.1, 2019-10-23T20:22:36Z, ZentriOS-W-3.6.3.0","uuid":"36413041000000004D0026001251373036363735"}' | socat - UDP-DATAGRAM:255.255.255.255:55555,broadcast
    """

    def __init__(self, timeout: int, ip_set: set[str]) -> None:
        """Initialize the discovery reader protocol."""
        self.timeout = timeout
        self.ip_set = ip_set

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Protocol method for connection made."""
        self.transport = transport
        _log.debug("UDP Discovery Listen - Socket connection created")

    def datagram_received(self, data: bytes, addr: tuple[Union[str, Any], int]) -> None:
        """Process datagram data."""
        message = data.decode()
        _log.debug(f"Received {message!r} from {addr}")
        self.process_message(message)

    def connection_lost(self, exc):  # type: ignore
        """Warn the connection closed."""
        _log.debug("UDP Discovery Listen - Closed after %s seconds", self.timeout)

    def process_message(self, data: Any) -> None:
        """Process incoming data."""
        ip = json.loads(data)["ip"]
        _log.debug("UDP Discovery Listen - Received data: %s", data)
        self.ip_set.add(ip)


class IFTDiscoverySenderProtocol(asyncio.DatagramProtocol):
    """Protocol for UDP Discovery message sending."""

    def __init__(self, message, on_con_lost) -> None:  # type: ignore
        """Initialize the protocol."""
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport) -> None:  # type: ignore
        """Configure socket and send message on connection."""
        self.transport = transport
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.transport.sendto(self.message.encode(), ("255.255.255.255", 3785))  # type: ignore

    def datagram_received(self, data, addr):  # type: ignore
        """Print out data."""
        _log.info("UDP Discovery Send - Sent discovery message [%s]", data.decode())
        self.transport.close()  # type: ignore

    def error_received(self, exc):  # type: ignore
        """Display error."""
        _log.warning("UDP Discovery Send - Error received:", exc)

    def connection_lost(self, exc):  # type: ignore
        """Close connection."""
        if not self.on_con_lost:
            self.on_con_lost.set_result(True)


class UDPFireplaceFinder:
    """Asyncio based IFT Discovery Class."""

    def __init__(self, timeout_in_seconds: int = 12) -> None:
        """Initialize class."""
        self.send_port = 3785
        self.recv_port = 55555
        self.ip_set: set[str] = set()
        self.loop = asyncio.get_running_loop()
        self.timeout = timeout_in_seconds

    @property
    def ips(self) -> list[str]:
        """Return ip set as a list."""
        return list(self.ip_set)

    async def send_discovery_packet(self) -> None:
        """Send out the UDP Discovery packet."""
        on_con_lost = self.loop.create_future()
        message = "IFT-search"
        _log.debug("UDP Discovery Send - Attempting to send discovery packet")
        transport, protocol = await self.loop.create_datagram_endpoint(
            lambda: IFTDiscoverySenderProtocol(message, on_con_lost),
            local_addr=("0.0.0.0", 3785),  # noqa: S104
        )
        try:
            await asyncio.wait_for(on_con_lost, timeout=self.timeout)
            _log.debug("UDP Discovery Send - Discovery packet sent")
        except (asyncio.TimeoutError, asyncio.CancelledError):
            _log.debug("UDP Discovery Send - Discovery packet could not send")
        finally:
            transport.close()

    async def start_discovery_reader(self) -> None:
        """Start the discovery reader."""
        transport, protocol = await self.loop.create_datagram_endpoint(
            lambda: IFTDiscoveryReaderProtocol(
                timeout=self.timeout, ip_set=self.ip_set
            ),
            local_addr=("0.0.0.0", self.recv_port),  # noqa: S104
        )
        try:
            await asyncio.sleep(self.timeout)
        finally:
            transport.close()

    async def search_fireplace(self, *, timeout: int) -> list[str]:
        """Search the network for fireplaces."""
        self.timeout = timeout

        await asyncio.gather(
            self.send_discovery_packet(), self.start_discovery_reader()
        )
        return self.ips
