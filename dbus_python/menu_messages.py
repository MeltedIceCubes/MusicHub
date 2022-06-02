""" Selection has to be defined as an array containing two arrays.
    This is to support multi-layered messages.
        Ex. Selection:"A3"
"""

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


