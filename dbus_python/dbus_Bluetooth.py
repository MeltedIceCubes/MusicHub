#  https://re-engines.com/2021/09/21/bluez/

from bluezero import adapter, device, tools
import time

found_device: device.Device = None

MAC_LIST = ["00:1A:7D:DA:71:13",
            "00:1A:7D:DA:71:14",
            "00:1A:7D:DA:71:15",
            "DC:A6:32:92:BF:F5"]
AdapterList = list()
Hub_Output = None
Hub_Input1 = None
Hub_Input2 = None
Pi_Dongle  = None


class AdapterNotInitialized(Exception):
    pass


class UnknownAdapter(Exception):
    pass


class DeviceDataError(Exception):
    pass


class AdapterMAC:  # define class for adapter initialization
    def __init__(self, address):
        self.address = str(address)
        self.found = False


def register_adapters():
    global MAC_LIST
    global AdapterList
    AdapterList.append(AdapterMAC(MAC_LIST[0]))  # MusicHub_Output
    AdapterList.append(AdapterMAC(MAC_LIST[1]))  # MusicHub_Input2
    AdapterList.append(AdapterMAC(MAC_LIST[2]))  # MusicHub_Input1
    AdapterList.append(AdapterMAC(MAC_LIST[3]))  # raspberry_pi_output


def check_for_dongles(found_adapters, adapterList):
    for a in found_adapters:
        for b in adapterList:
            if b.address == str(a):  # Access as normal string
                b.found = True
                break                # No need to check for this MAC anymore

    # Check if all dongles are  correctly listed. If not, raise Error
    check_dongle_init(adapterList)


def check_dongle_init(adpt_list):
    global Hub_Output
    global Hub_Input1
    global Hub_Input2
    global Pi_Dongle
    #  Iterate through adapters
    for a in adpt_list:
        if not a.found:
            raise AdapterNotInitialized("")
        else:
            #  Assign to adapter variables.
            if a.address == str(MAC_LIST[0]):
                Hub_Output = adapter.Adapter(a.address)
            elif a.address == str(MAC_LIST[1]):
                Hub_Input1 = adapter.Adapter(a.address)
            elif a.address == str(MAC_LIST[2]):
                Hub_Input2 = adapter.Adapter(a.address)
            elif a.address == str(MAC_LIST[3]):
                Pi_Dongle = adapter.Adapter(a.address)
            else:
                raise UnknownAdapter("Unknown adapter found : " + str(a.address))
            #print_dongle_properties(a.adapterObj)


def print_dongle_properties(dongle_obj):
    print('address: ', dongle_obj.address)
    print('name: ', dongle_obj.name)
    print('alias: ', dongle_obj.alias)
    print('powered: ', dongle_obj.powered)
    print('pairable: ', dongle_obj.pairable)
    print('pairable timeout: ', dongle_obj.pairabletimeout)
    print('discoverable: ', dongle_obj.discoverable)
    print('discoverable timeout: ', dongle_obj.discoverabletimeout)
    print('discovering: ', dongle_obj.discovering)
    print('Powered: ', dongle_obj.powered)


#  Call-back when a device is found
def on_device_found(device: device.Device):
    try:
        print(device.address)
        print(device.name)
    except:
        print('Error')

found_bob: device.Device = None
def connect_to_Bob(device: device.Device):
    global found_bob
    if device.name == "Bob":
        found_bob = device

# ****************
# ***   Main   ***
# ****************
def main():
    global Hub_Output
    global Hub_Input1
    global Hub_Input2
    global Pi_Dongle
    #List all of our adapters here.
    register_adapters()

    # Get list of connected adapters (Hardware)
    dongles = adapter.list_adapters()

    #List Dongles
    #print('dongles available: ', dongles)

    #Check to see if our dongles are properly listed. Error raised if not.
    check_for_dongles(dongles, AdapterList)

    # Turn off if it was on
    Hub_Input1.powered = False
    time.sleep(1)
    Hub_Input1.powered = True

    print("Now powered: ", Hub_Input1.powered)

    # Define callback for device found
    Hub_Input1.on_device_found = on_device_found

    # Start scan
    Hub_Input1.nearby_discovery(timeout=30)

    if found_bob is not None:
        found_bob.pair()
        print("Paired with Bob")

    print("Powering off")
    Hub_Input1.powered = False

def example_main():
    # Bluetoothドングルの取得
    dongles = adapter.list_adapters()
    #print('dongles available: ', dongles)  # List dongles

    check_for_dongles(dongles, AdapterList)

    dongle = adapter.Adapter(dongles[0])

    # Bluetoothドングルの電源が切れている場合は、電源を入れる
    if not dongle.powered:
        dongle.powered = True
        print('Now powered: ', dongle.powered)
    print('Start discovering')

    # デバイスが見つかったときのコールバック
    dongle.on_device_found = on_device_found

    # デバイスのスキャン開始
    dongle.nearby_discovery(timeout=20)

    # デバイスが見つかったら、ペアリング
    if (found_device != None):
        found_device.pair()

    # dongle.powered = False


if __name__ == '__main__':
    print(__name__)
    main()
