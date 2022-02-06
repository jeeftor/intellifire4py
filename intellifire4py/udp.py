import asyncio
import time
from socket import *
import json


class UDPFireplaceFinder:
    """ "UDP Broadcast based FIREPLACE finder"""

    def __init__(self):
        self.send_port = 3785
        self.recv_port = 55555

    def search_fireplace(self) -> str:
        self._ping()
        data = self._pong()
        print(data)
        fireplace_ip = json.loads(data)["ip"]
        return fireplace_ip

    def _ping(self):
        """Sends a UDP request to find fireplaces"""
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto(b"IFT-search", ("255.255.255.255", self.send_port))
        print("Sending Ping!")

    def _pong(self):
        """Receive a Fireplace "I EXIST" resutl"""
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(5000)
        s.bind(("0.0.0.0", self.recv_port))

        data, addr = s.recvfrom(1024)
        if data:
            # print("Got data from: ", addr)
            return data.decode()


def main():
    finder = UDPFireplaceFinder()
    print(finder.search_fireplace())


if __name__ == "__main__":
    main()
