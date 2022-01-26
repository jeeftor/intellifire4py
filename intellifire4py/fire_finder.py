import socket
import psutil
import aiohttp
import asyncio


class FireFinder:
    """A class to find fireplaces across IP addresses"""

    def __init__(self):
        self._ips = list(self.__get_ip_addresses(socket.AF_INET))


    def __get_ip_addresses(self, family):
        for interface, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == family:
                    yield (interface, snic.address)


    async def scan_subnets(self):

        urls = []

        for interface, address in self._ips:
            base_ip = ".".join(address.split('.')[0:3])
            for x in range(1,255):
                ip = f"{base_ip}.{x}"
                url = f"http://{ip}/poll"
                # Populate the URL List
                urls.append(url)



    async def fetch(self, session, url):
        async with session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            return await response.text()

    async def fetch_all(self, session, urls):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.fetch(session, url))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results



#
if __name__ == "__main__":

    f = FireFinder()
    f.scan_subnets()


    # ipv4s = list(get_ip_addresses(socket.AF_INET))
    # print(ipv4s)