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
    def __init__(self, message, selection_options, selection_map):
        self.message = message
        self.options = selection_options
        self.functions = selection_map

    def PrintMenu(self):
        for i in self.message:
            print(i)

# *************************************
#    ***     Message Parsing     ***
# _____________________________________
def ParseSelection(menu_obj: Menu_listing, selection) -> list:
    """ Return : [index of selection]
                 None if failed. """
    menu_selection_index = []
    if selection:

        # Identify the selections
        for i in range(len(selection)):
            try:
                # Find index of the char.
                menu_selection_index.append(menu_obj.options[i].index(selection[i]))
            except:
                return None
        try: # Get the command that the index points to.
            selected_function = menu_obj.functions
            for i in menu_selection_index:
                selected_function = selected_function[i]

            return selected_function
        except:
            return None
        
    else:
        return None

class eventA1:
    def __init__(self, priority = 1):
        self.hold = True
        self.Priority = priority
        self.EventName = "A1"
    def run(self,lock):
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
    def __init__(self, priority = 2):
        self.hold = False
        self.Priority = priority
    def run(self):
        global CANCEL_FLAG
        print("A2 event")
        for i in range(5, 0, -1):
            if CANCEL_FLAG == True:
                CANCEL_FLAG = False
                break
            print(i)
            time.sleep(1)
        print("Finished : A2 event")

class eventB1:
    def __init__(self, priority = 3):
        self.hold = False
        self.Priority = priority
    def run(self):
        global CANCEL_FLAG
        print("B1 event")
        for i in range(5, 0, -1):
            if CANCEL_FLAG == True:
                CANCEL_FLAG = False
                break
            print(i)
            time.sleep(1)

        print("Finished : B1 event")

class eventB2:
    def __init__(self, priority = 4 ):
        self.hold = False
        self.Priority = priority
    def run(self):
        global CANCEL_FLAG
        print("B2 event")
        for i in range(5, 0, -1):
            if CANCEL_FLAG == True:
                CANCEL_FLAG = False
                break
            print(i)
            time.sleep(1)
        print("Finished : B2 event" )

# class Cancel_Event
if __name__ == "__main__":
    x = eventA1().run()
