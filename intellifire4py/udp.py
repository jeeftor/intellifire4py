"""Fire finder module."""
import json
import time
from _socket import SOL_SOCKET, SO_BROADCAST
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Sequence

from const import _log


#
# class AsyncUDPFireplaceFinder:
#     """Async version of the Fireplace finder."""
#     def __init__(self) -> None:
#         """Initialize the finder."""
#         self.send_port = 3785
#         self.recv_port = 55555
#
#     async def search_fireplace(self, *, timeout: int) -> str:
#         """Search the network for fireplaces."""
#
#         # Fire off a ping
#         await self._ping()
#
#         data = self._pong(timeout=timeout)
#         print(data)
#         fireplace_ip: str = json.loads(data)["ip"]
#         return fireplace_ip
#
#     async def _ping(self, *, timeout: int) -> None:
#         """Send a UDP request to find fireplaces."""
#         s = socket(AF_INET, SOCK_DGRAM)
#         s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#         s.sendto(b"IFT-search", ("255.255.255.255", self.send_port))
#         print("Sending Ping!")
#
#     async def _pong(self, timeout: int) -> str:  # type: ignore
#         """Awaits timeout to collect all responses from fireplaces"""
#         s = socket(AF_INET, SOCK_DGRAM)
#         s.settimeout(5000)
#         s.bind(("0.0.0.0", self.recv_port))
#
#         data, addr = s.recvfrom(1024)
#         if data:
#             # print("Got data from: ", addr)
#             return data.decode()
#
#

class UDPFireplaceFinder:
    """UDP Broadcast based Fireplace finder."""

    def __init__(self) -> None:
        """Initialize the finder."""
        self.send_port = 3785
        self.recv_port = 55555
        self.ips: Sequence[str] = []

    def search_fireplace(self, *, timeout: int) -> list[str]:
        """Search the network for fireplaces."""
        self._ping()
        data = self._pong(timeout_in_seconds=timeout)
        return data  # type: ignore

    def _ping(self) -> None:
        """Send a UDP request to find fireplaces."""
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto(b"IFT-search", ("255.255.255.255", self.send_port))
        _log.info("Sending Ping!")

    def _pong(self, *, timeout_in_seconds: int) -> [str]:  # type: ignore
        """Receive a Fireplace "I EXIST" result."""
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(5000)
        s.bind(("0.0.0.0", self.recv_port))

        _log.info(f"Waiting {timeout_in_seconds} seconds to see which fireplaces respond")

        # Reset ip's
        ip_set: set[str] = set()
        t_end = time.time() + timeout_in_seconds
        while time.time() < t_end:
            data, addr = s.recvfrom(1024)
            if data:
                # print("Got data from: ", addr)
                _log.info(f"Received Fireplace response from: {addr}")
                ip = json.loads(data.decode())["ip"]
                ip_set.add(ip)
        return list(ip_set)


def main() -> None:
    """Run main function."""
    finder = UDPFireplaceFinder()
    print(finder.search_fireplace(timeout=15))


if __name__ == "__main__":
    main()
