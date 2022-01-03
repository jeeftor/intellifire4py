import json
import requests

from intellifire4py.intellifirepolldata import IntellifirePollData

class AsyncIntellifire:
    def __init__(self, ip) -> None:
        self.ip = ip

        self.__data: IntellifirePollData = None



class Intellifire:

    def __init__(self, ip) -> None:
        self.ip = ip

        self.__data: IntellifirePollData = None

    def poll(self):
        response = requests.get("http://" + self.ip + "/poll")
        print(response.json())
        self.__data = IntellifirePollData(**response.json())

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
