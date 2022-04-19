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
MAC_LIST = ["DC:A6:32:92:BF:F5",
            "00:1A:7D:DA:71:13",
            "00:1A:7D:DA:71:14",
            "00:1A:7D:DA:71:15"
            ]
# raspberry pi
# MusicHub : 1
# MusicHub : 2
# MusicHub : 3

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

FoundDevObjList = list()
DBusStragglers = list()
bus = None

class DongleInitError(Exception):
    pass


class FoundDeviceClass:
    def __init__(self, name, mac_address):
        self.device_name = name
        self.address = mac_address


def set_trusted(path):
    global bus
    props = dbus.Interface(bus.get_object("org.bluez", path), "org.freedesktop.DBus.Properties")
    props.Set("org.bkuez.Device1", "Trusted", True)


def init_Hub_Input1():
    global Hub_Input1_Dongle
    try:
        Hub_Input1_Dongle = adapter.Adapter(MAC_LIST[1])
        # Hub_Input1_Dongle.on_device_found = null_device_found
        Hub_Input1_Dongle.on_device_found = on_device_found
    except:
        raise DongleInitError("Hub Input1 dongle did not initialize properly")

def init_Hub_Output():
    global Hub_Output_Dongle

    try:
        Hub_Output_Dongle = adapter.Adapter(MAC_LIST[1])
        # Hub_Input1_Dongle.on_device_found = null_device_found
        Hub_Output_Dongle.on_device_found = on_device_found
    except:
        raise DongleInitError("Hub Output dongle did not initialize properly")


#  Call-back when a device is found
def on_device_found(device: device.Device):
    global FoundDevObjList
    try:
        print(device.address)
        print(device.name)
        FoundDevObjList.append(device)
    except:
        print('Error')


def find_Bob(found_list):
    for f in found_list:
        if f.name == "Bob":
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
    response = bt_dongle.powered       = False
    # bt_dongle.discoverable  = False
    time.sleep(1)
    bt_dongle.powered       = True
    bt_dongle.discoverable  = True


def power_off(bt_dongle: adapter.Adapter):
    print("Powering off")
    bt_dongle.discoverable = False
    bt_dongle.powered = False


def find_device_in_objects(adapter, device_address):
    global bus
    path_prefix = adapter.path
    manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
    objects = manager.GetManagedObjects()
    for path, ifaces in objects.items():
        device = ifaces.get("org.bluez.Device1")
        if device is None:
            continue
        if (device["Address"] == device_address and path.startswith(path_prefix)):
            obj = bus.get_object(BLUEZ_BUS_NAME, path)
            return dbus.Interface(obj, "org.bluez.Device1")
    return None


def pair_and_connect(found_device):
    if found_device:
        pairResultError = True
        try:
            pairResultError = found_device.Pair()
        except Exception as e:
            pairResultError = pair_exception_handler(e)
        if pairResultError:
            print("Pairing Failed.")
            return 0

        print("Device paired.")
        connectResultError = True
        try:
            connectResultError = found_device.Connect()
        except Exception as ee:
            connectResultError = connect_exception_handler(ee)
        if connectResultError:
            print("Connecting Failed.")
            return 0


        if not connectResultError:
            print("Device Connected")
    else:
        print("Did not get device, we\'ll get them next time.")

def pair_exception_handler(error):
    if "org.bluez.Error.AlreadyExists" in str(error):    # The only acceptable error
        print("AlreadyExists")
        return None
    else:
        print("Some other pairing error")
        return True
    #https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt


def connect_exception_handler(error):
    error = str(error)
    if "org.bluez.Error.AlreadyConnected" in str(error):
        print("AlreadyConnected")
        return False
    else:
        print("Some other connecting error")
        return True
    #https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt



def main():
    global DBusStragglers
    global bus

    # Initialize Hub Input 1
    init_Hub_Input1()

    # Power on
    cycle_power(Hub_Input1_Dongle)

    # Change BlueZ agent to NoInputNoOutput
    bus = dbus.SystemBus()      # Get system bus object
    bluez_obj = bus.get_object(BLUEZ_BUS_NAME, BLUEZ_OBJ_PATH)    # Get proxy object
    agent_manager = dbus.Interface(bluez_obj, AGENT_MANAGER)      # Get agent manager
    agent_manager.RegisterAgent(AGENT_PATH, NO_INPUT_NO_OUTPUT)   # NoInputNoOutput mode

    # Start scan
    Hub_Input1_Dongle.nearby_discovery(timeout=15)

    # Look for device named Bob
    # find_Bob(FoundDevObjList)

    # got_device = find_device_in_objects(Hub_Input1_Dongle, "F4:65:A6:E5:F0:5F")
    got_device = find_device_in_objects(Hub_Input1_Dongle, "A4:6C:F1:53:C4:35")

    pair_and_connect(got_device)

    sleep = 5
    print("sleeping for %d seconds" % sleep)
    time.sleep(sleep)

    # Clearing DBus device cache
    print("Clearing DBus device cache")
    find_dbus_stragglers(Hub_Input1_Dongle)

    for straggler in DBusStragglers:
        try:
            # # if "F4_65_A6_E5_F0_5F" in straggler:
            # if "A4_6C_F1_53_C4_35" in straggler:
            #     continue
            # else:
            #     Hub_Input1_Dongle.remove_device(straggler)

            Hub_Input1_Dongle.remove_device(straggler)

        except:
            pass

    # Power off dongle
    # power_off(Hub_Input1_Dongle)

if __name__ == '__main__':
    print(__name__)
    main()


#https://mdipirro.github.io/c++/2019/09/18/bluetooth-agent-qt-part1.html