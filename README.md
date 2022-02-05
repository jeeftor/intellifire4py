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


# Usage

```python

# Define an intellifre instance
fire = Intellifire("192.168.1.80")

# Poll to update the internal data source
fire.poll()

# Print out all values
print(fire.data)    

```

# I just want to control things!

# Where have all the firepalces gone!

The fireplace moduels are configured to respond to a specific UDP packet and return information. As such we can discover fireplaces on the network. Currently this will only return the ip address of the first fireplace to respond... (oh well)

```
# Creates a Fireplace Finder
finder = UDPFireplaceFinder()
# Prints IP of first fireplace to respond
print(finder.search_fireplace())
```