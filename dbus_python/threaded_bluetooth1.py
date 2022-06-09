#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#   &&&            MultiThreaded Bluetooth              &&&
#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

# ***************************
# ***   Package imports   ***
# ---------------------------
from bluezero import adapter, device
import time
import dbus
from xml.etree import ElementTree
import re
import sys
import threading
import menu_list2 as Menu
import menu_entries

# *****************************
#      Class Definitions
# -----------------------------
class DongleInitError(Exception):
    """@info: Exception for InitializeDongle()"""
    pass

class Event_Item:
    def __init__(self,passed_method, priority = 5, passed_args = None):
        self.Priority = priority
        self.Event = passed_method
        self.args = passed_args

class Executer_Class:
    def __init__(self):
        self._D1EventQueue = []
        self.D1Curr_event = None

        self._D2EventQueue = []
        self.D2Curr_event = None

        self._D3EventQueue = []
        self.D3Curr_event = None

    @property
    def D1EventQueue(self):
        return self._D1EventQueue
    @D1EventQueue.setter
    def D1EventQueue(self,val):
        self._D1EventQueue = val

    @property
    def D2EventQueue(self):
        return self._D2EventQueue
    @D2EventQueue.setter
    def D2EventQueue(self,val):
        self._D2EventQueue = val

    @property
    def D3EventQueue(self):
        return self._D3EventQueue
    @D3EventQueue.setter
    def D3EventQueue(self,val):
        self._D3EventQueue = val

    # @property
    # def EventQueue(self):
    #     return self._EventQueue
    # @EventQueue.setter
    # def EventQueue(self,val):
    #     self._EventQueue = val


    def append(self, function, lock_to_use, priority):
        global Dongle_Selection

        func_init = function

        # Set up thread to be run from queue.
        func_event_thread = threading.Thread(target = func_init,args = (lock_to_use,))

        # Event Item with function and the Priority from the function itself.
        func_event_item = Event_Item(func_event_thread, priority)

        if Dongle_Selection is Hub_Dongle1:
            temp_EventQueue = self.D1EventQueue + [func_event_item]
            self.D1EventQueue = sorted(temp_EventQueue, key=lambda x: x.Priority)
            return self.D1EventQueue
        elif Dongle_Selection is Hub_Dongle2:
            # Temp location to use for sorting.
            temp_EventQueue = self.D2EventQueue + [func_event_item]
            self.D2EventQueue = sorted(temp_EventQueue, key=lambda x: x.Priority)
            return self.D2EventQueue
        elif Dongle_Selection is Hub_Dongle3:
            # Temp location to use for sorting.
            temp_EventQueue = self.D3EventQueue + [func_event_item]
            self.D1EventQueue = sorted(temp_EventQueue, key=lambda x: x.Priority)
            return self.D3EventQueue


        return None

    def RunNextInQueue(self,queue):
        #queue = one of the dongle's queues.
        if len(queue) > 0:
            queued_func = queue.pop(0)
            queued_func.Event.start()
            return queued_func.Event
        else:
            return None

    def Execution_Loop(self):
        global EXIT_PROGRAM
        while not EXIT_PROGRAM: # Enter loop
            if not D1_Lock.locked(): # Dongle 1
                self.D1Curr_event = self.RunNextInQueue(self.D1EventQueue)
            if not D2_Lock.locked(): # Dongle 2
                self.D2Curr_event = self.RunNextInQueue(self.D2EventQueue)
            if not D3_Lock.locked(): # Dongle3
                self.D3Curr_event = self.RunNextInQueue(self.D3EventQueue)

class Controller_Class:
    def __init__(self):
        print("Press Z at any time to quit\n\n")
        self.CurrMenu = None

    def GetInput(self):
        global EXIT_PROGRAM
        while not EXIT_PROGRAM:
            self.CurrMenu.PrintMenu()

            x = input()

            if x =="Z": # Exit condition
                EXIT_PROGRAM = True
                break
            # TODO : ADD THREAD CANCEL FLAG

            # Get command from the input choice.
            selected_command, command_priority = Menu.ParseSelection(self.CurrMenu,x)
            Executer.append(selected_command,D1_Lock,command_priority)

class HubDongle:
    def __init__(self, lock, mac_address: str):
        """
        @info : Initialize dongle with the given mac address.
        @param : str(mac address)
                Ex. "00:1A:7D:DA:71:13"
        """

        pass

        try:
            # Make adapter object with specified mac address.
            this_Dongle = adapter.Adapter(mac_address)
            # this_Dongle.on_device_found = self.on_device_found
            self.Dongle = this_Dongle
        except:
            self.Dongle = None
            raise DongleInitError("Dongle with MAC:%s could not initialize" % mac_address)


def InitializeAllDongles():
    Hub_Dongle1 = HubDongle(D1_Lock, MAC_LIST[1])

    Hub_Dongle2 = HubDongle(D2_Lock, MAC_LIST[2])

    Hub_Dongle3 = HubDongle(D3_Lock, MAC_LIST[3])


def select_dongle1(lock):
    lock.acquire()
    print("Dongel 1")
    Dongle_Selection = Hub_Dongle1
    lock.release()
def select_dongle2(lock):
    lock.acquire()
    print("Dongel 2")
    Dongle_Selection = Hub_Dongle2
    lock.release()
def select_dongle3(lock):
    lock.acquire()
    print("Dongel 3")
    Dongle_Selection = Hub_Dongle3
    lock.release()

class Dongle_Select_Obj:
    def __init__(self):
        self.msg       = menu_entries.Dongle_select_msg
        self.select    = menu_entries.Dongle_select_select
        self.functions = [select_dongle1, select_dongle2,select_dongle3]
        self.priority  = [1,1,1]


# *****************************
#      Define Constants
# -----------------------------
EXIT_PROGRAM = False
MAC_LIST = ["DC:A6:32:92:BF:F5",
            "00:1A:7D:DA:71:13",
            "00:1A:7D:DA:71:14",
            "00:1A:7D:DA:71:15"]
            # raspberry pi
            # MusicHub : 1
            # MusicHub : 2
            # MusicHub : 3


# ********************************
#     Define Global Variables
# --------------------------------
EXIT_PROGRAM = False

# Main Control & Execution Scheduler
Controller = Controller_Class()
Executer = Executer_Class()

Dongle_Selection= None

# Dongle Objs :
Hub_Dongle1 = None # 00:1A:7D:DA:71:13
Hub_Dongle2 = None # 00:1A:7D:DA:71:14
Hub_Dongle3 = None # 00:1A:7D:DA:71:15

# Thread lock objs
D1_Lock = threading.Lock()
D2_Lock = threading.Lock()
D3_Lock = threading.Lock()

# Thread Cancel flag
D1_Cancel = False
D2_Cancel = False
D3_Cancel = False

Dongle_Selection_menu = Dongle_Select_Obj()

def main():
    InitializeAllDongles()
    Controller.CurrMenu = Menu.Menu_listing(Dongle_Selection_menu.msg,
                                            Dongle_Selection_menu.select,
                                            Dongle_Selection_menu.functions,
                                            Dongle_Selection_menu.priority)

    Controller_Thread = threading.Thread(target = Controller.GetInput)
    Executer_Thread   = threading.Thread(target = Executer.Execution_Loop)

    Controller_Thread.start()
    Executer_Thread.start()

    Controller_Thread.join()
    Executer_Thread.join()

if __name__ == "__main__":
    print("Starting Program")
    main()
    print("Ending Program")