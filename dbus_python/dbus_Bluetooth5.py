#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#   &&&   Refactored dbus_Bluetooth.py   &&&
#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

# TODO : Modularize the code to be paired with other devices.
# TODO : Allow it to be paired with multiple devices with multiple dongles.

# ***************************
# ***   Package imports   ***
# ---------------------------


from bluezero import adapter, device
import time
import dbus
from xml.etree import ElementTree
import re

# *****************************
#   Define Global Variables
# -----------------------------
MAC_LIST = ["DC:A6:32:92:BF:F5",
            "00:1A:7D:DA:71:13",
            "00:1A:7D:DA:71:14",
            "00:1A:7D:DA:71:15"]
            # raspberry pi
            # MusicHub : 1
            # MusicHub : 2
            # MusicHub : 3

# ******************
#    Capabilities
# ------------------
DISPLAY_ONLY         = "DisplayOnly"
DISPLAY_YES_NO       = "DisplayYesNo"
KEYBOARD_ONLY        = "KeyboardOnly"
NO_INPUT_NO_OUTPUT   = "NoInputNoOutput"
KEYBOARD_DISPLAY     = "KeyboardDisplay"

# ********************************
#    Bus paths and object paths
# --------------------------------
BLUEZ_BUS_NAME       = 'org.bluez'
BLUEZ_OBJ_PATH       = '/org/bluez'
AGENT_INTERFACE      = 'org.bluez.Agent1'
AGENT_PATH           = '/test/agent'
AGENT_MANAGER        = 'org.bluez.AgentManager1'

# ********************
#    Dongle Objects
# --------------------
# Hub_Output_Dongle = None
Hub_Input1_Dongle = None
# Hub_Input2_Dongle = None
# Pi_Bt_Dongle      = None

FoundDevObjList = list()
DBusStragglers = list()
bus = None

class DeviceAndProperties:
    def __init__(self, deviceObj, properties):
        self.deviceObj = deviceObj
        self.properties = properties

class HubDongle:
    def __init__(self, mac_address):
        """
        @info : Initialize dongle with the given mac address.
        @param : str(mac address)
                Ex. "00:1A:7D:DA:71:13"
        """
        self.device_list    = [] # Populate with class: DeviceAndProperties.
                                 # - deviceObj
                                 # - properties
        self.usable_devices = []
        try:
            # Make adapter object with specified mac address.
            this_Dongle = adapter.Adapter(mac_address)
            this_Dongle.on_device_found = self.on_device_found
            self.Dongle = this_Dongle
        except:
            self.Dongle = None
            raise DongleInitError("Dongle with MAC:%s could not initialize" % mac_address)

    def on_device_found(self, device: device.Device):
        """
        @info : Call back function when a device is found.
        @param : device object
        """
        global FoundDevObjList
        try:
            print(device.address)
            print(device.name)
        except:
            print('Error')

    def cycle_power(self):
        """
        @info : Cycle power. Off -> On
        """
        print("cycling_power")
        self.Dongle.powered = False
        time.sleep(1)
        self.Dongle.powered = True

    def power_on(self):
        """
        @info : Power on.
        """
        print("Powering on")
        self.Dongle.powered = True

    def power_off(self):
        """
        @info : Power off.
        """
        print("Powering off")
        self.Dongle.powered = False

    def discoverable_on(self):
        """
        @info : Turn discoverable on.
        """
        self.Dongle.discoverable = True

    def discoverable_off(self):
        """
        @info : Turn discoverable off.
        """
        try:
            self.Dongle.discoverable = False
        except:
            pass    # means it was on or some other issue.

    def pair_and_connect(self, found_device):
        """
        @info : Pair and Connect to a found device.
        @param : device object
        """
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

    def find_device_in_objects(self, device_address):
        """
        @info : Find device object with the given mac address.
        @param : str(device_address)
        """
        global bus
        path_prefix = self.Dongle.path
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        for path, ifaces in objects.items():
            device_obj = ifaces.get("org.bluez.Device1")
            if device_obj is None:
                continue
            if (device_obj["Address"] == device_address and path.startswith(path_prefix)):
                obj = bus.get_object(BLUEZ_BUS_NAME, path)
                return dbus.Interface(obj, "org.bluez.Device1")
        return None

    def find_devices_in_adapter(self):
        """
        @info : Look through for found devices.
        @return : array of device interfaces
        """
        global bus
        path_prefix = self.Dongle.path
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        device_list = []
        for path, ifaces in objects.items():
            found_device = ifaces.get("org.bluez.Device1")
            if found_device is None:
                continue
            if (path.startswith(path_prefix)):
                obj = bus.get_object(BLUEZ_BUS_NAME, path)
                props_iface = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
                properties = props_iface.GetAll("org.bluez.Device1")
                device_itself = dbus.Interface(obj, "org.bluez.Device1")
                device_and_properties = DeviceAndProperties(device_itself, properties)
                self.device_list.append(device_and_properties)

        # Iterate through devices looking for device with a name attribute.
        for device in self.device_list:
            try:
                if "Name" in device.properties:
                    # Add to list if it has a "Name" attribute
                    self.usable_devices.append(device)
            except:
                print("Could not print name of this device")

        # Iterate through with a number to use so that you can select.
        # Note: Numbers start from 1 so we need to -1 from the actual input.
        for i, device in enumerate(self.usable_devices, 1):
            print("%d : %s" % (i, device.properties["Name"]))

        # Get selection from user. This can be replaced with something else later.
        selection = int(input())
        if selection > i or selection < 1:
            print("Invalid Selection")
            return False
        else:
            try:
                target = self.usable_devices[selection - 1]
                self.pair_and_connect(target.deviceObj)
            except:
                pass

    def list_usable_devices(self):
        """
        @info : Look through the device_list and make a list of the responsive objects.
                Adds usable device objects to
        @return :
        """
        # Iterate through devices looking for device with a name attribute.
        for device in self.device_list:
            try:
                if "Name" in device.properties:
                    #Add to list if it has a "Name" attribute
                    self.usable_devices.append(device)
            except:
                print("Could not print name of this device")

        # Iterate through with a number to use so that you can select.
        # Note: Numbers start from 1 so we need to -1 from the actual input.
        for i, device in enumerate(self.usable_devices, 1):
            print("%d : %s" %(i, device.properties["Name"]))

        # Get selection from user. This can be replaced with something else later.
        selection = int(input())
        if selection > i or selection <1:
            print("Invalid Selection")
            return False
        else:
            try:
                target = self.usable_devices[selection-1]
                self.pair_and_connect(target.deviceObj)
            except:
                pass


class DongleInitError(Exception):
    """@info: Exception for InitializeDongle()"""
    pass


class StragglerObj():
    def __init__(self, obj_path:str):
        self.path   = obj_path
        self.Remove = None


def get_device_mac(path):
    """
    @info : Get the device mac address
    @param : object path in string form.
    """
    pattern = r'\/org\/bluez\/hci\d\/dev[_\d\w]{18}'
    match = re.search(pattern, path)
    if match:
        return match.group(0)
    else:
        return None


def recursive_introspection(service, object_path):
    """
    @info : Recursively enters the dbus object tree to find more objects.
            Updates [DBusStragglers] with the found objects
    @param :- bus : session bus object. Ex: dbus.SystemBus()
            - service : dbus service to introspect Ex: "org.bluez"
            - object_path : the path of the top most object we want to introspect.
                            Ex: "/org/bluez"
    """
    global DBusStragglers, bus

    match_result = get_device_mac(object_path)
    if match_result is not None:
        DBusStragglers.append(StragglerObj(match_result))

    # Goes through object looking for new objects.
    obj = bus.get_object(service, object_path)
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable')
    xml_string = iface.Introspect()
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            if object_path == '/':
                object_path = ''
            new_path = '/'.join((object_path, child.attrib['name']))
            recursive_introspection(service, new_path)


def find_dbus_stragglers():
    """
    @info : finds objects within the given adapter's path to mark for removal
            Calls and lists the objects that are stuck in the cache for bluez
    @param : adapter object to introspect.
    """
    global bus
    service     = 'org.bluez'
    object_path = '/org/bluez'
    recursive_introspection(service, object_path)
    list_dbus_stragglers()


def list_dbus_stragglers():
    """
    @info : NON FUNCTIONAL. JUST VISUAL.
            Print the DBus Stragglers. 
    """
    global DBusStragglers   # List of strings
    print("\nListing Stragglers:")
    for s in DBusStragglers:
        print(s.path)


def pair_exception_handler(error):
    """
    @info : Handles the exception to any failed pair requests.
    @param : exceptions to device.Pair()
    @note : more info here :
            https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt
    """
    if "org.bluez.Error.AlreadyExists" in str(error):    # The only acceptable error
        print("AlreadyExists")
        return None
    else:
        print("Some other pairing error")
        return True


def connect_exception_handler(error):
    """
    @info : Handles the exception ot any failed connect requests.
    @param : exceptions to device.Connect()
    @note : more info here: 
            https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt
    """
    error = str(error)
    if "org.bluez.Error.AlreadyConnected" in str(error):
        print("AlreadyConnected")
        return False
    else:
        print("Some other connecting error")
        return True


def remove_stragglers(white_list, this_dongle):
    global DBusStragglers
    for straggler in DBusStragglers:
        for white_list_item in white_list:
            if white_list_item in straggler.path:
                straggler.Remove = False            # Mark it to not remove
            elif straggler.Remove is not False:     # Make sure that it hasn't been marked to not remove
                straggler.Remove = True
    for straggler in DBusStragglers:
        try:
            if straggler.Remove is not False:        # If marked for removal
                this_dongle.remove_device(straggler.path)
                print("Removed : %s" % straggler.path)
        except:
            pass


def main():
    global Hub_Input1_Dongle, bus

    bus = dbus.SystemBus()                                              # Define global system bus to use
    bluez_obj       = bus.get_object(BLUEZ_BUS_NAME, BLUEZ_OBJ_PATH)    # Get proxy object
    agent_manager   = dbus.Interface(bluez_obj, AGENT_MANAGER)          # Get agent manager
    agent_manager.RegisterAgent(AGENT_PATH, NO_INPUT_NO_OUTPUT)         # Set agent as NoInputNoOutput mode

    # Initialize Input 1 Dongle
    Hub_Input1_Dongle = HubDongle(MAC_LIST[1])

    # Power on
    Hub_Input1_Dongle.power_on()

    # Discoverable on
    Hub_Input1_Dongle.discoverable_on()

    # Start scan
    Hub_Input1_Dongle.Dongle.nearby_discovery(timeout=15)

    # List pairable devices.
    Hub_Input1_Dongle.find_devices_in_adapter()

    x = input()

    find_dbus_stragglers()      # List DBus cache stragglers

    # Hub_Input1_white_list = ["F4_65_A6_E5_F0_5F", "A4_6C_F1_53_C4_35"]
    Hub_Input1_white_list = []
    # Remove stragglers except the ones that are White-Listed
    remove_stragglers(Hub_Input1_white_list, Hub_Input1_Dongle.Dongle)

    print("End of line")

    # Power off
    Hub_Input1_Dongle.power_off()


if __name__ == '__main__':
    print(__name__)
    main()