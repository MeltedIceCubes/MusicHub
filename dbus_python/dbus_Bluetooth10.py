from cust_bluezero import adapter, device
import dbus
import re, sys, time, threading

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

BLUEZ_BUS_NAME       = 'org.bluez'


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
        bus = dbus.SystemBus()
        self.Hub_Dongle1 = HubDongle(MAC_LIST[1], bus)
        self.Hub_Dongle2 = HubDongle(MAC_LIST[2], bus)
        self.Hub_Dongle3 = HubDongle(MAC_LIST[3], bus)
        self.Curr_Dongle = self.Hub_Dongle1
    def shutdown(self):
        self.Hub_Dongle1.Power_Off()
        self.Hub_Dongle2.Power_Off()
        self.Hub_Dongle3.Power_Off()
        config.PrintToSocket("Dongle Power off")
class HubDongle:
    def __init__(self, mac_address: str, bus):
        # System Bus Object
        self.SysBus = bus

        # device_list :
        #  - used to pairing and connecting
        #  - list of potential devices to connect to.
        #  - Used in find_
        self._device_list = []


        try:
            # Make adapter object with specified mac address.
            self.Dongle = adapter.Adapter(mac_address)
            self.Dongle.on_device_found = self.on_device_found
        except:
            self.Dongle = None
            logging.debug("\nDongle with MAC:%s could not initiailze" % mac_address)
            raise DongleInitError("Dongle with MAC:%s could not initialize" % mac_address)

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

    # ---------------------------------------------------------
    # ---                      Power                        ---
    # ---------------------------------------------------------
    def Power_Check(self):
        return self.Dongle.powered

    def Power_Toggle(self, ctrl):
        ctrl = None # Unused
        if not self.Power_Check(): # OFF -> ON
            self.Dongle.powered = True
            print("Power on")
        else:                 # ON -> OFF
            self.Dongle.powered = False
            print("Power off")

    def Power_Off(self):
        self.Dongle.powered = False
    # ---------------------------------------------------------
    # ---                    Scanning                       ---
    # ---------------------------------------------------------

    def Scan_On(self, ctrl):
        """
        @info : Start Scan in a separate thread.
        @TODO : Add spinner animation to wait time
        """
        ctrl = None # Unused
        stop_sig = [False] # used to stop wait time counter.
        # Set up thread for discovery
        discovery_Thread = threading.Thread(target = self.enable_nearby_discovery,
                                            args =(5, stop_sig,) )
        discovery_Thread.start()
        showWaitTime(5000, stop_sig)
        discovery_Thread.join()

    def enable_nearby_discovery(self, timer, stop_signal):
        """
        @info : start nearby discovery:
              : Sends stop signal to the waiter to stop.
        """
        try:
            self.Dongle.discoverable = True
            self.Dongle.nearby_discovery(timeout = timer)
            # self.Dongle.discoverable = False
            print("discovery over")
        except:
            print("Not powered")
        self.find_connectable_devices()
        stop_signal[0] = True

    def find_connectable_devices(self):
        """
        @info : Find and save viable devices to connect to.
        """
        # Clear device list.(Since we're updating it from here)
        self._device_list = []
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
                    self._device_list.append(
                        DeviceIFaceAndProps(_device_iface,
                                            _properties,
                                            _props_iface))
        print("Devices found and listed")

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
            print(int(now-start))
            delta = now
    print("waitOver")


