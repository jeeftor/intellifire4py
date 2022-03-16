[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

<a href="https://www.buymeacoffee.com/jeef" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-yellow.png" alt="Buy Me A Coffee" height="41" width="174"></a>

```
    ________________________________________
   [________________________________________]
     ||_|_||_|_|_|_|_|_|_|_|_|_|_|_|_|_|_||
     |_|_|_|  |                  |  |_|_|_|
     ||_|_||  |         )'       |  ||_|_||
     |_|_|_|  |       ),  )      |  |_|_|_|
     ||_|_||  |     ,  ) , )     |  ||_|_|| Oooo an ascii fireplace
     |_|_|_|  |    (  ( , ) ,    |  |_|_|_|
     ||_|_||  |   , ,' ) ( , )   |  ||_|_||
     |_|_|_|  | _)' , ( '   (__ _|  |_|_|_|
     ||_|_|| /_)_,)___),_)'_)__(_ \ ||_|_||
_____lc|_|_|/)______)_____)______( \|_|_|_|_____
""""/______________________________________\""""
"""[________________________________________]""""
""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""
```

- [`CHANGELOG`](https://raw.githubusercontent.com/jeeftor/intellifire4py/master/CHANGELOG)
- [`Source Code`](https://github.com/jeeftor/intellifire4py)

**Table o`Contents**

<!-- toc -->

- [Intellifire](#intellifire)
- [Local Polling](#local-polling)
    * [Status Attributes](#status-attributes)
    * [Error Codes](#error-codes)
- [Auto Discovery](#auto-discovery)
- [Fireplace Control](#fireplace-control)
        + [SSL Considerations](#ssl-considerations)
    * [Local Control](#local-control)
    * [Cloud Control](#cloud-control)
- [Control API Overview](#control-api-overview)
    * [The default fireplace](#the-default-fireplace)
    * [Power (Flame on/off)](#power-flame-onoff)
    * [Flame Height](#flame-height)
    * [Fan Speed](#fan-speed)
    * [Lights](#lights)
    * [Beep](#beep)
    * [Thermostat](#thermostat)
    * [Sleep Timer](#sleep-timer)
- [Control Exceptions](#control-exceptions)
- [Sample Code](#sample-code)

<!-- tocstop -->

# Intellifire

This is an Python Async Module for dealing with IntelliFire places. This is a 100% unofficial python module for working with the IntelliFire API for Intellifire WIFI Modules.

Intellifire is a wifi module for a variety of fireplaces produced by Hearth and Home Technologies

# Local Polling

Intellifire publishes status information on a `/post` http endpiont.  `IntellifireAsync` will poll an intellifire interface on the local network for a read-only view of the device. All that is required is the ip address.

A demonstration of how to poll a fireplace is as follows:

```python
async def main():
    fire = IntellifireAsync("192.168.1.3")
    await fire.poll()

    # Poll the fire
    print(f"{fire.data.temperature_c} c")
    print(f"{fire.data.temperature_f} f")
    print(f"{fire.data.thermostat_setpoint_c} c")
    print(f"{fire.data.thermostat_setpoint_f} f")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

```
## Status Attributes

The following attributes are available on an `IntellifireAsync` object


```python
battery: int
connection_quality: int
downtime: int
ecm_latency: int
errors: list[int]
error_codes: list[IntellifireErrorCode]
error_codes_string: str
fanspeed: int
flameheight: int
fw_ver_str: str
fw_version: str
has_fan: bool
has_light: bool
has_power_vent: bool
has_thermostat: bool
ipv4_address: str
is_hot: bool
is_on: bool
light_level: int
name: str
pilot_on: bool
prepurge: int
raw_thermostat_setpoint: int
serial: str
temperature_c: int
temperature_f: float
thermostat_on: bool
thermostat_setpoint_c: float
thermostat_setpoint_f: float
timer_on: bool
timeremaining_s: int
uptime: int

```

## Error Codes

There are a variety of methods to pull error information from the module

```python
fire.error_pilot_flame
fire.error_flame
fire.error_fan_delay
fire.error_maintenance
fire.error_disabled
fire.error_fan
fire.error_lights
fire.error_accessory
fire.error_soft_lock_out
fire.error_ecm_offline
fire.error_offline
```

Additionally you can pull an array of `IntellifireErrorCode` objects or strings with:

```python
fire.error_codes
fire.error_codes_string
```





# Auto Discovery

The IFT module will respond to the receipt of a udp packet with its ip information. You can run either a Sync or Async version of this functionaly.

```python
print("----- Find Fire Places - Sync Mode  (waiting 3 seconds)-----")
finder = UDPFireplaceFinder()
print(finder.search_fireplace(timeout=3))

print("----- Find Fire Places - Aync Mode  (waiting 3 seconds)-----")
af = AsyncUDPFireplaceFinder()
await af.search_fireplace(timeout=3)
```


# Fireplace Control

The Async Control Interface gives you the ability to directly send commands to your IFT unit. To instantiate one you will need

- `ip` - Fireplace ip on the network - *used for initial instantiation*
- `username` - Username (email) used in intellifire app - *used for login*
- `password` - Password - *used for login*

After the module connects to `iftapi.net` it will pull down a `user_id` which is globally applicable to all fireplaces on a user account and an `api_key` which is fireplace specific.


### SSL Considerations

Sometimes we live in a tough SSL world and as such you can disable SSL (https) mode for communicating with `iftapi.net` as well as disable SSL Certificate Verification. In most cases you will not need to deal with this.

```
# No SSH Inspection and use HTTP mode
ift_control = IntellifireControlAsync(
	fireplace_ip=ip,
	use_http=True,
	verify_ssl=False
)
```


## Local Control

Local control can take advantage of the units `/post` endpoint. However these commands require an **ApiKey** that must to be retreived from  `iftapi.net`.

*This is currently only implemnted in the [`IntellifireControlAsync`](intellifire4py/control_async.py#L24) control module.*

Local control is the default state but if you need to manually set it you can use:

```python
ift_control.send_mode = IntellifireSendMode.LOCAL
```


## Cloud Control

Taking advantage of the `iftapi.net` REST API - the module can send commands to the cloud in order to control a specific fireplace. In order to enable this you need to set the `.send_mode` to something like:

```python
ift_control.send_mode = IntellifireSendMode.CLOUD
```

# Control API Overview


Conceptually the API is divided into `Users` who have control of `Locations` which contain `Fireplaces`.

```
┌───────────┐
│   Users   │
└─────┬─────┘
      │
      │
┌─────▼─────┐
│ Location  │
└─────┬─────┘
      │
      │
┌─────▼─────┐
│ Fireplace │
└───────────┘
```

The IFT-API requires cookie based authentication for sending control commands via its REST API endpoint. These cookies are generated by the login method:

```python
username = os.environ['IFT_USER']
password = os.environ['IFT_PASS']

# Init and login
ift_control = IntellifireControlAsync(fireplace_ip='192.168.1.65')
await ift_control.login(username=username, password=password)
```

Once the login is complete all further control requests will use data from these cookies to authenticate and control things. Local calls will use an api_key from the cookie while cloud calls will use the entire cookie.

## The default fireplace

All commands will reference a specific `IntellifireFireplace`, however in the case that you have a single Intellifire Device installed in your user account you can just use the `.default_fireplace` property

```python
default_fireplace = ift_control.default_fireplace
print("Serial:", default_fireplace.serial)
print("APIKey:", default_fireplace.apikey)
```

## Power (Flame on/off)

The following calls will toggle the flame on or off:

```python
control_interface.flame_on(fireplace=fireplace)
control_interface.flame_off(fireplace=fireplace)
```
## Flame Height

You can control the flame height with `set_flame_height` method. Height ranges from 0 to 4:

```python
await control_interface.set_flame_height(fireplace=fireplace, height=3)
```

*Note that a zero height flame is the "lowest" flame setting supported by the module.*

## Fan Speed

Fan speed is controled via the `set_fan_speed` method. Valid ranges for `speed` 0 to 4.

```python
await control_interface.set_fan_speed(fireplace=fireplace, speed=1)
```

## Lights

You can control lights with `set_lights` method. Valid ranges for `level` are 0 to 3.


```python
await control_interface.set_lights(fireplace=fireplace, speed=1)
```

## Beep

Apparently, if the fireplace is on (flame on) you can send a beep. This also may not work.


```python
await control_interface.beep(fireplace=fireplace)
```

## Thermostat



```python
# Set to 70 and store the value internally
await ift_control.set_thermostat_f(fireplace=defualt_fireplace, temp_f=70)
# Set to 23 and store value internally
await ift_control.set_thermostat_c(fireplace=defualt_fireplace, temp_c=23)
# Turn off thermostat
await ift_control.turn_off_thermostat(fireplace=defualt_fireplace)
# Turn on thermostat and set temp to 23c as this was the last temp
await ift_control.turn_on_thermostat(fireplace=defualt_fireplace)
```

## Sleep Timer

The sleep timer range is from (`1`-`180` minutes). Interact as follows:

```python
await ift_control.set_sleep_timer(fireplace=default_fp, minutes=120)
await ift_control.turn_off_sleep_timer(fireplace=default_fp, minutes=120)
```

# Control Exceptions

- `LoginException` - problem with the login process (username/password).
- `InputRangeException` - control value is out of valid range.
- `ApiCallException` - Some sort of api exception occured.


# Sample Code

There is some sample code in [`example.py`](https://github.com/jeeftor/intellifire4py/blob/master/example.py)
