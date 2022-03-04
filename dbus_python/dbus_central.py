from bluezero import central

central.Central()

MAC_LIST = ["00:1A:7D:DA:71:13",
            "00:1A:7D:DA:71:14",
            "00:1A:7D:DA:71:15",
            "DC:A6:32:92:BF:F5"]
AdapterList = list()
#Hub_Output = central.Central()
Hub_Input1 = central.Central(MAC_LIST[1])
#Hub_Input2 = central.Central()
#Pi_Dongle  = central.Central()

