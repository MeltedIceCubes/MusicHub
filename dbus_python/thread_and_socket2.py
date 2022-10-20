#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#   &&&            MultiThreaded Bluetooth              &&&
#   &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

# ***************************
# ***   Package imports   ***
# ---------------------------
from cust_bluezero import adapter, device
import time
import dbus
from xml.etree import ElementTree
import re
import sys
import threading
import menu_list3 as Menu
import menu_entries2 as  menu_entries
import dbus_Bluetooth9 as Bluetooth
import logging
from gpio import buttons_polling2

logging.basicConfig(format = '%(message)s',level = logging.DEBUG)


import socket
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

SocketOutput = None

# *****************************
#      Class Definitions
# -----------------------------
class DongleInitError(Exception):
    """@info: Exception for InitializeDongle()"""
    pass

class Event_Item:
    def __init__(self,passed_method, passed_args = None):
        self.Event = passed_method
        self.args = passed_args

class Executer_Class:
    def __init__(self):
        self.D1EventQueue = []
        self.D1Curr_event = None

        self.D2EventQueue = []
        self.D2Curr_event = None

        self.D3EventQueue = []
        self.D3Curr_event = None

    # @property
    # def D1EventQueue(self):
    #     return self._D1EventQueue
    # @D1EventQueue.setter
    # def D1EventQueue(self,val):
    #     self._D1EventQueue = val
    # 
    # @property
    # def D2EventQueue(self):
    #     return self._D2EventQueue
    # @D2EventQueue.setter
    # def D2EventQueue(self,val):
    #     self._D2EventQueue = val
    # 
    # @property
    # def D3EventQueue(self):
    #     return self._D3EventQueue
    # @D3EventQueue.setter
    # def D3EventQueue(self,val):
    #     self._D3EventQueue = val

    def Execution_Loop(self):
        global EXIT_PROGRAM
        while not EXIT_PROGRAM: # Enter loop
            if not D1_Lock.locked(): # Dongle 1
                self.RunNextInQueue(self.D1EventQueue)
                 # self.D1Curr_event = self.RunNextInQueue(self.D1EventQueue)
            if not D2_Lock.locked(): # Dongle 2
                self.D2Curr_event = self.RunNextInQueue(self.D2EventQueue)
            if not D3_Lock.locked(): # Dongle3
                self.D3Curr_event = self.RunNextInQueue(self.D3EventQueue)


    def append(self, function, lock_to_use, data):
        global Dongle_Selection, Hub_Dongle1, Hub_Dongle2, Hub_Dongle3

        if function == None:
            return None

        func_init = function

        # Set up thread to be run from queue.
        func_event_thread = threading.Thread(target = func_init,args = (lock_to_use,data,))

        # Event Item with function and the Priority from the function itself.
        func_event_item = Event_Item(func_event_thread)

        if Dongle_Selection is Hub_Dongle1:
            self.D1EventQueue = self.D1EventQueue + [func_event_item]
            return self.D1EventQueue

        elif Dongle_Selection is Hub_Dongle2:
            self.D2EventQueue = self.D2EventQueue + [func_event_item]
            return self.D2EventQueue

        elif Dongle_Selection is Hub_Dongle3:
            self.D1EventQueue = self.D3EventQueue + [func_event_item]
            return self.D3EventQueue

        return None

    def RunNextInQueue(self,queue):
        #queue = one of the dongle's queues.
        if len(queue) > 0:
            queued_func = queue.pop(0)
            queued_func.Event.start()
            queued_func.Event.join()
            return True
        else:
            return None



class Controller_Class:
    def __init__(self):
        logging.debug("\nPress Z at any time to quit\n"
              "Press R to refresh menu\n\n")
        self.CurrMenu = None
        self.ButtonScan = buttons_polling2.InputManagerObj()

    def GetInput(self):
        global EXIT_PROGRAM, Dongle_Selection
        x = "Z"
        self.CurrMenu.PrintMenu()
        while not EXIT_PROGRAM:
            while Ctrl_Lock.locked():
                continue

            # TODO : Remove Later
            time.sleep(0.1)
            if x != None:
                self.CurrMenu.PrintSocketMenu(SocketOutput)
            # SocketOutput.sendall(self.CurrMenu.displayState)

            self.ButtonScan.PollInput()   #Get input choice

            if self.ButtonScan.NewOutput == True:  #check for new output
                x = self.ButtonScan.SingleOutput
            else:
                x = None

            # Get command from the input choice.
            selected_command, data = Menu.ButtonToSelection(self.CurrMenu,x)

            task_lock = self.getTaskLock()

            Executer.append(selected_command,task_lock,data)

        # Shutdown
        Bluetooth.shutdown([], dongle_1=Hub_Dongle1, dongle_2=Hub_Dongle2, dongle_3=Hub_Dongle3)
        SocketOutput.sendall(b'End of line')

    def getTaskLock(self):
        global Dongle_Selection
        if Dongle_Selection == Hub_Dongle1:
            task_lock = D1_Lock
        elif Dongle_Selection == Hub_Dongle2:
            task_lock = D2_Lock
        elif Dongle_Selection == Hub_Dongle3:
            task_lock = D3_Lock
        else:  # Need a defualt or it will crash.
            task_lock = D1_Lock
        return task_lock

def InitializeAllDongles():
    global Hub_Dongle1,Hub_Dongle2,Hub_Dongle3
    Hub_Dongle1 = Bluetooth.HubDongle(D1_Lock, MAC_LIST[1])
    Hub_Dongle2 = Bluetooth.HubDongle(D2_Lock, MAC_LIST[2])
    Hub_Dongle3 = Bluetooth.HubDongle(D3_Lock, MAC_LIST[3])


def select_dongle1(lock,data):
    global Hub_Dongle1, Dongle_Selection
    data = None
    lock.acquire()
    Dongle_Selection = Hub_Dongle1
    SocketOutput.sendall(b'Selection:Dongle1')
    # logging.debug("Dongle 1 selected. Address = %s" %str(id(Dongle_Selection)))
    MenuTo_FunctionSelection()
    lock.release()
def select_dongle2(lock,data):
    global Hub_Dongle2, Dongle_Selection
    data = None
    lock.acquire()
    Dongle_Selection = Hub_Dongle2
    SocketOutput.sendall(b'Selection:Dongle2')
    # logging.debug("Dongle 2 selected. Address = %s" %str(id(Dongle_Selection)))
    SocketOutput.sendall(b"Dongle 2 selected.")
    MenuTo_FunctionSelection()
    lock.release()
def select_dongle3(lock,data):
    global Hub_Dongle3, Dongle_Selection
    data = None
    lock.acquire()
    Dongle_Selection = Hub_Dongle3
    SocketOutput.sendall(b'Selection:Dongle3')
    # logging.debug("Dongle 3 selected. Address = %s" %str(id(Dongle_Selection)))
    SocketOutput.sendall(b"Dongle 3 selected.")
    MenuTo_FunctionSelection()
    lock.release()

def Power_control(lock, data):
    lock.acquire()
    data = None
    # logging.debug("Power toggle")
    SocketOutput.sendall(b"Power toggle")
    MenuTo_PowerSelection()
    lock.release()
def Scan_control(lock, data):
    lock.acquire()
    data = None
    # logging.debug("Scan toggle")
    SocketOutput.sendall(b"Scan toggle")
    MenuTo_ScanSelection()
    lock.release()
def Media_controls(lock, data):
    lock.acquire()
    data = None
    # logging.debug("Media Controls")
    SocketOutput.sendall(b"Media Controls")
    MenuTo_MediaSelection()
    lock.release()
def BackTo_DongleSelect(lock, data):
    lock.acquire()
    data = None
    # logging.debug("Back to dongle select")
    SocketOutput.sendall(b"Back to dongle select")
    MenuTo_DongleSelection()
    lock.release()

def Power_on(lock, data):
    lock.acquire()
    global Dongle_Selection
    Dongle_Selection.power_on()
    data = None
    # print("Power on")
    # logging.debug("Back to Function Select")
    SocketOutput.sendall(b"Back to Function Select")
    MenuTo_FunctionSelection()
    lock.release()
def Power_backToFunctions(lock, data):
    # Combined power off and back button
    lock.acquire()
    global Dongle_Selection
    Dongle_Selection.power_off()
    data = None
    # logging.debug("Back to Function Select")
    SocketOutput.sendall(b"Back to Function Select")
    MenuTo_FunctionSelection()
    lock.release()

def Scan_on(lock, data):
    lock.acquire()
    global Dongle_Selection, Ctrl_Lock
    # TESTTEST

    global EXIT_PROGRAM, Controller
    Ctrl_Lock.acquire()

    while not EXIT_PROGRAM:
        Controller.ButtonScan.PollInput()
        if Controller.ButtonScan.NewOutput == True:
            x = Controller.ButtonScan.SingleOutput
            logging.debug(x)
        else:
            x = None
    # END OF TESTTEST

    if Dongle_Selection.Dongle.powered:
        Ctrl_Lock.acquire()
        logging.debug("Scan on")
        Dongle_Selection.discoverable_on()
        try :
            Dongle_Selection.Dongle.nearby_discovery(timeout=5) #Start Scan.
        except:
            pass
        Dongle_Selection.find_devices_in_adapter() #List pairable devices.

        Dongle_Selection.get_media_controls() # Get media controls.
        Dongle_Selection.get_Alias()
        Dongle_Selection.discoverable_off()
    else:
        logging.debug("Power is off. Can\'t start scan")
    data = None
    logging.debug("Scan stopped")
    if Ctrl_Lock.locked():
        Ctrl_Lock.release()
    MenuTo_ScanSelection()
    lock.release()

def Scan_backToFunctions(lock, data):
    lock.acquire()
    data = None
    logging.debug("Back to Function Select")
    MenuTo_FunctionSelection()
    lock.release()

def Media_Play(lock,data):
    lock.acquire()
    global Dongle_Selection
    Dongle_Selection.MediaControl.MediaController.Play()
    logging.debug("Play")
    lock.release()
def Media_Pause(lock,data):
    lock.acquire()
    global Dongle_Selection
    Dongle_Selection.MediaControl.MediaController.Pause()
    logging.debug("Pause")
    lock.release()
def Media_Prev(lock,data):
    lock.acquire()
    global Dongle_Selection
    Dongle_Selection.MediaControl.MediaController.Previous()
    logging.debug("Prev")
    lock.release()
def Media_Next(lock,data):
    lock.acquire()
    global Dongle_Selection
    Dongle_Selection.MediaControl.MediaController.Next()
    logging.debug("Next")
    lock.release()
def Media_VolDn(lock,data):
    lock.acquire()
    global Dongle_Selection
    logging.debug("VolDn")
    volume = Dongle_Selection.MediaControl.VolumeDown()
    logging.debug(volume)
    lock.release()
def Media_VolUp(lock, data):
    lock.acquire()
    global Dongle_Selection
    logging.debug("VolUp")
    volume = Dongle_Selection.MediaControl.VolumeUp()
    logging.debug(volume)
    lock.release()
def Media_backToFunctions(lock,data):
    lock.acquire()
    logging.debug("Back to Function Select")
    MenuTo_FunctionSelection()
    lock.release()


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
#         Define Globals
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
Ctrl_Lock = threading.Lock()
D1_Lock = threading.Lock()
D2_Lock = threading.Lock()
D3_Lock = threading.Lock()

# Thread Cancel flag
D1_Cancel = False
D2_Cancel = False
D3_Cancel = False

DONGLE_SELECT = b"DONGLE"
FUNCT_SELECT = b"FUNCT"
POWER_SELECT = b"POWER"
SCAN_SELECT = b"SCAN"
MEDIA_SEELCT = b"MEDIA"

Dongle_Selection_menu = Menu.Menu_listing(
    menu_entries.Dongle_select_msg,
    menu_entries.Dongle_select_choices,
    [select_dongle1, select_dongle2, select_dongle3],
    [None, None, None],
    DONGLE_SELECT)
def MenuTo_DongleSelection():
    global Controller
    Controller.CurrMenu = Dongle_Selection_menu

Function_Selection_menu = Menu.Menu_listing(
    menu_entries.Action_select_msg,
    menu_entries.Action_select_choices,
    [Power_control, Scan_control, Media_controls, BackTo_DongleSelect],
    [None, None, None, None],
    FUNCT_SELECT)
def MenuTo_FunctionSelection():
    global Controller
    Controller.CurrMenu = Function_Selection_menu

Power_menu = Menu.Menu_listing(
    menu_entries.Power_msg,
    menu_entries.Power_select,
    [Power_on, Power_backToFunctions],
    [None, None, None, None],
    POWER_SELECT)
def MenuTo_PowerSelection():
    global Controller
    Controller.CurrMenu = Power_menu

Scan_menu = Menu.Menu_listing(
    menu_entries.Scan_msg,
    menu_entries.Scan_select,
    [Scan_on, Scan_backToFunctions],
    [None, None],
    SCAN_SELECT)
def MenuTo_ScanSelection():
    global Controller
    Controller.CurrMenu = Scan_menu

Media_menu = Menu.Menu_listing(
    menu_entries.Media_control_msg,
    menu_entries.Media_control_select,
    [Media_Play,
     Media_Pause,
     Media_Prev,
     Media_Next,
     Media_VolDn,
     Media_VolUp,
     Media_backToFunctions],
    [None, None, None, None, None, None, None],
    MEDIA_SEELCT)
def MenuTo_MediaSelection():
    global Controller
    Controller.CurrMenu = Media_menu

def ExitChecker():
    global EXIT_PROGRAM
    while not EXIT_PROGRAM:
        message = input("Press enter to quit\n\n")
        if message == "Z":
            EXIT_PROGRAM = True
            break

def main():

    global Hub_Dongle1,Dongle_Selection, SocketOutput

    #Set up socket for output
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as SocketOutput:
        SocketOutput.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SocketOutput.connect((HOST,PORT))

        InitializeAllDongles()

        # Just to set as default.
        Dongle_Selection = Hub_Dongle1

        Controller.CurrMenu = Dongle_Selection_menu
        # Controller.CurrMenu = Function_Selection_menu

        # Set up threads
        Controller_Thread  = threading.Thread(target = Controller.GetInput)
        Executer_Thread    = threading.Thread(target = Executer.Execution_Loop)
        ExitChecker_Thread = threading.Thread(target = ExitChecker)

        Controller_Thread.start()
        Executer_Thread.start()
        ExitChecker_Thread.start()

        Controller_Thread.join()
        Executer_Thread.join()
        ExitChecker_Thread.join()



if __name__ == "__main__":
    logging.debug("Starting Program")
    main()
    logging.debug("Ending Program")
