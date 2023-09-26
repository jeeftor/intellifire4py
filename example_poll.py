"""Poll fire place examples."""

import asyncio
import logging
import os

from intellifire4py.local_api import IntelliFireAPILocal


logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    """Define main function."""
    print(
        """
    Accessing IFT_IP environment variable to connect to fireplace
    """
    )
    ip = os.environ["IFT_IP"]

    api = IntelliFireAPILocal(fireplace_ip=ip)
    await api.poll(suppress_warnings=False)
    print(api.data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
