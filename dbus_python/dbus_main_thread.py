import dbus_Bluetooth7 as bluez_dbus
import menu_list as menu
import time
import threading

BREAK_MAIN_LOOP = False
START_TIME = 0
Active_threads = []

class SelectionMap:
    def __init__(self,menu_obj:menu.Menu_listing, function_list:list):
        self.MenuMethods = menu_obj
        self.MenuFunctions = function_list

class process:
    def __init__(self, sleep_time, name):
        self.sleep_time = sleep_time
        self.start_time = 0
        self.name = name
    def timer(self):
        self.start_time = 1000 * time.time()
        time.sleep(self.sleep_time)
        print("%s : %d -> %d" % (self.name, (self.start_time - START_TIME), (1000 * time.time() - START_TIME)))

class UI_thread:
    def __init__(self):
        print("Press Z at any time to quit\n\n")
        self.observers = []
        self.MenuIfc = None

    def waitForInput(self):
        while True:
            self.MenuIfc.MenuMethods.PrintMenu()
            x = input()
            selection = self.MenuIfc.MenuMethods.ParseSelection(x)
            menu_choice = self.MenuIfc.MenuFunctions
            for i in selection:
                menu_choice = menu_choice[i]
            menu_choice()


            # TODO: Make this accept the same dimension of inputs as the parser


            # for callback in self.observers:
            #     callback()

            if x == "Z":
                print("Stopped at : %d" %(time.time() * 1000))
                break

UI_LOOP = UI_thread()  # global class


def eventA():
    print("A event")
def eventA1():
    print("A1 event")
def eventA2():
    print("A2 event")
def eventB():
    print("B event")
def eventB1():
    print("B1 event")
def eventB2():
    print("B2 event")
def eventReset():
    print("Reset events")


Event_message = ['Select Event : ',
                 'A : ',
                 '     1',
                 '     2',
                 'B : ',
                 '     1',
                 '     2']
Event_selection = [['A','B'],['1','2']]

if __name__ == '__main__':
    print("Main Thread : Start")
    event_menu = menu.Menu_listing(Event_message,Event_selection)
    event_menu_obj = SelectionMap(event_menu, [[eventA1,eventA2], [eventB1, eventB2]])

    UI_LOOP.MenuIfc = event_menu_obj

    # UI_LOOP.observers.append()  # Register observers
    ui_thread = threading.Thread(target=UI_LOOP.waitForInput)
    ui_thread.start()

    ui_thread.join()
    print("\n\nMain Thread : End")
    # UI_thread()