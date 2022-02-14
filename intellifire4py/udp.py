"""Fire finder module."""
import json
import time
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Sequence

from _socket import SO_BROADCAST, SOL_SOCKET

from .const import _log


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

        _log.info(
            f"Waiting {timeout_in_seconds} seconds to see which fireplaces respond"
        )

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


class AsyncUDPFireplaceFinder:
    """UDP Broadcast based Fireplace finder."""

    def __init__(self) -> None:
        """Initialize the finder."""
        self.send_port = 3785
        self.recv_port = 55555
        self.ips: Sequence[str] = []

    async def search_fireplace(self, *, timeout: int) -> list[str]:
        """Search the network for fireplaces."""
        await self._ping()
        await self._pong(timeout_in_seconds=timeout)

        return self.ips  # type: ignore

    async def _ping(self) -> None:
        """Send a UDP request to find fireplaces."""
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto(b"IFT-search", ("255.255.255.255", self.send_port))
        _log.info("Sending Ping!")

    async def _pong(self, *, timeout_in_seconds: int) -> None:
        """Receive a Fireplace "I EXIST" result."""
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(5000)
        s.bind(("0.0.0.0", self.recv_port))

        _log.info(
            f"Waiting {timeout_in_seconds} seconds to see which fireplaces respond"
        )

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
        self.ips = list(ip_set)
