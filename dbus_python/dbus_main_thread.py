import dbus_Bluetooth7 as bluez_dbus
import menu_list as menu
import time
import threading



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
            if x == "Z":
                print("Stopped at : %d" %(time.time() * 1000))
                break

            menu_choice = self.MenuIfc.MenuFunctions    #load up the menu choice methods
            selection = self.MenuIfc.MenuMethods.ParseSelection(x) #
            if not selection:
                print("[%s] is not a valid input.\nTry again" %x)
                continue
            for i in selection:
                menu_choice = menu_choice[i]
            selection_exe    = menu_choice()
            selection_thread = threading.Thread(target=selection_exe.run)
            selection_thread.start()
            if selection_exe.hold == True:
                selection_thread.join()



class eventA1:
    def __init__(self):
        self.hold = True
    def run(self):
        print("A1 event")
        for i in range(3, 0, -1):
            print(i)
            time.sleep(1)
class eventA2:
    def __init__(self):
        self.hold = False
    def run(self):
        print("A2 event")
        for i in range(3, 0, -1):
            print(i)
            time.sleep(1)

class eventB1:
    def __init__(self):
        self.hold = False
    def run(self):
        print("B1 event")
        for i in range(3, 0, -1):
            print(i)
            time.sleep(1)
class eventB2:
    def __init__(self):
        self.hold = False
    def run(self):
        print("B2 event")
        for i in range(3, 0, -1):
            print(i)
            time.sleep(1)

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




BREAK_MAIN_LOOP = False
START_TIME = 0
Active_threads = []
UI_LOOP = UI_thread()  # global  object



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