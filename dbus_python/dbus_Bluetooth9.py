#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#   &&&         dbus_Bluetooth.py        &&&
#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

# TODO : Implement tcp messaging system

# ***************************
# ***   Package imports   ***
# ---------------------------


from cust_bluezero import adapter, device
# from custom_bluezero import adapter, device
import time
import dbus
from xml.etree import ElementTree
import re
import sys
import logging
logging.basicConfig(format = '%(message)s',level = logging.DEBUG)

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
# Hub_Input1_Dongle = None
# Hub_Input2_Dongle = None
# Pi_Bt_Dongle      = None

FoundDevObjList = list()
DBusStragglers = list()
bus = dbus.SystemBus()

class DeviceAndProperties:
    def __init__(self, deviceObj, properties, props_iface):
        self.deviceObj = deviceObj
        self.properties = properties
        self.props_iface = props_iface

class HubDongle:
    def __init__(self,lock ,mac_address: str ):
        """
        @info : Initialize dongle with the given mac address.
        @param : str(mac address)
                Ex. "00:1A:7D:DA:71:13"
        """
        self.device_list    = [] # Populate with class: DeviceAndProperties.
                                 # - deviceObj
                                 # - properties
        self.usable_devices = []
        self.connected_obj = None
        self.MediaControl = self.MediaControlClass()
        self.ConnectedAlias = None
        self.device_path = None
        try:
            # Make adapter object with specified mac address.
            this_Dongle = adapter.Adapter(mac_address)
            this_Dongle.on_device_found = self.on_device_found
            self.Dongle = this_Dongle
        except:
            self.Dongle = None
            logging.debug("\nDongle with MAC:%s could not initiailze" % mac_address)
            raise DongleInitError("Dongle with MAC:%s could not initialize" % mac_address)

    def set_to_null_device_found(self):
        self.Dongle.on_device_found = self.null_device_found

    def set_to_on_device_found(self):
        self.Dongle.on_device_found = self.on_device_found

    def on_device_found(self, device: device.Device):
        """
        @info : Call back function when a device is found.
        @param : device object
        """
        pass

    def null_device_found(self, device: device.Device):
        """
        @info : Method for when device is not in use at the moment.
        """
        try:
            pass
        except:
            pass

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
        logging.debug("Powering on")
        # print(self.Dongle.powered)
        self.Dongle.powered = True

    def power_off(self):
        """
        @info : Power off.
        """
        logging.debug("Powering off")
        # print(self.Dongle.powered)
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

    def pair_and_connect(self, device_and_props):
        """
        @info : Pair and Connect to a found device.
        @param : device object
        """
        found_device = device_and_props.deviceObj
        if found_device:
            pairResultError = True
            try:
                pairResultError = found_device.Pair()
            except Exception as e:
                pairResultError = pair_exception_handler(e)
            if pairResultError:
                logging.debug("Pairing Failed.")
                return 0

            logging.debug("Device paired.")

            trustResultError = True
            try:
                trustResultError = device_and_props.props_iface.Set("org.bluez.Device1", "Trusted", True)
            except Exception as ee:
                logging.debug("%s" %ee)
                logging.debug("Failed to trust")

            connectResultError = True
            try:
                connectResultError = found_device.Connect()
            except Exception as eee:
                connectResultError = connect_exception_handler(eee)
            if connectResultError:
                logging.debug("Connecting Failed.")
                return 0

            if not connectResultError:
                self.connected_obj = found_device
                logging.debug("Device Connected")
        else:
            logging.debug("Did not get device, we\'ll get them next time.")

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
        self.usable_devices = []
        self.device_list = []
        for path, ifaces in objects.items():
            found_device = ifaces.get("org.bluez.Device1")
            if found_device is None:
                continue
            if (path.startswith(path_prefix)):
                obj = bus.get_object(BLUEZ_BUS_NAME, path)
                props_iface = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
                properties = props_iface.GetAll("org.bluez.Device1")
                device_itself = dbus.Interface(obj, "org.bluez.Device1")
                device_and_properties = DeviceAndProperties(device_itself, properties, props_iface)
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
        if len(self.usable_devices) == 0:
            logging.debug("No usable devices.")
            return False

        for i, device in enumerate(self.usable_devices, 1):
            logging.debug("%d : %s" % (i, device.properties["Name"]))

        # Get selection from user. This can be replaced with something else later.
        selection = int(input())
        if selection > i or selection < 1:
            logging.debug("Invalid Selection")
            return False
        else:
            try:
                target = self.usable_devices[selection - 1]
                self.pair_and_connect(target)
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
                logging.debug("Could not print name of this device")

        # Iterate through with a number to use so that you can select.
        # Note: Numbers start from 1 so we need to -1 from the actual input.
        for i, device in enumerate(self.usable_devices, 1):
            logging.debug("%d : %s" %(i, device.properties["Name"]))

        # Get selection from user. This can be replaced with something else later.
        selection = int(input())
        if selection > i or selection <1:
            logging.debug("Invalid Selection")
            return False
        else:
            try:
                target = self.usable_devices[selection-1]
                self.pair_and_connect(target)
            except:
                pass

    def get_Alias(self):
        try:
            connected_device = self.connected_obj
            ctrl_obj = bus.get_object(BLUEZ_BUS_NAME, connected_device.object_path)
            ctrl_props_iface = dbus.Interface(ctrl_obj, 'org.freedesktop.DBus.Properties')
            ctrl_properties = ctrl_props_iface.GetAll('org.bluez.Device1')
            self.ConnectedAlias = ctrl_properties["Alias"]
            logging.debug("Got Alias: %s" %self.ConnectedAlias)
        except:
            logging.debug("Couldn't get Alias")


    def get_media_controls(self):
        if self.connected_obj:
            # Get MediaController first.
            for i in range(2):
                time.sleep(1)
                self.getMediaControl()
                if (self.MediaControl.MediaController is not None) and (self.MediaControl.MediaPlayer is not None):
                    break

            # Get MediaTransport. (for adjusting volume)
            self.getMediaTransport()
            logging.debug("Finished fetching media controls")

    def getMediaControl(self):
        try:
            connected_device = self.connected_obj
            ctrl_obj = bus.get_object(BLUEZ_BUS_NAME, connected_device.object_path)
            ctrl_props_iface = dbus.Interface(ctrl_obj, 'org.freedesktop.DBus.Properties')
            ctrl_properties = ctrl_props_iface.GetAll('org.bluez.MediaControl1')
            self.MediaControl.MediaController = dbus.Interface(ctrl_obj, 'org.bluez.MediaControl1')
            logging.debug("Got Controller obj")
        except:
            logging.debug("No Controller obj available")
            time.sleep(0.1)
        try:
            if 'Player' in ctrl_properties:  # If there is a player, we need to go deeper.
                play_obj = bus.get_object(BLUEZ_BUS_NAME, ctrl_properties['Player'])
                play_props_iface = dbus.Interface(play_obj, 'org.freedesktop.DBus.Properties')
                play_properties = play_props_iface.GetAll('org.bluez.MediaPlayer1')
                self.MediaControl.MediaPlayer = dbus.Interface(play_obj, 'org.bluez.MediaPlayer1')
                logging.debug("Got Player obj")
        except:
            logging.debug("No Player obj available")
        finally:
            if self.MediaControl.MediaPlayer is None:
                logging.debug("No MediaPlayer was found")
    class MediaControlClass:
        def __init__(self):
            self.MediaController = None
            self.MediaPlayer     = None
            self.MediaTransporter= None


        def GetVolume(self):
            try:
                volume = self.MediaTransporter.Get('org.bluez.MediaTransport1', 'Volume')
            except:
                volume = None
            finally:
                return volume

        def VolumeUp(self):
            try:
                volume = self.MediaTransporter.Get('org.bluez.MediaTransport1', 'Volume')
                volume = volume + 10
                if volume > 127:
                    volume = 127
                self.MediaTransporter.Set('org.bluez.MediaTransport1', 'Volume', dbus.UInt16(volume))
            except:
                volume = None
            finally:
                return volume

        def VolumeDown(self):
            try:
                volume = self.MediaTransporter.Get('org.bluez.MediaTransport1', 'Volume')
                volume = volume - 10
                if volume < 0:
                    volume = 0
                self.MediaTransporter.Set('org.bluez.MediaTransport1', 'Volume', dbus.UInt16(volume))
            except:
                volume = None
            finally:
                return volume


    def getMediaTransport(self):
        """https://scribles.net/controlling-bluetooth-audio-on-raspberry-pi/"""
        obj = bus.get_object('org.bluez', "/")
        mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
        try:
            for path, ifaces in mgr.GetManagedObjects().items():
                if (self.connected_obj.object_path in path ) and \
                        ('org.bluez.MediaTransport1' in ifaces):
                    self.MediaControl.MediaTransporter = dbus.Interface(
                        bus.get_object('org.bluez', path),
                        'org.freedesktop.DBus.Properties')
                    logging.debug("Got Transporter obj")
                    continue
        except:
            logging.debug("No Transporter obj available")
        finally:
            if self.MediaControl.MediaTransporter is None:
                logging.debug("No Transporter obj was found")




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
    logging.debug("\nListing Stragglers:")
    for s in DBusStragglers:
        logging.debug("%s" %s.path)


def pair_exception_handler(error):
    """
    @info : Handles the exception to any failed pair requests.
    @param : exceptions to device.Pair()
    @note : more info here :
            https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt
    """
    if "org.bluez.Error.AlreadyExists" in str(error):    # The only acceptable error
        logging.debug("AlreadyExists")
        return None
    else:
        logging.debug("Some other pairing error")
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
        logging.debug("AlreadyConnected")
        return False
    else:
        logging.debug("Some other connecting error")
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
                logging.debug("Removed : %s" % straggler.path)
        except:
            pass


def shutdown(whiteList, dongle_1 = None, dongle_2 = None, dongle_3 = None):
    dongle_list = []
    # Make dongle list
    if dongle_1:
        dongle_list.append(dongle_1)
    if dongle_2:
        dongle_list.append(dongle_2)
    if dongle_3:
        dongle_list.append(dongle_3)


    find_dbus_stragglers()  # List DBus cache stragglers

    for dongle in dongle_list:
        # Remove stragglers except the ones that are White-Listed
        logging.debug("Clearing %s"%dongle.Dongle.alias)
        remove_stragglers(whiteList, dongle.Dongle)
        
        # Power off
        dongle.power_off()


def main():
    global Hub_Input1_Dongle, Hub_Output_Dongle, bus

    bus = dbus.SystemBus()                                              # Define global system bus to use
    bluez_obj       = bus.get_object(BLUEZ_BUS_NAME, BLUEZ_OBJ_PATH)    # Get proxy object
    agent_manager   = dbus.Interface(bluez_obj, AGENT_MANAGER)          # Get agent manager
    agent_manager.RegisterAgent(AGENT_PATH, NO_INPUT_NO_OUTPUT)         # Set agent as NoInputNoOutput mode

    # ****************
    # *** Dongle 1 ***
    # ________________
    # Initialize Input 1 Dongle

    Hub_Input1_Dongle = HubDongle(MAC_LIST[1])

    x1 = int(input("Type 1 to start scan : "))
    if x1 == 1:
        # Power on
        Hub_Input1_Dongle.power_on()

        # Discoverable on
        Hub_Input1_Dongle.discoverable_on()

        # Start scan
        Hub_Input1_Dongle.Dongle.nearby_discovery(timeout=15)
        #I think to stop it, it would be :
        #       Hub_Input1_Dongle.Dongle.stop_discovery()

    # List pairable devices.
    Hub_Input1_Dongle.find_devices_in_adapter()

    # Get media controls
    Hub_Input1_Dongle.get_media_controls()

    Hub_Input1_Dongle.MediaControl.use_media_controls()
    # Discoverable off
    Hub_Input1_Dongle.discoverable_off()

    x1 = int(input("Type 0 to exit :"))
    if x1 == 0:
        shutdown([], dongle_1= Hub_Input1_Dongle, dongle_2=Hub_Output_Dongle)
        sys.exit()

    # Disable on_device_found so that the other adapter can use it.
    Hub_Input1_Dongle.set_to_null_device_found()

    # ****************
    # *** Dongle 2 ***
    # ________________

    # Initialize Output Dongle
    Hub_Output_Dongle = HubDongle(MAC_LIST[3])

    # Power on
    Hub_Output_Dongle.power_on()

    # Discoverable on
    Hub_Output_Dongle.discoverable_on()

    # Start scan
    Hub_Output_Dongle.Dongle.nearby_discovery(timeout=15)

    # List pairable devices.
    Hub_Output_Dongle.find_devices_in_adapter()

    # Get media controls
    Hub_Output_Dongle.get_media_controls()

    x2 = input()

    # Disable on_device_found so that the other adapter can use it.
    Hub_Output_Dongle.set_to_null_device_found()

    # ***************************
    # ***  Clean up devices   ***
    # ___________________________
    shutdown([], dongle_1= Hub_Input1_Dongle, dongle_2=Hub_Output_Dongle)
    logging.debug("End of line")



if __name__ == '__main__':
    print("Here is my name: ")
    print(__name__)
    # main()