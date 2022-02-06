"""Sync intellifire module."""
import requests

from intellifire4py.model import IntellifirePollData


class Intellifire:
    """Synchronous intellifire poller."""

    def __init__(self, ip: str) -> None:
        """Initialize the class."""
        self.ip = ip

        self.__data: IntellifirePollData = None  # type: ignore

    def poll(self) -> None:
        """Poll the device for data."""
        try:
            response = requests.get("http://" + self.ip + "/poll")
            if response.status_code == 404:
                # Valid address - but poll endpoint not found
                raise ConnectionError("Fireplace Endpoint Not Found - 404")

            print(response.json())
            self.__data = IntellifirePollData(**response.json())
        except ConnectionError:
            raise ConnectionError("ConnectionError - host not found")

    @property
    def data(self) -> IntellifirePollData:
        """Return Intellifire data."""
        return self.__data


def main() -> None:
    """Run main function."""
    print("Starting Intellifre Parser")
    fire = Intellifire("192.168.1.65")
    # Poll the fire
    fire.poll()
    print(f"{fire.data.temperature_c} c")
    print(f"{fire.data.temperature_f} f")


if __name__ == "__main__":
    main()
