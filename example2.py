"""Example usage of the Library."""
import asyncio
import os

from intellifire4py.intellifire import IntellifireAPICloud, IntellifireAPILocal


async def main() -> None:
    """Run an entirely local instance of the api -> assuming apiKey and user_id already exist."""
    username = os.environ["IFT_USER"]
    password = os.environ["IFT_PASS"]
    user_id = os.environ["IFT_USER_ID"]
    api_key = os.environ["IFT_API_KEY"]
    fireplace_ip = "192.168.1.65"

    cloud_api = IntellifireAPICloud(use_http=True, verify_ssl=False)
    await cloud_api.login(username=username, password=password)

    cloud_user = cloud_api.get_user_id()
    cloud_api_key = cloud_api.get_fireplace_api_key()

    print("UserID = ", cloud_user)
    print("ApiKey = ", cloud_api_key)

    api = IntellifireAPILocal(
        fireplace_ip=fireplace_ip,
        api_key=api_key,
        user_id=user_id,
    )

    await api.poll()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
