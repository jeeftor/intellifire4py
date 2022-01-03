import requests

from intellifire4py.intellifirepolldata import IntellifirePollData


class Intellifire:

    def __init__(self, ip) -> None:
        self.ip = ip

        self.__data: IntellifirePollData = None

    def poll(self):
        try:
            response = requests.get("http://" + self.ip + "/poll")
            if response.status_code == 404:
                # Valid address - but poll endpoint not found
                raise ConnectionError("Fireplace Endpoint Not Found - 404")

            # print(response.json())
            self.__data = IntellifirePollData(**response.json())
        except ConnectionError as e:
            raise ConnectionError("ConnectionError - host not found")

    @property
    def data(self) -> IntellifirePollData:
        return self.__data


def main():
    print("Starting Intellifre Parser")
    fire = Intellifire("192.168.1.80")
    # Poll the fire
    fire.poll()
    print(f"{fire.data.temperature_c} c")
    print(f"{fire.data.temperature_f} f")


if __name__ == "__main__":
    main()
