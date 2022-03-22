#   ****************************************
#   ***   Refactored dbus_Bluetooth.py   ***
#   ****************************************
# DONE : Scan for other devices (phone, headset, etc.)  with adapter.Adapter()
# !   Implemented as  :   Hub_Input1_Dongle.nearby_discovery()
# DONE : Clear any dbus object that gets saved after a scan
#       - Ex. /org/bluez/hci2/dev_40_DE_65_18_E5_06
# DONE : Register with device.Device(adapter_addr, device_addr)
# TODO : Change agent capabilities with a function.
# TODO : Accept pairing requests with NoInputNoOutput.



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

# Capabilities
DISPLAY_ONLY         = "DisplayOnly"
DISPLAY_YES_NO       = "DisplayYesNo"
KEYBOARD_ONLY        = "KeyboardOnly"
NO_INPUT_NO_OUTPUT   = "NoInputNoOutput"
KEYBOARD_DISPLAY     = "KeyboardDisplay"

BLUEZ_BUS_NAME       = 'org.bluez'
BLUEZ_OBJ_PATH       = '/org/bluez'
AGENT_INTERFACE      = 'org.bluez.Agent1'
AGENT_PATH           = '/test/agent'
AGENT_MANAGER        = 'org.bluez.AgentManager1'

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
        Hub_Output_Dongle.on_device_found = None
        # Hub_Output_Dongle.on_device_found = on_device_found
    except:
        raise DongleInitError("Hub Output dongle did not initialize properly")

    try:
        Hub_Input1_Dongle = adapter.Adapter(MAC_LIST[2])
        # Hub_Input1_Dongle.on_device_found = null_device_found
        Hub_Input1_Dongle.on_device_found = on_device_found
    except:
        raise DongleInitError("Hub Input1 dongle did not initialize properly")

    try:
        Hub_Input2_Dongle = adapter.Adapter(MAC_LIST[1])
        Hub_Input2_Dongle.on_device_found = None
        # Hub_Input2_Dongle.on_device_found = on_device_found
    except:
        raise DongleInitError("Hub Input2 dongle did not initialize properly")

    try:
        Pi_Bt_Dongle = adapter.Adapter(MAC_LIST[3])
        Pi_Bt_Dongle.on_device_found = None
        # Pi_Bt_Dongle.on_device_found = on_device_found
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


def null_device_found(device: device.Device):
    # Do nothing.
    pass


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

    # Goes through object looking for new objects.
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


def pair_with_device(adapter_to_pair: adapter.Adapter, mac_address: str):
    try:
        device_connection = device.Device(adapter_to_pair.address, mac_address)
        device_connection.pairabletimeout = 20
        device_connection.pair()
        print("Pairing success")
    except:
        print("Pairing Failed")


def cycle_power(bt_dongle: adapter.Adapter):
    bt_dongle.powered       = False
    bt_dongle.discoverable  = False
    time.sleep(1)
    bt_dongle.powered       = True
    bt_dongle.discoverable  = True


def main():
    global FoundDevices
    global DBusStragglers

    # Initialize Dongles
    initdongles()

    # Power on
    cycle_power(Hub_Input1_Dongle)
    # Hub_Input1_Dongle.on_device_found = on_device_found

    # Change BlueZ agent to NoInputNoOutput
    bus = dbus.SystemBus()      # Get system bus object
    bluez_obj = bus.get_object(BLUEZ_BUS_NAME, BLUEZ_OBJ_PATH)    # Get proxy object
    agent_manager = dbus.Interface(bluez_obj, AGENT_MANAGER)      # Get agent manager
    agent_manager.RegisterAgent(AGENT_PATH, DISPLAY_ONLY)   # NoInputNoOutput mode

    # Start scan
    Hub_Input1_Dongle.nearby_discovery(timeout=15)

    # Look for device named Bob
    find_Bob(FoundDevices)

    print("Clearing DBus device cache")
    # Clearing DBus device cache
    find_dbus_stragglers(Hub_Input1_Dongle)

    # BOB : F4:65:A6:E5:F0:5F
    print("trying to pair with bob")
    try:
        pair_with_device(Hub_Input1_Dongle, "F4:65:A6:E5:F0:5F")
    except:
        pass


    for straggler in DBusStragglers:
        try:
            Hub_Input1_Dongle.remove_device(straggler)
        except:
            pass

    time.sleep(5)
    print("Powering off")
    # Powering off dongle
    Hub_Input1_Dongle.powered = False
    Hub_Input1_Dongle.discoverable = False


if __name__ == '__main__':
    print(__name__)
    main()


#https://mdipirro.github.io/c++/2019/09/18/bluetooth-agent-qt-part1.html