import menu_messages as menu

# ********************************************
#   ***      Message and selections      ***
# ********************************************
# Selection has to be defined as an array containing two arrays.
#   This is to support multi-layered messages.
#       Ex. Selection:"A3"
#
DeviceSelect_message = ["Select Device",
                        "  1 : Input_1",
                        "  2 : Input_2",
                        "  3 : Output"]
DeviceSelect_selection  = [["1","2","3"]]

Initialize_message = [  "Initialize Dongle?",
                        "  1 : Yes",
                        "  2 : No"]
Initialize_selection =[["1","2","3"]]

Scan_message = ["Start Scan?",
                "  1 : Yes",
                "  2 : No"]
Scan_selection = [["1","2"]]


# ***********************************
# ***      Initialize Dongle      ***
# ***********************************
class Menu_listing:
    def __init__(self, message, selection_options):
        self.message = message
        self.options = selection_options

    def ParseSelection(self, selection):
        """this will return the index of the selection"""
        menu_selection_index = []
        for i in range(len(selection)):
            try:
                menu_selection_index.append(self.options[i].index(selection[i]))
            except:
                return None

        print(menu_selection_index)
        return menu_selection_index

    def PrintMenu(self):  # Print messages
        for menu in self.message:
            print(menu)

# Initialize_Menu = Menu_listing(Initialize_message, Initialize_selection)
Initialize_Menu = Menu_listing(menu.Initialize_message, menu.Initialize_selection)


if __name__ == "__main__":
    Initialize_Menu.PrintMenu()
    x = input()
    Initialize_Menu.ParseSelection(x)