# -*- coding: utf-8 -*-
"""
Control bluetoothctl with python using pexpect.
"""
import pexpect
import Bluetoothctl.btctlWrapper as btctl
import time
import re
import menu_messages as menu

# Mac Address defines
INPUT1 = "00:1A:7D:DA:71:15"
INPUT2 = "00:1A:7D:DA:71:14"
OUTPUT = "00:1A:7D:DA:71:13"

class agent:
    def __init__(self, macAdd):
        self.macAdd = macAdd
        self.btCtrl =btctl.Bluetoothctl()
        

def select_to_command(agent,selection):
    if selection == 1:    # Agent off
        agent.agent_off()
        print("Agent off")
    elif selection ==2:   # Power off
        pass
    elif selection ==3:   # Agent NoInputNoOutput
        pass
    elif selection ==4:   # default-agent
        pass
    elif selection ==5:   # power on 
        pass
    elif selection ==6:   # discoverable on 
        pass
    elif selection ==7:   # pairable on
        pass
    elif selection ==8:   # Authorize service...
        pass
    elif selection ==9:   # connect ... 
        pass
    else: #Selection doesn't exist
        pass
    
if __name__ =="__main__":
    #********************
    #   Start Sequence
    #********************
    print("Init Bluetooth")
    bl = btctl.Bluetoothctl()
    start_sts = bl.clear_start()
    print("Ready!")
    bl.agent_off()
    
    
    #*****************************
    #   Select Bluetooth Module   
    #*****************************
    
    print("Select module") 
    
    
    
    select = bl.select_device("00:1A:7D:DA:71:15")
    
    
    
    #try:
    #    out = bl.get_output("select " + OUTPUT, 1)
    #except BluetoothctlError as e:
    #    pass
    #else:
    #    for line in out:
    #        line = line.decode("utf-8")
    #        res = re.match("Agent\sregistered",line)
    #        if res == None:
    #            print("No match found")
    #        else:
    #            print(res.group())
    #   success = True if res == 1 else False



#   *********************
#   ***   Code Dump   ***
#   *********************


#child = pexpect.spawn('bluetoothctl',encoding='utf-8',timeout = 1,echo = False)
#child.send("agent off" + "\n")
##words = child.expect(["bluetooth",pexpect.EOF])
#words = child.expect("\[bluetooth\]")
#print(child.before)
#print(child.after)
#   *********************
#   ***   Resources   ***
#   *********************
#  API : https://pexpect.readthedocs.io/en/stable/api/pexpect.html
#  Example code : https://gist.github.com/egorf/66d88056a9d703928f93
#  