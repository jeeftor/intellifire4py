import json
import requests

from intellifire4py.intellifirepolldata import IntellifirePollData


class Intellifire:

    def __init__(self, ip) -> None:
        self.ip = ip

        self.data: IntellifirePollData = None

    def poll(self):
        response = requests.get("http://" + self.ip + "/poll")
        print(response.json())
        self.data = IntellifirePollData(**response.json())


def main():
    print("Starting Intellifre Parser")

    fire = Intellifire("192.168.1.80")
    data = fire.poll()
    print(data.serial)


if __name__ == "__main__":
    main()