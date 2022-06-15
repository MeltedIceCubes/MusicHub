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
    def __init__(self,msg,select,priority,functions,data):
        self.message    = msg
        self.options    = select
        self.priority   = priority
        self.functions  = functions
        self.data       = data
    def PrintMenu(self):
        for i in self.message:
            print(i)


# *************************************
#    ***     Message Parsing     ***
# _____________________________________
def ParseSelection(menu_obj: Menu_listing, selection) -> list:
    """ Return : [index of selection]
                 None if failed. """
    sel_index = None
    if selection:
        # Identify the selections
        try:
            # Find index of the char.
            sel_index=  menu_obj.options.index(selection[0])
        except:
            print("Invalid selection")
            return None, None, None
        try:  # Get the command that the index points to.
            selected_function = menu_obj.functions[sel_index]
            function_priority = menu_obj.priority[sel_index]
            function_data = menu_obj.data[sel_index]
            return selected_function, function_data, function_priority
        except:
            print("No command with that input")
            return None, None, None

    else:
        print("No input")
        return None, None, None


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
    pass
    x = eventA1().run()
