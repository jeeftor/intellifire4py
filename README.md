<img src="http://raw.githubusercontent.com/home-assistant/brands/master/core_integrations/intellifire/icon.png" height=100 >


- [`CHANGELOG`](https://raw.githubusercontent.com/jeeftor/intellifire4py/master/CHANGELOG)
- [`Source Code`](https://github.com/jeeftor/intellifire4py)

# Intellifire (New and Improved)

This is a 100% unofficial python module for working with the IntelliFire API for Intellifire WIFI Modules.



Intellifire is a wifi module for a variety of fireplaces. It has both ios/android apps - but they dont like to publish the api.

From my research I've identified 4 endpoints:

`/poll`
`/get_serial`
`/get_challenge`
`/post`

This module will parse data from botht he `/get_serial` and `/poll` endpoints and parse the resultatn JSON into something readable.

If anybody knows more about OAuth and wants to help me reverse engineer the control endpoints I'd love the help!

Hit me up on github: https://github.com/jeeftor


# Local Polling

Both `Intellifire` and `IntellifireAsync` classes will poll an intellifire interface on the local network for a read-only view of the device. All that is required is the ip address. If you need to discover that see further on in this document.

## Sync 

This is not fully developed and you shouldn't really use it - if you DO want to use it - 

```python
# Define an intellifre instance
fire = Intellifire("192.168.1.80")

# Poll to update the internal data source
fire.poll()

# Print out all values
print(fire.data)    
```

## Async

```python
async def main():
    fire = IntellifireAsync("127.0.0.1")
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



# Fireplace Control

The Async Control Interface gives you the ability to directly send commands to your IFT unit. To instantiate one you will need 

- `ip` - Fireplace ip on the network - *used for initial instantiation*
- `username` - Username (email) used in intellifire app - *used for login*
- `password` - Password - *used for login*

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


# Local Control

Local control can take advantage of the units `/post` endpoint. However these commands require an **ApiKey** that must to be retreived from  `iftapi.net`. 

*This is currently only implemnted in the [`IntellifireControlAsync`](intellifire4py/control_async.py#L24) control module.*

Local control is the default state but if you need to manually set it you can use:

```python
ift_control.send_mode = IntellifireSendMode.LOCAL
```


# Cloud Control

Taking advantage of the `iftapi.net` REST API - the module can send commands to the cloud in order to control a specific fireplace. In order to enable this you need to set the `.send_mode` to something like:

```python
ift_control.send_mode = IntellifireSendMode.CLOUD
```

# API Overview


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
control_interface = IntellifireControl(fireplace_ip='192.168.1.65')
control_interface.login(username=username, password=password)
```

Once the login is complete all further control requests will use the cookies to authenticate and control things.

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

# Beep

Apparently, if the fireplace is on (flame on) you can send a beep.


```python
await control_interface.beep(fireplace=fireplace)
```

# Thermostat



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

# Sleep Timer

The sleep timer range is from (`1`-`180` minutes). Interact as follows:

```python
await ift_control.set_sleep_timer(fireplace=default_fp, minutes=120)
await ift_control.turn_off_sleep_timer(fireplace=default_fp, minutes=120)
```

# Control Exceptions

- `LoginException` - problem with the login process (username/password).
- `InputRangeException` - control value is out of valid range.
- `ApiCallException` - Some sort of api exception occured.


# Where have all the firepalces gone!

The fireplace moduels are configured to respond to a specific UDP packet and return information. As such we can discover fireplaces on the network. Currently this will only return the ip address of the first fireplace to respond... (oh well). 

```python
# Creates a Fireplace Finder
finder = UDPFireplaceFinder()
# Prints IP of first fireplace to respond
print(finder.search_fireplace())
```

*TODO: Listen for a set time and return a list of all fireplaces that respond.*


# Sample Code


Here is some sample code for how you can play with the control library. This was removed from the lib itself in release `0.9.8`

```python
async def main() -> None:
    """Run main function."""
    username = os.environ["IFT_USER"]
    password = os.environ["IFT_PASS"]
    ip = os.environ["IFT_IP"]
    ift_control = IntellifireControlAsync(
        fireplace_ip=ip, use_http=True, verify_ssl=False
    )

    try:
        try:
            await ift_control.login(username=username, password="assword")
        except LoginException:
            print("Bad password!")
            await ift_control.login(username=username, password=password)

        print("Logged in:", ift_control.is_logged_in)

        # Get location list
        locations = await ift_control.get_locations()
        location_id = locations[0]["location_id"]
        print("location_id:", location_id)

        username = await ift_control.get_username()
        print("username", username)

        # Extract a fireplace
        fireplaces = await ift_control.get_fireplaces(location_id=location_id)
        fireplace: IntellifireFireplace = fireplaces[0]
        default_fireplace = ift_control.default_fireplace

        print("Closing Session")
        await ift_control.close()
        fireplaces = await ift_control.get_fireplaces(location_id=location_id)
        username = await ift_control.get_username()
        print("username", username)

        print("Serial:", default_fireplace.serial)
        print("APIKey:", default_fireplace.apikey)




        print('await ift_control.set_flame_height(fireplace=default_fireplace, height=4)')
        await ift_control.set_flame_height(fireplace=default_fireplace, height=4)

        time.sleep(10)
        ift_control.send_mode = IntellifireSendMode.CLOUD
        print('await ift_control.set_flame_height(fireplace=default_fireplace, height=0)')
        await ift_control.set_flame_height(fireplace=default_fireplace, height=0)



        sleep_time = 5
        await ift_control.flame_on(fireplace=fireplace)
        await ift_control.set_fan_speed(fireplace=fireplace, speed=0)
        time.sleep(sleep_time)
        await ift_control.set_fan_speed(fireplace=fireplace, speed=1)
        time.sleep(sleep_time)
        await ift_control.set_fan_speed(fireplace=fireplace, speed=2)
        time.sleep(sleep_time)
        await ift_control.set_fan_speed(fireplace=fireplace, speed=3)
        await ift_control.flame_off(fireplace=fireplace)
        for control in [IntellifireSendMode.LOCAL, IntellifireSendMode.CLOUD]:
            print("Using çontrol Møde: ", control)
            ift_control.send_mode = control
            sleep_time = 5
            await ift_control.flame_off(fireplace=default_fireplace)
            time.sleep(sleep_time)
            await ift_control.flame_on(fireplace=fireplace)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=default_fireplace, height=1)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=2)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=3)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=4)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=5)
            time.sleep(sleep_time)
            await ift_control.set_flame_height(fireplace=fireplace, height=1)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=0)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=2)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=3)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=4)
            time.sleep(sleep_time)
            await ift_control.set_fan_speed(fireplace=fireplace, speed=1)
            time.sleep(sleep_time)
            await ift_control.beep(fireplace=fireplace)
            time.sleep(sleep_time)
            await ift_control.flame_off(fireplace=fireplace)
    finally:
        await ift_control.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

```