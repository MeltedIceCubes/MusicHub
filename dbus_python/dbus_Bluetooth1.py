#   ****************************************
#   ***   Refactored dbus_Bluetooth.py   ***
#   ****************************************
# TODO : Scan for other devices (phone, headset, etc.)  with adapter.Adapter()
# TODO : Clear any dbus object that gets saved after a scan
#       - Ex. /org/bluez/hci2/dev_40_DE_65_18_E5_06
#           - This needs to be deleted
# TODO : Register with device.Device(adapter_addr, device_addr)


#**********************
#   Include packages
#**********************
from bluezero import adapter, device, tools
import time
import dbus
from xml.etree import ElementTree
import re

#*****************************
#   Define Global Variables
#*****************************
MAC_LIST = ["00:1A:7D:DA:71:13",
            "00:1A:7D:DA:71:14",
            "00:1A:7D:DA:71:15",
            "DC:A6:32:92:BF:F5"]
Hub_Output_Dongle = None
Hub_Input1_Dongle = None
Hub_Input2_Dongle = None
Pi_Bt_Dongle      = None
FoundDevices = list()
DBusStragglers = list()

class DongleInitError(Exception):
    pass


class FoundDeviceClass:
    def __init__(self, name, mac_address):
        self.device_name = name
        self.address = mac_address


def initdongles():
    global Hub_Output_Dongle
    global Hub_Input1_Dongle
    global Hub_Input2_Dongle
    global Pi_Bt_Dongle
    try:
        Hub_Output_Dongle = adapter.Adapter(MAC_LIST[0])
    except:
        raise DongleInitError("Hub Output dongle did not initialize properly")

    try:
        Hub_Input1_Dongle = adapter.Adapter(MAC_LIST[2])
    except:
        raise DongleInitError("Hub Input1 dongle did not initialize properly")

    try:
        Hub_Input2_Dongle = adapter.Adapter(MAC_LIST[1])
    except:
        raise DongleInitError("Hub Input2 dongle did not initialize properly")

    try:
        Pi_Bt_Dongle = adapter.Adapter(MAC_LIST[3])
    except:
        raise DongleInitError("Pi Bluetooth dongle did not initialize properly")


#  Call-back when a device is found
def on_device_found(device: device.Device):
    global FoundDevices

    try:
        print(device.address)
        print(device.name)
        FoundDevices.append(FoundDeviceClass(device.name, device.address))
    except:
        print('Error')


def find_Bob(found_list: FoundDeviceClass):
    for f in found_list:
        if f.device_name == "Bob":
            print("Found Bob")
        else:
            print("That wasn't Bob")


def recursive_introspection(bus, service, object_path):
    global DBusStragglers

    #print(object_path)  # Print the object path.

    match_result = match_regex(object_path)
    if match_result is not None:
        DBusStragglers.append(match_result)

    # Does something I don't really understand.
    obj = bus.get_object(service, object_path)
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable')
    xml_string = iface.Introspect()
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            if object_path == '/':
                object_path = ''
            new_path = '/'.join((object_path, child.attrib['name']))
            recursive_introspection(bus, service, new_path)


def find_dbus_stragglers(this_adapter: adapter.Adapter):
    bus         = dbus.SystemBus()
    service     = 'org.bluez'
    object_path = '/org/bluez'
    recursive_introspection(bus, service, object_path)
    list_dbus_stragglers(this_adapter)


def match_regex(string_to_match):
    pattern = r'\/org\/bluez\/hci\d\/dev[_\d\w]{18}'
    match = re.search(pattern, string_to_match)
    if match:
        return match.group(0)
    else:
        return None


def list_dbus_stragglers(this_adapter: adapter.Adapter):
    global DBusStragglers   # List of strings
    print("\nListing Stragglers:")
    for s in DBusStragglers:
        print(s)



def main():
    global FoundDevices
    global DBusStragglers
    # Initialize Dongles
    initdongles()

    # Power on
    Hub_Input1_Dongle.powered = False
    Hub_Input1_Dongle.discoverable = False
    time.sleep(1)
    Hub_Input1_Dongle.powered = True
    Hub_Input1_Dongle.discoverable = True
    print("Hub Input 1 Powered")

    #Set callback function
    Hub_Input1_Dongle.on_device_found = on_device_found

    # Start scan
    Hub_Input1_Dongle.nearby_discovery(timeout=10)

    # Look for device named Bob
    find_Bob(FoundDevices)


    print("Clearing DBus device cache")
    # Clearing DBus device cache
    find_dbus_stragglers(Hub_Input1_Dongle)
    for straggler in DBusStragglers:
        Hub_Input1_Dongle.remove_device(straggler)


    print("Powering off")
    # Powering off dongle
    Hub_Input1_Dongle.powered = False
    Hub_Input1_Dongle.discoverable = False





if __name__ == '__main__':
    print(__name__)
    main()