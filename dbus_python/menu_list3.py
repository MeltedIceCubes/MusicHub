import time
import threading
import logging
logging.basicConfig(format = '%(message)s',level = logging.DEBUG)


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
    def __init__(self, msg, select, functions, data, state):
        self.message    = msg
        self.options    = select
        self.functions  = functions
        self.data       = data
        self.displayState = state

    def PrintMenu(self):  #For debugging
        for i in self.message:
            logging.debug("%s" %i)
    def PrintSocketMenu(self,socketObj):  #For socket communication
        for i in self.message:
            socketObj.sendall(i)


def ButtonToSelection(menu_obj:Menu_listing, selection):
    sel_index = None
    if selection:
        try:
            sel_index = menu_obj.options.index(selection)
        except:
            logging.debug("Invalid selection")
            return None, None
        try:  # Get the command that the index points to.
            selected_function = menu_obj.functions[sel_index]
            function_data = menu_obj.data[sel_index]
            return selected_function, function_data
        except:
            logging.debug("No command with that input")
            return None, None
    else: #No input
        return None, None


# UNUSED
def ParseSelection(menu_obj: Menu_listing, selection):
    """ Return : [index of selection]
                 None if failed. """
    sel_index = None
    if selection:
        # Identify the selections
        try:
            # Find index of the char.
            sel_index=  menu_obj.options.index(selection[0])
        except:
            logging.debug("Invalid selection")
            return None, None, None
        try:  # Get the command that the index points to.
            selected_function = menu_obj.functions[sel_index]
            function_priority = menu_obj.priority[sel_index]
            function_data = menu_obj.data[sel_index]
            return selected_function, function_data, function_priority
        except:
            logging.debug("No command with that input")
            return None, None, None

    else:
        logging.debug("No input")
        return None, None, None

if __name__ == "__main__":
    pass
    x = eventA1().run()
