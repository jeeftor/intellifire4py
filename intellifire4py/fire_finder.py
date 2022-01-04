#
# import socket
# import psutil
#
# from socket import getaddrinfo, AF_INET, gethostname
#
# for ip in getaddrinfo(host=gethostname(), port=None, family=AF_INET):
#     print(ip)
#     # print(ip[4][0])
#
#
# class FireFinder:
#     """A class to find fireplaces across IP addresses"""
#
#     def __init__(self):
#         self._ips = self.__get_ip_addresses()
#
#
#     def __get_ip_addresses(family):
#         for interface, snics in psutil.net_if_addrs().items():
#             for snic in snics:
#                 if snic.family == family:
#                     yield (interface, snic.address)
#
#
#     def _scan_subnet(self, addre):
#
# if __name__ == "__main__":
#
#     # ipv4s = list(get_ip_addresses(socket.AF_INET))
#     # print(ipv4s)