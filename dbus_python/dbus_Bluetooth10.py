from cust_bluezero import adapter, device
import dbus
import re, sys, time, threading
from xml.etree import ElementTree

import logging
logging.basicConfig(format = '%(message)s',level = logging.DEBUG)
import config


# *********************************************************
# ***             Global Declarations                   ***
# *********************************************************
MAC_LIST = ["DC:A6:32:92:BF:F5",
            "00:1A:7D:DA:71:13",
            "00:1A:7D:DA:71:14",
            "00:1A:7D:DA:71:15"]
            # raspberry pi
            # MusicHub : 1
            # MusicHub : 2
            # MusicHub : 3

BLUEZ_BUS_NAME = 'org.bluez'


# *********************************************************
# ***                  Functions                        ***
# *********************************************************

class DeviceIFaceAndProps:
    """
    @info : storage for device's props and iface
    """
    def __init__(self, deviceObj, properties, props_iface):
        self.deviceObj = deviceObj
        self.properties = properties
        self.props_iface = props_iface

class Bluetooth_Object_Manager:
    def __init__(self):
        # Define global system bus to use
        self.SysBus = dbus.SystemBus()
        # Get proxy object
        bluez_obj   = self.SysBus.get_object('org.bluez', '/org/bluez')
        # Get agent manager
        self.agent_manager = dbus.Interface(bluez_obj, 'org.bluez.AgentManager1')
        # Set agent as NoInputNoOutput mode
        self.agent_manager.RegisterAgent('/test/agent', "NoInputNoOutput")

        self.Hub_Dongle1 = HubDongle(MAC_LIST[1], self.SysBus, "Dongle 1")
        self.Hub_Dongle2 = HubDongle(MAC_LIST[2], self.SysBus, "Dongle 2")
        self.Hub_Dongle3 = HubDongle(MAC_LIST[3], self.SysBus, "Dongle 3")
        self.Curr_Dongle = self.Hub_Dongle1
        self.VolIdleCounter = 0
        self.Dongle1Vol  = 0
        self.Dongle2Vol  = 0
        self.Dongle3Vol  = 0

        self.Stragglers = list()
    def shutdown(self):
        self.Hub_Dongle1.discoverable_off()
        self.Hub_Dongle1.Power_Off()
        self.Hub_Dongle2.discoverable_off()
        self.Hub_Dongle2.Power_Off()
        self.Hub_Dongle3.discoverable_off()
        self.Hub_Dongle3.Power_Off()
        config.PrintToSocket("Dongle Power off")
        # Maybe clearing stragglers should be last?
        self.find_dbus_stragglers()
        self.remove_stragglers()

    def DongleSelect(self, Next = False, Prev = False):
        # This is dumb but I dont want to over complicate it...
        if (Next == False) and (Prev == False): 
            return
        if Next == True:
            if self.Curr_Dongle.Dongle.address == MAC_LIST[1]:
                self.Curr_Dongle = self.Hub_Dongle2
            elif self.Curr_Dongle.Dongle.address == MAC_LIST[2]:
                self.Curr_Dongle = self.Hub_Dongle3
        elif Prev == True:
            if self.Curr_Dongle.Dongle.address == MAC_LIST[3]:
                self.Curr_Dongle = self.Hub_Dongle2
            elif self.Curr_Dongle.Dongle.address == MAC_LIST[2]:
                self.Curr_Dongle = self.Hub_Dongle1

    def GetDongleVolumes(self):
        if self.VolIdleCounter == 0:
            if self.Hub_Dongle1.MediaControl.MediaTransporter != None:
                self.Hub_Dongle1.Volume = self.Hub_Dongle1.MediaControl.GetVolume()
            if self.Hub_Dongle2.MediaControl.MediaTransporter != None:
                self.Hub_Dongle2.Volume = self.Hub_Dongle2.MediaControl.GetVolume()
            if self.Hub_Dongle3.MediaControl.MediaTransporter != None:
                self.Hub_Dongle3.Volume = self.Hub_Dongle3.MediaControl.GetVolume()
        else:
            self.VolIdleCounter += 1
            if self.VolIdleCounter >= 15:
                self.VolIdleCounter = 0

    def remove_stragglers(self):

        for straggler in self.Stragglers:
            try:
                self.Hub_Dongle1.Dongle.remove_device(straggler)
                logging.debug("Removed : %s" %straggler)
                self.Hub_Dongle2.Dongle.remove_device(straggler)
                logging.debug("Removed : %s" % straggler)
                self.Hub_Dongle3.Dongle.remove_device(straggler)
                logging.debug("Removed : %s" % straggler)
            except:
                logging.debug("Failed to remove : %s" %straggler)

    def find_dbus_stragglers(self):
        """
        @info : finds objects within the given adapter's path to mark for removal
                Calls and lists the objects that are stuck in the cache for bluez
       @param :- service : dbus service to introspect Ex: "org.bluez"
        - object_path : the path of the top most object we want to introspect.
                        Ex: "/org/bluez"
        """
        self.recursive_introspection('org.bluez', '/org/bluez')

    def recursive_introspection(self, service = 'org.bluez', object_path = '/org/bluez' ):
        match_result = self.get_device_mac(object_path)

        _obj = self.SysBus.get_object(service,object_path)

        if match_result is not None:
            try:
                _device_props = dbus.Interface(_obj, 'org.freedesktop.DBus.Properties')
                if (_device_props.Get('org.bluez.Device1', 'Trusted') == True):
                    # We shall spare the trusted.
                    print("Not Removing : %s" %(object_path))
            except:
                # self.Stragglers.append(match_result) # Can't be trusted. Remove
                self.Stragglers.append(object_path) # Can't be trusted. Remove


    # Goes through object looking for new objects
        _obj = self.SysBus.get_object(service,object_path)
        _iface = dbus.Interface(_obj, 'org.freedesktop.DBus.Introspectable')
        _xml_string = _iface.Introspect()
        for child in ElementTree.fromstring(_xml_string):
            if child.tag == 'node':
                if object_path == '/':
                    object_path = ''
                new_path = '/'.join((object_path, child.attrib['name']))
                self.recursive_introspection(service, new_path)

    def get_device_mac(self,path):
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


class HubDongle:
    def __init__(self, mac_address: str, bus, Name):
        # System Bus Object
        self.SysBus = bus

        # device_list :
        #  - used to pairing and connecting
        #  - list of potential devices to connect to.
        #  - Used in find_
        self.Name = Name
        self.device_list = []
        self.scan_time = 5
        self.connected_device = None
        self.Volume = 0
        self.MediaControl = self.MediaControlClass()
        self.Stragglers = list()
        self.PulseIfc = None
        try:
            # Make adapter object with specified mac address.
            self.Dongle = adapter.Adapter(mac_address)
            self.Dongle.on_device_found = self.on_device_found
        except:
            self.Dongle = None
            logging.debug("\nDongle with MAC:%s could not initiailze" % mac_address)

    def on_device_found(self, device: device.Device):
        """
        @info : Call back function when a device is found.
        @param : device object
        """
        try:
            logging.debug(device.address)
            logging.debug(device.name)
        except:
            logging.debug('Error')

    # ---------------------------------------------------------
    # ---                      Power                        ---
    # ---------------------------------------------------------
    def Power_Check(self):
        return self.Dongle.powered

    def Power_Toggle(self):
        ctrl = None # Unused
        if not self.Power_Check(): # OFF -> ON
            self.Dongle.powered = True
            print("Power on")
        else:                 # ON -> OFF
            self.Dongle.powered = False
            print("Power off")

    def Power_On(self):
        self.Dongle.powered = True
        print("Power on ")

    def Power_Off(self):
        self.Dongle.powered = False
        print("Power off ")
    # ---------------------------------------------------------
    # ---                    Scan                           ---
    # ---------------------------------------------------------

    def Scan_On(self):
        """
        @info : Start Scan in a separate thread.
        @TODO : Add spinner animation to wait time
        """
        ctrl = None # Unused
        stop_sig = [False] # used to stop wait time counter.
        # Set up thread for discovery
        discovery_Thread = threading.Thread(target = self.enable_nearby_discovery,
                                            args =(self.scan_time, stop_sig,) )
        discovery_Thread.start()
        #Replace this with an animation
        showWaitTime(self.scan_time*1000, stop_sig)
        discovery_Thread.join()

    def enable_nearby_discovery(self, timer, stop_signal):
        """
        @info   : start nearby discovery:
                : Sends stop signal to the waiter to stop.
        """
        try:
            self.discoverable_on()
            self.Dongle.nearby_discovery(timeout = timer)
            # self.Dongle.discoverable = False
            logging.debug("discovery over")
        except:
            logging.debug("Not powered")
        self.find_connectable_devices()
        stop_signal[0] = True
    def discoverable_on(self):
        self.Dongle.discoverable = True
    def discoverable_off(self):
        try:
            self.Dongle.discoverable = False
        except:
            pass
    def find_connectable_devices(self):
        """
        @info : Find and save viable devices to connect to.
        """
        # Clear device list.(Since we're updating it from here)
        self.device_list = []
        # DBus path to use
        path_prefix = self.Dongle.path
        # Get object manager
        _manager = dbus.Interface(self.SysBus.get_object("org.bluez","/"),
                                    "org.freedesktop.DBus.ObjectManager")
        # Get objects to look through.
        objects = _manager.GetManagedObjects()
        # Iterate through objects.
        for path, ifaces in objects.items():
            # Get "Device1" interface of this object
            found_device = ifaces.get("org.bluez.Device1")
            # This object didn't have "Device1" interface
            if found_device is None:
                continue
            # Check if this object from the dongle we're using now.
            if (path.startswith(path_prefix)):
                # get object from system bus.
                _obj = self.SysBus.get_object(BLUEZ_BUS_NAME, path)
                # get property interface
                _props_iface = dbus.Interface(_obj, 'org.freedesktop.DBus.Properties')
                # get all properties of "Device1"
                _properties = _props_iface.GetAll("org.bluez.Device1")
                # get device interface
                _device_iface = dbus.Interface(_obj, "org.bluez.Device1")
                # check if the device has a name.
                # (if it doesn't it's some stray signal)
                if "Name" in _properties:
                    # Append device's properties and interface
                    self.device_list.append(
                        DeviceIFaceAndProps(_device_iface,
                                            _properties,
                                            _props_iface))
        print("Devices found and listed")

    def pair_and_connect(self,device_and_props):
        """
        @info : Pair and connect to a found device.
        @param : device object
        """
        target_device = device_and_props.deviceObj

        if target_device:
            try:
                if device_and_props.props_iface.Get('org.bluez.Device1', 'Trusted') == True:
                # TODO : Check if target is already trusted to see if Pair and Trust process
                #       can be eliminated.
                    try:
                        connectResultError = target_device.Connect()
                    except Exception as eee:
                        connectResultError = connect_exception_handler(eee)
                    if connectResultError:
                        config.PrintToSocket(r'*d0-Failed to Connect\r')
                    else:
                        config.PrintToSocket(r'*d0-Device Connected\r')
                        self.connected_device = target_device
                        return True
            except:
                pass
            else: # Back to default way. Pair->Trust->Connect
                pairResultError = True
                try:
                    pairResultError = target_device.Pair()
                except Exception as e:
                    pairResultError = pair_exception_handler(e)
                if pairResultError is not None:
                    return False
                config.PrintToSocket(r'*d0-Device Paired\r')

                trustResultError = True
                try:
                    trustResultError = device_and_props.props_iface.Set("org.bluez.Device1", "Trusted", True)
                    config.PrintToSocket(r'*d0-Device Trusted\r')
                except Exception as ee:
                    config.PrintToSocket(r'*d0-Failed to trust\r')

                try:
                    connectResultError = target_device.Connect()
                except Exception as eee:
                    connectResultError = connect_exception_handler(eee)
                if connectResultError:
                    config.PrintToSocket(r'*d0-Failed to Connect\r')
                    return False
                else:
                    config.PrintToSocket(r'*d0-Device Connected\r')
                    self.connected_device = target_device
                    return True
        else:
            config.PrintToSocket(r'*d0-Something went wrong. Try again.\r')
            return False



    # ---------------------------------------------------------
    # ---                    Media                          ---
    # ---------------------------------------------------------
        # Note: Do I have to refresh if player object changes?
        # or does it not change?
    class MediaControlClass:
        def __init__(self):
            self.MediaController = None
            self._ifc_MediaController = None
            self.MediaPlayer     = None
            self._ifc_MediaPlayer = None
            self.MediaTransporter = None
            # self._ifc_MediaTransporter = None

        def Play_Media(self):
            if self.MediaController != None:
                self.MediaController.Play()
            elif self.MediaPlayer != None:
                self.MediaPlayer.Play()
        def Pause_Media(self):
            if self.MediaController != None:
                self.MediaController.Pause()
            elif self.MediaPlayer != None:
                self.MediaPlayer.Pause()
        def Plause_Media(self):
            try:
                state = self.GetPlayStatus_Media()
                
                if state == "playing":
                    self.Pause_Media()
                elif state == "paused":
                    self.Play_Media()
                else: # Means we can't control shit
                    pass
            except:
                pass

        def GetPlayStatus_Media(self):
            val = None
            try:
                val = self._ifc_MediaPlayer.Get('org.bluez.MediaPlayer1', 'Status')

            except:
                try:
                    val = self._ifc_MediaController.Get('org.bluez.MediaControl1', 'Status')
                except:
                    pass
            return val
            # None = Failed
            # 1    = Playing
            # 2    = Paused



        def Prev_Media(self):
            try: 
                if self.MediaController != None: 
                    self.MediaController.Previous()
                elif self.MediaPlayer != None: 
                    self.MediaPlayer.Previous()
            except:
                pass
        def Next_Media(self):
            try:
                if self.MediaController != None: 
                    self.MediaController.Next()
                elif self.MediaPlayer != None: 
                    self.MediaPlayer.Next()
            except:
                pass
        def VolUp_Media(self):
            volume = None
            try:
                # volume = self.thisDongle.Volume
                volume = self.GetVolume()
                volume += 10
                if volume >127:
                    volume = 127
                self.MediaTransporter.Set('org.bluez.MediaTransport1', 'Volume', dbus.UInt16(volume))
            except:
                volume = -1
            finally:
                return volume
        def VolDn_Media(self):
            volume = None
            try:
                volume = self.GetVolume()
                volume -= 10
                if volume < 0:
                    volume = 0
                self.MediaTransporter.Set('org.bluez.MediaTransport1', 'Volume', dbus.UInt16(volume))
            except:
                volume = -1
            finally:
                return volume
        def VolMute_Media(self):
            volume = 0
            try:
                self.MediaTransporter.Set('org.bluez.MediaTransport1', 'Volume', dbus.UInt16(volume))
            except:
                volume = -1
            finally:
                return volume
        def GetVolume(self):
            if self.MediaTransporter is not None:
                try:
                    return self.MediaTransporter.Get('org.bluez.MediaTransport1', 'Volume')
                except:
                    return 0
            else:
                return 0
    def get_media_controls(self):
        if self.connected_device:
            for i in range(3): # Number of attempts
                self.getMediaControlObj()
                if (self.MediaControl.MediaController is not None) and\
                        (self.MediaControl.MediaPlayer is not None):
                    break
            self.getMediaTransportObj()     # Separate from Media control attempts
                                            # since some devices may not support this.

    def getMediaControlObj(self):
        _ctrl_obj           = None
        _ctrl_props_iface   = None
        _ctrl_properties    = None
        try:
            connected_device = self.connected_device
            _ctrl_obj           = self.SysBus.get_object(BLUEZ_BUS_NAME, connected_device.object_path)
            _ctrl_props_iface   = dbus.Interface(_ctrl_obj, 'org.freedesktop.DBus.Properties')
            _ctrl_properties    = _ctrl_props_iface.GetAll('org.bluez.MediaControl1')
            self.MediaControl.MediaController = dbus.Interface(_ctrl_obj, 'org.bluez.MediaControl1')
            self.MediaControl._ifc_MediaController = _ctrl_props_iface
            logging.debug("Got Controller obj")
        except:
            logging.debug("No Controller obj available")
        finally:
            if self.MediaControl.MediaController is None:
                logging.debug("No Media Controller was found")

        try:
            if 'Player' in _ctrl_properties: # if there is a player iface, we need to go deeper
                _play_obj           = self.SysBus.get_object(BLUEZ_BUS_NAME, _ctrl_properties['Player'])
                _play_props_iface   = dbus.Interface(_play_obj, 'org.freedesktop.DBus.Properties')
                _play_properties    = _play_props_iface.GetAll('org.bluez.MediaPlayer1')
                self.MediaControl.MediaPlayer = dbus.Interface(_play_obj, 'org.bluez.MediaPlayer1')
                self.MediaControl._ifc_MediaPlayer = _play_props_iface
                logging.debug("Got Player obj")
        except:
            logging.debug("No Player obj available")
        finally:
            if self.MediaControl.MediaPlayer is None:
                logging.debug("No Media Player was found")

    def getMediaTransportObj(self):
        """
        https://scribles.net/controlling-bluetooth-audio-on-raspberry-pi/
        """
        obj = self.SysBus.get_object('org.bluez','/')
        mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
        try:
            for _path, _ifaces in mgr.GetManagedObjects().items():
                if (self.connected_device.object_path in _path) and \
                        ('org.bluez.MediaTransport1' in _ifaces):
                    self.MediaControl.MediaTransporter = dbus.Interface(
                        self.SysBus.get_object('org.bluez',_path),
                        'org.freedesktop.DBus.Properties')
                    logging.debug("Got Transporter obj")
                    continue
        except:
            logging.debug("No Transporter obj available")
        finally:
            if self.MediaControl.MediaTransporter is None:
                logging.debug("No Transporter obj was found")





def pair_exception_handler(error):
    """
    @info : Handles the exception to any failed pair requests.
    @param : exceptions to device.Pair()
    @note : more info here :
            https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/device-api.txt
    """
    if "org.bluez.Error.AlreadyExists" in str(error):  # The only acceptable error
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
        logging.debug(error)
        logging.debug("Some other connecting error")
        return True

def showWaitTime(waitTime, stop_signal):
    # time in ms
    now = time.time() * 1000
    start = now
    incriment = 1000
    delta = now

    print(now-start)
    while (waitTime > ( now - start)) and stop_signal[0] == False:
        now = time.time() * 1000
        if (now-delta) > incriment:
            logging.debug(int(now-start))
            delta = now
    logging.debug("waitOver")



