# Todo :
# Main control thread
# Execution scheduler thread
# Dongle Thread class A
# Dongle Thread class B

import threading
import time
# from menu_list1 import Menu_listing, ParseSelection, eventA1, eventA2, eventB1,eventB2,CANCEL_FLAG
import menu_list1 as Menu
class Executer_Class:
    def __init__(self):
        self._function_to_run = None
        self._EventQueue = []
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
    def append(self,val):
        self.EventQueue = self.EventQueue + [val]
        return self.EventQueue
    def extend(self,val):
        return self.EventQueue.extend(val)

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
                break
            elif x == "X": # Cancel current thread
                Menu.CANCEL_FLAG = True
                continue

            # Get command from choice input
            selected_Command = Menu.ParseSelection(self.CurrMenu, x)

            if not selected_Command: # check if choice is valid
                print("[%s] is not a valid input.\nTry again" % x)
                continue

            Executer.function_to_run = (selected_Command)
            Executer.RunThread()
            # Executer.WaitThread()
            # command = selected_Command()
            # command.run()
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

    Controller_Thread.start()

    Controller_Thread.join()



if __name__ == "__main__":
    print(" Main Thread : Start\n\n")
    main()
    print("\n\n Main Thread : End")