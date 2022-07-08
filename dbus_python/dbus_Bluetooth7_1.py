#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#   &&&   Refactored dbus_Bluetooth.py   &&&
#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

# TODO : Multithread the program

# ***************************
# ***   Package imports   ***
# ---------------------------


from bluezero import adapter, device
import time
import dbus
from xml.etree import ElementTree
import re
import sys

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
DISPLAY_ONLY = "DisplayOnly"
DISPLAY_YES_NO = "DisplayYesNo"
KEYBOARD_ONLY = "KeyboardOnly"
NO_INPUT_NO_OUTPUT = "NoInputNoOutput"
KEYBOARD_DISPLAY = "KeyboardDisplay"

# ********************************
#    Bus paths and object paths
# --------------------------------
BLUEZ_BUS_NAME = 'org.bluez'
BLUEZ_OBJ_PATH = '/org/bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = '/test/agent'
AGENT_MANAGER = 'org.bluez.AgentManager1'

# ********************
#    Dongle Objects
# --------------------
Hub_Output_Dongle = None
Hub_Input1_Dongle = None
# Hub_Input2_Dongle = None
# Pi_Bt_Dongle      = None

FoundDevObjList = list()
DBusStragglers = list()
bus = None


class DeviceAndProperties:
    def __init__(self, deviceObj, properties, props_iface):
        self.deviceObj = deviceObj
        self.properties = properties
        self.props_iface = props_iface


class HubDongle:
    def __init__(self, mac_address: str):
        """
        @info : Initialize dongle with the givenpair_and_connect mac address.
        @param : str(mac address)
                Ex. "00:1A:7D:DA:71:13"
        """
        self.device_list = []  # Populate with class: DeviceAndProperties.
        # - deviceObj
        # - properties
        self.usable_devices = []
        self.connected_obj = None
        self.MediaControl = self.MediaControlClass()
        try:
            # Make adapter object with specified mac address.
            this_Dongle = adapter.Adapter(mac_address)
            this_Dongle.on_device_found = self.on_device_found
            self.Dongle = this_Dongle
        except:
            self.Dongle = None
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
        try:
            print(device.address)
            print(device.name)
        except:
            print('Error')

    def null_device_found(self, device: device.Device):
        """
        @info : Method for when device is not in use at the moment.
        """
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
            pass  # means it was on or some other issue.

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
                print("Pairing Failed.")
                return 0

            print("Device paired.")

            trustResultError = True
            try:
                trustResultError = device_and_props.props_iface.Set("org.bluez.Device1", "Trusted", True)
            except Exception as ee:
                print(ee)
                print("Failed to trust")

            connectResultError = True
            try:
                connectResultError = found_device.Connect()
            except Exception as eee:
                connectResultError = connect_exception_handler(eee)
            if connectResultError:
                print("Connecting Failed.")
                return 0

            if not connectResultError:
                self.connected_obj = found_device
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
            print("No usable devices.")
            return False

        for i, device in enumerate(self.usable_devices, 1):
            print("%d : %s" % (i, device.properties["Name"]))

        # Get selection from user. This can be replaced with something else later.
        selection = int(input())
        if selection > i or selection < 1:
            print("Invalid Selection")
            return False
        else:
            # try:
            target = self.usable_devices[selection - 1]
            self.pair_and_connect(target)
            # except:
            #     pass

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
                self.pair_and_connect(target)
            except:
                pass

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
            print("Finished fetching media controls")

    def getMediaControl(self):
        try:
            connected_device = self.connected_obj
            ctrl_obj = bus.get_object(BLUEZ_BUS_NAME, connected_device.object_path)
            ctrl_props_iface = dbus.Interface(ctrl_obj, 'org.freedesktop.DBus.Properties')
            ctrl_properties = ctrl_props_iface.GetAll('org.bluez.MediaControl1')
            self.MediaControl.MediaController = dbus.Interface(ctrl_obj, 'org.bluez.MediaControl1')
            print("Got Controller obj")
        except:
            print("No Controller obj available")
            time.sleep(0.1)
        try:
            if 'Player' in ctrl_properties:  # If there is a player, we need to go deeper.
                play_obj = bus.get_object(BLUEZ_BUS_NAME, ctrl_properties['Player'])
                play_props_iface = dbus.Interface(play_obj, 'org.freedesktop.DBus.Properties')
                play_properties = play_props_iface.GetAll('org.bluez.MediaPlayer1')
                self.MediaControl.MediaPlayer = dbus.Interface(play_obj, 'org.bluez.MediaPlayer1')
                print("Got Player obj")
        except:
            print("No Player obj available")
        finally:
            if self.MediaControl.MediaPlayer is None:
                print("No MediaPlayer was found")

    def getMediaTransport(self):
        """https://scribles.net/controlling-bluetooth-audio-on-raspberry-pi/"""
        obj = bus.get_object('org.bluez', "/")
        mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
        try:
            for path, ifaces in mgr.GetManagedObjects().items():
                if (self.connected_obj.object_path in path) and \
                        ('org.bluez.MediaTransport1' in ifaces):
                    self.MediaControl.MediaTransporter = dbus.Interface(
                        bus.get_object('org.bluez', path),
                        'org.freedesktop.DBus.Properties')
                    print("Got Transporter obj")
                    continue
        except:
            print("No Transporter obj available")
        finally:
            if self.MediaControl.MediaTransporter is None:
                print("No Transporter obj was found")

    class MediaControlClass:
        def __init__(self):
            self.MediaController = None
            self.MediaPlayer = None
            self.MediaTransporter = None

        def use_media_controls(self):
            if self.MediaController is None and self.MediaPlayer is None and self.MediaTransporter is None:
                return

            Controller_Message = ["Q:",
                                  "  1: FastForward",
                                  "  2: Next",
                                  "  3: Pause",
                                  "  4: Play",
                                  "  5: Previous",
                                  "  6: Rewind",
                                  "  7: Stop",
                                  "  8: Volume Down",
                                  "  9: Volume Up"]
            Player_Message = ["W",
                              "  1: FastForward",
                              "  2: Hold",
                              "  3: Next",
                              "  4: Pause",
                              "  5: Play",
                              "  6: Press",
                              "  7: Previous",
                              "  8: Release",
                              "  9: Rewind",
                              "  0: Stop"]
            Transporter_Message = ["E",
                                   "  1: Get Volume",
                                   "  2: Volume Down",
                                   "  3: Volume Up"]
            if self.MediaController is not None:
                for c_message in Controller_Message:
                    print(c_message)
            if self.MediaPlayer is not None:
                for p_message in Player_Message:
                    print(p_message)
            if self.MediaTransporter is not None:
                for t_message in Transporter_Message:
                    print(t_message)
            x = "X"
            while True:
                x = input()
                if x == "Z":
                    break
                elif len(x) != 2:
                    print("Command should be 2 characters. Try again")
                    continue
                else:
                    if x[0] == "q" or x[0] == "Q":  # Control Media Controller
                        if x[1] == "1":
                            self.MediaController.FastForward()
                        elif x[1] == "2":
                            self.MediaController.Next()
                        elif x[1] == "3":
                            self.MediaController.Pause()
                        elif x[1] == "4":
                            self.MediaController.Play()
                        elif x[1] == "5":
                            self.MediaController.Previous()
                        elif x[1] == "6":
                            self.MediaController.Rewind()
                        elif x[1] == "7":
                            self.MediaController.Stop()
                        elif x[1] == "8":
                            self.MediaController.VolumeDown()  # Doesn't work
                        elif x[1] == "9":
                            self.MediaController.VolumeUp()  # Doesn't work
                    if x[0] == "w" or x[0] == "W":
                        if x[1] == "1":
                            self.MediaPlayer.FastForward()
                        elif x[1] == "2":
                            self.MediaPlayer.Hold()
                        elif x[1] == "3":
                            self.MediaPlayer.Next()
                        elif x[1] == "4":
                            self.MediaPlayer.Pause()
                        elif x[1] == "5":
                            self.MediaPlayer.Play()
                        elif x[1] == "6":
                            self.MediaPlayer.Press()
                        elif x[1] == "7":
                            self.MediaPlayer.Previous()
                        elif x[1] == "8":
                            self.MediaPlayer.Release()
                        elif x[1] == "9":
                            self.MediaPlayer.Rewind()
                        elif x[1] == "0":
                            self.MediaPlayer.Stop()
                    if x[0] == "e" or x[0] == "E":
                        if x[1] == "1":  # Get Volume
                            volume = self.GetVolume()
                            print(volume)
                        elif x[1] == "2":  # Volume Down
                            volume = self.VolumeDown()
                            print(volume)
                        elif x[1] == "3":  # Volume Up
                            volume = self.VolumeUp()
                            print(volume)

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

        def Play_Control(self):
            pass

        def Pause_Control(self):
            pass

        def VolUp_Control(self):
            pass

        def VolDn_Control(self):
            pass


class DongleInitError(Exception):
    """@info: Exception for InitializeDongle()"""
    pass


class StragglerObj():
    def __init__(self, obj_path: str):
        self.path = obj_path
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
    service = 'org.bluez'
    object_path = '/org/bluez'
    recursive_introspection(service, object_path)
    list_dbus_stragglers()


def list_dbus_stragglers():
    """
    @info : NON FUNCTIONAL. JUST VISUAL.
            Print the DBus Stragglers.
    """
    global DBusStragglers  # List of strings
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
    if "org.bluez.Error.AlreadyExists" in str(error):  # The only acceptable error
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
                straggler.Remove = False  # Mark it to not remove
            elif straggler.Remove is not False:  # Make sure that it hasn't been marked to not remove
                straggler.Remove = True
    for straggler in DBusStragglers:
        try:
            if straggler.Remove is not False:  # If marked for removal
                this_dongle.remove_device(straggler.path)
                print("Removed : %s" % straggler.path)
        except:
            pass


def shutdown(whiteList, dongle_1=None, dongle_2=None, dongle_3=None):
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
        remove_stragglers(whiteList, dongle.Dongle)

        # Power off
        dongle.power_off()


def main():
    global Hub_Input1_Dongle, Hub_Output_Dongle, bus

    bus = dbus.SystemBus()  # Define global system bus to use
    bluez_obj = bus.get_object(BLUEZ_BUS_NAME, BLUEZ_OBJ_PATH)  # Get proxy object
    agent_manager = dbus.Interface(bluez_obj, AGENT_MANAGER)  # Get agent manager
    agent_manager.RegisterAgent(AGENT_PATH, NO_INPUT_NO_OUTPUT)  # Set agent as NoInputNoOutput mode

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
        # I think to stop it, it would be :
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
        shutdown([], dongle_1=Hub_Input1_Dongle, dongle_2=Hub_Output_Dongle)
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
    shutdown([], dongle_1=Hub_Input1_Dongle, dongle_2=Hub_Output_Dongle)
    print("End of line")


if __name__ == '__main__':
    print("Here is my name: ")
    print(__name__)
    main()