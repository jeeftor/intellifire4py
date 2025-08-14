"""Example usage of the Library."""

import asyncio
import logging

from intellifire4py.udp import UDPFireplaceFinder


logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    """Run main function."""
    timeout = 1
    print(f"----- Find Fire Places - (waiting {timeout} seconds)-----")
    af = UDPFireplaceFinder()
    print(await af.search_fireplace(timeout=timeout))

    timeout = 12
    print(f"----- Find Fire Places - (waiting {timeout} seconds)-----")
    af = UDPFireplaceFinder()
    print(await af.search_fireplace(timeout=timeout))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
