import os
import time
import requests

# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# import http.client as http_client
#
# http_client.HTTPConnection.debuglevel = 1
from intellifire4py.const import IntellifireCommand, _log
from intellifire4py.model import IntellifireFireplace, IntellifireLocations, IntellifireFireplaces


class ApiCallException(Exception):
    """Error wiht the API call"""


class InputRangeException(Exception):
    """Input out of boudns"""

    def __init__(self, field: str, min: int, max: int):
        self.message = f"{field} is out of bounds: valid values [{min}:{max}]"
        super().__init__(self.message)


class LoginException(Exception):
    pass


class IntellifireControl:
    """Hacked together control API for intellifire modules"""

    def __init__(self, fireplace_ip: str):
        self._cookie = None
        self.is_logged_in = False
        self._ip = fireplace_ip
        pass

    def login(self, *, username, password):
        """Logs into iftapi.net in order to request cookies"""
        data = f'username={username}&password={password}'
        p = requests.post('http://iftapi.net/a//login', data=data.encode())  # , headers=headers)
        self._cookie = p.cookies
        self.is_logged_in = True

    def _login_check(self):
        if not self.is_logged_in:
            raise LoginException("Not Logged In")

    def get_username(self):
        """Api call to iftapi.net to extract the username based on cookie information"""
        self._login_check()

        url = 'http://iftapi.net/a/getusername'
        p = requests.get(url=url, cookies=self._cookie)
        print(p.text)

    def get_locations(self):
        """Enumerates configured locations that a user has access to. 'location_id' can be used to discovery fireplaces
        and associated serial numbers + api keys at a give location. """
        self._login_check()
        p = requests.get(url='http://iftapi.net/a/enumlocations', cookies=self._cookie)
        return p.json()['locations']

    def get_fireplaces(self, *, location_id: str) -> [IntellifireFireplace]:
        """Gets fireplaces at a location with associated API keys!!!"""
        self._login_check()
        p = requests.get(url=f'http://iftapi.net/a/enumfireplaces?location_id={location_id}', cookies=self._cookie)
        return IntellifireFireplaces(**p.json()).fireplaces

    def get_challenge(self):
        return requests.get(f"http://{self._ip}/get_challenge").text

    def _send_cloud_command(self, command: IntellifireCommand, value: int, serial: str):
        """Sends a cloud based control command"""
        self._login_check()
        data = f"{command.value['value']}={value}"
        r = requests.post(f'http://iftapi.net/a/{serial}//apppost', data=data.encode(), cookies=self._cookie)
        if r.status_code != 204:
            raise ApiCallException("Error with API call")

    def send_command(self, *, fireplace: IntellifireFireplace, command: IntellifireCommand, value: int):
        """Sends a command to a given firepalce"""

        # Validate the range on input
        min_value: int = command.value["min"] # type: ignore
        max_value: int = command.value["max"] # type: ignore
        if value > max_value or value < min_value:
            raise InputRangeException(field=command.value["value"], min=min_value, max=max_value) # type: ignore
        self._send_cloud_command(command=command, value=value, serial=fireplace.serial)
        _log.info(f"Sending Intellifire command: [{command.value}={value}]")

    def _send_local_command(self, command: int):
        """Not yet implemented"""
        pass

    def beep(self, *, fireplace: IntellifireFireplace):
        self.send_command(fireplace=fireplace, command=IntellifireCommand.BEEP, value=1)

    def flame_on(self, *, fireplace: IntellifireFireplace):
        self.send_command(fireplace=fireplace, command=IntellifireCommand.POWER, value=1)

    def flame_off(self, *, fireplace: IntellifireFireplace):
        self.send_command(fireplace=fireplace, command=IntellifireCommand.POWER, value=0)

    def set_light(self, *, fireplace: IntellifireFireplace, level: int):
        self.send_command(fireplace=fireplace, command=IntellifireCommand.LIGHT, value=level)

    def set_flame_height(self, *, fireplace: IntellifireFireplace, height: int):
        self.send_command(fireplace=fireplace, command=IntellifireCommand.FLAME_HEIGHT, value=height)

    def set_fan_speed(self, *, fireplace: IntellifireFireplace, speed: int):
        self.send_command(fireplace=fireplace, command=IntellifireCommand.FAN_SPEED, value=speed)

    def fan_off(self, *, fireplace: IntellifireFireplace):
        self.send_command(fireplace=fireplace, command=IntellifireCommand.FAN_SPEED, value=0)

    @property
    def user(self):
        return self._cookie.get("user")

    @property
    def auth_cookie(self):
        return self._cookie.get("auth_cookie")

    @property
    def web_client_id(self):
        return self._cookie.get("web_client_id")


def main():
    username = os.environ['IFT_USER']
    password = os.environ['IFT_PASS']

    # Init and login
    control_interface = IntellifireControl('192.168.1.65')
    control_interface.login(username=username, password=password)

    # Get location list
    locations = control_interface.get_locations()
    location_id = locations[0]['location_id']

    # Extract a fireplace
    fireplace: IntellifireFireplace = control_interface.get_fireplaces(location_id=location_id)[0]

    sleep_time = 5
    control_interface.flame_off(fireplace=fireplace)
    time.sleep(sleep_time)
    control_interface.flame_on(fireplace=fireplace)
    # time.sleep(sleep_time)
    # control_interface.set_flame_height(fireplace=fireplace, height=1)
    # time.sleep(sleep_time)
    # control_interface.set_flame_height(fireplace=fireplace, height=2)
    # time.sleep(sleep_time)
    # control_interface.set_flame_height(fireplace=fireplace, height=3)
    # time.sleep(sleep_time)
    # control_interface.set_flame_height(fireplace=fireplace, height=4)
    # time.sleep(sleep_time)
    # control_interface.set_flame_height(fireplace=fireplace, height=5)
    # time.sleep(sleep_time)
    # control_interface.set_flame_height(fireplace=fireplace, height=1)
    # time.sleep(sleep_time)
    # control_interface.set_fan_speed(fireplace=fireplace, speed=0)
    # time.sleep(sleep_time)
    # control_interface.set_fan_speed(fireplace=fireplace, speed=2)
    # time.sleep(sleep_time)
    # control_interface.set_fan_speed(fireplace=fireplace, speed=3)
    # time.sleep(sleep_time)
    # control_interface.set_fan_speed(fireplace=fireplace, speed=4)
    time.sleep(sleep_time)
    # control_interface.set_fan_speed(fireplace=fireplace, speed=1)
    control_interface.beep(fireplace=fireplace)
    time.sleep(sleep_time)
    control_interface.flame_off(fireplace=fireplace)

    # api_key = fireplace.apikey
    # serial = fireplace.serial
    # challenge = control_interface.get_challenge()

    # print("apikey", api_key)
    # print("serial", serial)


if __name__ == "__main__":
    main()
