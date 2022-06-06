# Todo :
# Main control thread
# Execution scheduler thread
# Dongle Thread class A
# Dongle Thread class B

import threading
import time
# from menu_list1 import Menu_listing, ParseSelection, eventA1, eventA2, eventB1,eventB2,CANCEL_FLAG
import menu_list1 as Menu

EXIT_PROGRAM = False
Executer_Lock = threading.Lock()
# Executer_Lock = threading.Lock()


class Event_Item:
    def __init__(self,passed_method, priority = 5, passed_args = None):
        self.Priority = priority
        self.Event = passed_method
        self.args = passed_args


class Executer_Class:
    def __init__(self):
        self._function_to_run = None
        self._EventQueue = []
        self.curr_event = None

    def Execution_Loop(self):
        global EXIT_PROGRAM
        while True:  # Start Loop
            if EXIT_PROGRAM == True: # Check for exit condition
                break

            if not Executer_Lock.locked(): # Check that other function is not running.
                self.curr_event = self.RunNextInQueue() # Pick and run the next in the event queue
            time.sleep(0.2) # Delete for real implementation

    @property
    def function_to_run(self):
        return self._function_to_run
    @function_to_run.setter
    def function_to_run(self, new_func):
        new_func_setup = new_func()
        new_func_thread= threading.Thread(target = new_func_setup.run)
        self._function_to_run = new_func_thread

    @property
    def EventQueue(self):
        return self._EventQueue
    @EventQueue.setter
    def EventQueue(self, val):
        self._EventQueue = val
    def append(self,function):
        func_init = function()
        func_event_thread = threading.Thread(target = func_init.run,args = (Executer_Lock,))
        func_event_item = Event_Item(func_event_thread,func_init.Priority)
        temp_EventQueue = self.EventQueue + [func_event_item]
        self.EventQueue = sorted(temp_EventQueue, key = lambda x : x.Priority)
        # self.EventQueue = self.EventQueue + [func_event_item]
        # z = sorted(x,key= lambda gg : gg.priority)
        return self.EventQueue

    def RunNextInQueue(self):
        if len(self.EventQueue) > 0:
            queued = self.EventQueue.pop(0)
            # queued = self.EventQueue[0]
            queued.Event.start()
            return queued.Event
        else:
            return None
    def RunThread(self):
        self._function_to_run.start()

    def WaitThread(self):
        self._function_to_run.join()


class Controller_Class:
    def __init__(self):
        print("Press Z at any time to quit\n\n")
        self.CurrMenu = None

    def GetInput(self):
        while True:
            self.CurrMenu.PrintMenu() #
            x = input()

            if x == "Z": # Exit condition
                EXIT_PROGRAM = True
                break
            elif x == "X": # Cancel current thread
                Menu.CANCEL_FLAG = True
                continue

            # Get command from choice input
            selected_Command = Menu.ParseSelection(self.CurrMenu, x)

            if not selected_Command: # check if choice is valid
                print("[%s] is not a valid input.\nTry again" % x)
                continue

            # Executer.function_to_run = (selected_Command)
            # Executer.RunThread()
            # Executer.WaitThread()
            Executer.append(selected_Command)


            print("Finished loop")

Controller = Controller_Class()
Executer = Executer_Class()

Test_Event_message = ['Select Event : ',
                 'A : ',
                 '     1',
                 '     2',
                 'B : ',
                 '     1',
                 '     2']
Test_Event_selection = [['A','B'],['1','2']]
Test_Event_map = [[Menu.eventA1,Menu.eventA2], [Menu.eventB1, Menu.eventB2]]


def main():
    # Make Menu listing object. This contains the selection details
    Test_Menu_listing = Menu.Menu_listing(Test_Event_message, Test_Event_selection, Test_Event_map)

    # Assign to current menu listing
    Controller.CurrMenu = Test_Menu_listing

    # Set up thread.
    Controller_Thread = threading.Thread(target = Controller.GetInput)
    Executer_Thread = threading.Thread(target = Executer.Execution_Loop)

    Controller_Thread.start()
    Executer_Thread.start()

    Controller_Thread.join()
    Executer_Thread.join()



if __name__ == "__main__":
    print(" Main Thread : Start\n\n")
    main()
    print("\n\n Main Thread : End")