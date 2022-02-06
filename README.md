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



# I just want to control things!

API Wise things appear to be organized into `Users` who have control of `Locations` which contain `Fireplaces`.

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

## Power (Flame on/off)

The following calls will toggle the flame on or off:

```python
control_interface.flame_on(fireplace=fireplace)
control_interface.flame_off(fireplace=fireplace)
```
## Flame Height

You can control the flame height with `set_flame_height` method. Height ranges from 0 to 4:

```python
control_interface.set_flame_height(fireplace=fireplace, height=3)
```

## Fan Speed

Fan speed is controled via the `set_fan_speed` method. Valid ranges for `speed` 0 to 4.

```python
control_interface.set_fan_speed(fireplace=fireplace, speed=1)
```

## Lights

You can control lights with `set_lights` method. Valid ranges for `level` are 0 to 3.


```python
control_interface.set_lights(fireplace=fireplace, speed=1)

```
# Beep

Apparently, if the fireplace is on (flame on) you can send a beep.


```python
control_interface.beep(fireplace=fireplace)

```

# Control Exceptions

- `LoginException` - problem with the login process (username/password).
- `InputRangeException` - control value is out of valid range.
- `ApiCallException` - Some sort of api exception occured.


# Where have all the firepalces gone!

The fireplace moduels are configured to respond to a specific UDP packet and return information. As such we can discover fireplaces on the network. Currently this will only return the ip address of the first fireplace to respond... (oh well)

```python
# Creates a Fireplace Finder
finder = UDPFireplaceFinder()
# Prints IP of first fireplace to respond
print(finder.search_fireplace())
```
