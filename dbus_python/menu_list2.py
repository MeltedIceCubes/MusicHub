import time
import threading


# ********************************************
#   ***      Message and selections      ***
# ____________________________________________
# Selection has to be defined as an array containing two arrays.
#   This is to support multi-layered messages.
#       Ex. Selection:"A3"

class CancelCommandIssued(Exception):
    """@info Cancel Command was sent. Exit when possible."""
    pass


CANCEL_FLAG = False


class Menu_listing:
    def __init__(self, message, selection_options, selection_map, priority_map):
        self.message = message
        self.options = selection_options
        self.functions = selection_map
        self.priority = priority_map

    def PrintMenu(self):
        for i in self.message:
            print(i)


# *************************************
#    ***     Message Parsing     ***
# _____________________________________
def ParseSelection(menu_obj: Menu_listing, selection) -> list:
    """ Return : [index of selection]
                 None if failed. """
    menu_selection_index = None
    if selection:
        # Identify the selections
        try:
            # Find index of the char.
            menu_selection_index=  menu_obj.options.index(selection[0])
        except:
            print("Invalid selection")
            return None
        try:  # Get the command that the index points to.
            selected_function = menu_obj.functions[menu_selection_index]
            function_priority = menu_obj.priority[menu_selection_index]
            return selected_function, function_priority
        except:
            print("No command with that input")
            return None

    else:
        print("No input")
        return None


class eventA1:
    Priority = 1

    def __init__(self, priority=1):
        self.hold = True
        self.EventName = "A1"

    def run(self, lock):
        global CANCEL_FLAG
        lock.acquire()
        print("A1 event")
        for i in range(5, 0, -1):
            if CANCEL_FLAG == True:
                CANCEL_FLAG = False
                break
            print(i)
            time.sleep(1)
        lock.release()


class eventA2:
    Priority = 2

    def __init__(self, priority=2):
        self.hold = False

    def run(self, lock):
        global CANCEL_FLAG
        lock.acquire()
        print("A2 event")
        for i in range(5, 0, -1):
            if CANCEL_FLAG == True:
                CANCEL_FLAG = False
                break
            print(i)
            time.sleep(1)
        lock.release()


class eventB1:
    Priority = 3

    def __init__(self, priority=3):
        self.hold = False

    def run(self, lock):
        global CANCEL_FLAG
        lock.acquire()
        print("B1 event")
        for i in range(5, 0, -1):
            if CANCEL_FLAG == True:
                CANCEL_FLAG = False
                break
            print(i)
            time.sleep(1)
        lock.release()


class eventB2:
    Priority = 4

    def __init__(self, priority=4):
        self.hold = False

    def run(self, lock):
        global CANCEL_FLAG
        lock.acquire()
        print("B2 event")
        for i in range(5, 0, -1):
            if CANCEL_FLAG == True:
                CANCEL_FLAG = False
                break
            print(i)
            time.sleep(1)
        lock.release()


# class Cancel_Event
if __name__ == "__main__":
    x = eventA1().run()
