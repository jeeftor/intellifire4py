# Usage

There are two main APIs in version 3.0 of IntelliFire4Py

## Control Config Values

In order to actually issue commands to the fireplace you will need to obtain a few items from the cloud portal. These can be done automatically

- `user_id` - This is a the `user_id` associated with your specific account
- `api_key` - This is a specific key associated with a specific fireplace
- `fireplace_ip` - The IP address of the fireplace on the local network

## UDP Discovery

This code is also available in `example_discovery.py`:

```python
import asyncio
from intellifire4py.udp import UDPFireplaceFinder

async def main() -> None:
    """Discovery fire places"""

    # Most likely fail discovery due to a short time out
    timeout = 1
    print(f"----- Find Fire Places - (waiting {timeout} seconds)-----")
    af = UDPFireplaceFinder()
    print(await af.search_fireplace(timeout=timeout))

    # Set a reasonalbe timeout
    print(f"----- Find Fire Places - (waiting {timeout} seconds)-----")
    af = UDPFireplaceFinder()
    print(await af.search_fireplace(timeout=timeout))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

```

## Local Polling

With only access to the ip address of the unit you can perform local polling of data using `IntelliFireAPILocal`.

```python
import asyncio
import logging
import os

from intellifire4py import IntelliFireAPILocal

logging.basicConfig(level=logging.DEBUG)

async def main() -> None:
    """Main function."""
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
```

## Cloud Credentials

In order to actually control the unit you will need to access the cloud in order to pull down some credentials. This is demonstrated in `example_cloud_info.py` however the key usage is as follows:

```python
cloud_api = IntelliFireAPICloud(use_http=True, verify_ssl=False)
await cloud_api.login_with_credentials(username=username, password=password)

# Once logged in you can pull out the api key for the default (first detected) fireplace
api_key = cloud_api.get_fireplace_api_key(cloud_api.default_fireplace)

# Extract user_id
user_id = cloud_api.get_user_id()
```

When obtained these values can then be used for local control of the fireplace

## Local Control

In order to control the fireplace you must instantiate `IntelliFireAPILocal` as follows:

```python
from intellifire4py import IntelliFireAPILocal

api = IntelliFireAPILocal(
    fireplace_ip=fireplace_ip,
    user_id=user_id,
    api_key=api_key
)

# And then you can issue commands such as:
await api.flame_on()
```
