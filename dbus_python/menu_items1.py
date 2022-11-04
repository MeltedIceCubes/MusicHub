#!/usr/bin/env python3.9
import menu_list4 as Menu
import config
# *********************************************************
# ***             Button Menu Definitions               ***
# *********************************************************
#           C1        C2        C3        C4        C5
#       ---------------------------------------------------
#  R1   |  Power  |  Media  | Connect |   Yes   |    No   |
#       |---------|---------|---------|---------|---------|
#  R2   |   Scan  | Devices |   Save  |         |   Back  |
#       |---------|---------|---------|---------|---------|
#  R3   |   Play  |  Pause  |   Prev  |   Next  |         |
#       ---------------------------------------------------


class M_Generic_Display_obj:
    """
            ***  Generic Display Menu Object ***
    """
    def __init__(self):
        self.thisDongle = None
        self.MenuEnabled = True
    def Pressed(self, ctrl):
        print("Running : %s" %self.__class__.__name__)
        config.PrintToSocket(r'*s0-K:*d2-Morris-Takamoto*s8-:K\r')
        return ctrl.CurrMenu
    def UpdateData(self, **data):
        if "Enable" in data:
            self.MenuEnabled = data["Enable"]
        print(self.MenuEnabled)
    def MakeDefR1Menu(self, **option):
        if "Powered" in option:
            # Power on case:
            if option["Powered"]:
                return Menu.MenuObj(
                    func1=config.M_R1_Power.Pressed,
                    func2=config.M_R1_Media.Pressed,
                    func3=config.M_R1_Connect.Pressed)
            # Power off case:
            elif not option["Powered"]:
                return Menu.MenuObj(
                    func1=config.M_R1_Power.Pressed)
    def MakeYesNoMenu(self):
        return Menu.MenuObj(func4=config.M_R1_Yes.Pressed, func5=config.M_R1_No.Pressed)
    def MakeDefR2Menu(self):
        return Menu.MenuObj(
            func1=config.M_R2_Scan.Pressed,
            func2=config.M_R2_Devices.Pressed,
            func3=config.M_R2_Save.Pressed,
            func5=config.M_R2_Back.Pressed, )


class M_R1_Power_class(M_Generic_Display_obj):
    """
            ***  Power Menu Object  ***
    Resp:
     - Toggle Power for current bluetooth object
    """
    def __init__(self):
        super().__init__()

    def Pressed(self, ctrl):
        config.PrintToSocket(r'*d0-Power On?\r')
        return self.Set_YesNoMenu()

    def Set_YesNoMenu(self):
        config.M_R1_Yes.Function = config.BtController.Curr_Dongle.Power_On
        config.M_R1_Yes.NextMenu = self.MakeDefR1Menu(Powered = True)
        config.M_R1_No.Function  = config.BtController.Curr_Dongle.Power_Off
        config.M_R1_No.NextMenu  = self.MakeDefR1Menu(Powered = False)
        return self.MakeYesNoMenu()

class M_R1_Media_class(M_Generic_Display_obj):
    """
            ***  Media Menu Object  ***
    Resp:
     - Give access to Media controls for current bluetooth object
    """

    def Pressed(self, ctrl):
        config.PrintToSocket(r'*d0-Media Mode\r')
        return ctrl.CurrMenu
class M_R1_Connect_class(M_Generic_Display_obj):
    """
            ***  Connect Menu Object  ***
    Resp:
     - Change menu to Connection-Mode
    """
    def __init__(self):
        super().__init__()
    def Pressed(self, ctrl):
        config.PrintToSocket(r'*d0-Connect Menu\r')
        config.M_R2_Back.NextMenu =  self.MakeDefR1Menu(
            Powered = config.BtController.Curr_Dongle.Power_Check())
        return self.MakeDefR2Menu()

class M_R1_Yes_class(M_Generic_Display_obj):
    """
            ***  Yes Menu Object  ***
    Resp:
     - Adapt to other menu's needs to respond to prompts
    """
    def __init__(self):
        super().__init__()
        self.NextMenu = None
        self.Function = None
    def Pressed(self,ctrl):
        config.PrintToSocket(r'*s0-Yes\r')
        self.Function()
        self.Function = None
        return self.NextMenu
class M_R1_No_class(M_Generic_Display_obj):
    """
            ***  No Menu Object  ***
    Resp:
     - Adapt to other menu's needs to respond to prompts
    """
    def __init__(self):
        super().__init__()
        self.NextMenu = None
        self.Function = None
    def Pressed(self,ctrl):
        config.PrintToSocket(r'*s0-No\r')
        self.Function()
        self.Function = None
        return self.NextMenu
class M_R2_Scan_class(M_Generic_Display_obj):
    """
            ***  Scan Menu Object  ***
    Resp:
     - Start scan when pressed
     - ? Twist encoder to change scan time
    """
    def __init__(self):
        super().__init__()
    def Pressed(self,ctrl):
        config.PrintToSocket(r'*d0-Scanning\r')
        config.BtController.Curr_Dongle.Scan_On()
        config.PrintToSocket(r'*d0-Scan Over\r')
        return ctrl.CurrMenu

class M_R2_Devices_class(M_Generic_Display_obj):
    """
            ***  Device Menu Object  ***
    Resp:
     - Show avaliable devices (After scan or whitelist)
    """
    def __init__(self, ):
        super().__init__()
    def Pressed(self, ctrl):
        # Refresh list
        config.BtController.Curr_Dongle.find_connectable_devices()
        # Make  list of connectable devices for encoder selection
        config.M_Encoder = M_Device_List_Encoder_obj()
        config.M_Encoder.devlist = list(config.BtController.Curr_Dongle.device_list)
        config.M_Encoder.printFirstDev()
        config.M_R2_Back.NextMenu = self.MakeDefR2Menu()
        return self.MakeDeviceMenu()
    def MakeDeviceMenu(self):
        return Menu.MenuObj(
            func5  = config.M_R2_Back.Pressed,
            funcEC = config.M_Encoder.PressedEC,
            funcCW = config.M_Encoder.PressedCW,
            funcCCW= config.M_Encoder.PressedCCW)



class M_R2_Save_class(M_Generic_Display_obj):
    """
            ***  Save Menu Object  ***
    Resp:
     - Path : Connect->Devices->Save
         - Guide user to save device to whitelist
         - Guide user to delete device from whitelist
     - Path : Connect->Save
         - Show saved devices
         - Guide user to delete device from whitelist
    """
    def __init__(self):
        super().__init__()
class M_R2_Back_class(M_Generic_Display_obj):
    """
            ***  Back Menu Object  ***
    Resp:
     - Adapt to other menu's needs to respond to prompts
    """
    def __init__(self):
        super().__init__()
        self.NextMenu = None
    def Pressed(self,ctrl):
        config.PrintToSocket(r'*s0-Going Back\r')
        return self.NextMenu

class M_R3_Play_class(M_Generic_Display_obj):
    """
            ***  Play Menu Object  ***
    Resp:
     - Media device play control
    """
    def __init__(self):
        super().__init__()

class M_R3_Pause_class(M_Generic_Display_obj):
    """
            ***  Pause Menu Object  ***
    Resp:
     - Media device pause control
    """
    def __init__(self):
        super().__init__()

class M_R3_Prev_class(M_Generic_Display_obj):
    """
            ***  Prev Menu Object  ***
    Resp:
     - Media device previous control
    """
    def __init__(self):
        super().__init__()

class M_R3_Next_class(M_Generic_Display_obj):
    """
            ***  Next Menu Object  ***
    Resp:
     - Media device next control
    """
    def __init__(self):
        super().__init__()

class M_Generic_Encoder_obj:
    """
            ***  Generic Encoder Menu Object ***
    """
    def __init__(self):
        self.thisDongle = None
        self.EC_func = None
        self.CW_func = None
        self.CCW_func = None
        self.EC_Enabled = True
        self.CW_Enabled = True
        self.CCW_Enabled = True
    def UpdateData(self, **data):
        if "EnableEC" in data:
            self.EC_Enabled = data["EnableEC"]
        if "EnableCW" in data:
            self.CW_Enabled = data["EnableCW"]
        if "EnableCCW" in data:
            self.CW_Enabled = data["EnableCCW"]
    def PressedEC(self,ctrl):
        if self.EC_func is not None:
            self.EC_func()
        return ctrl.CurrMenu
    def PressedCW(self,ctrl):
        if self.CW_func is not None:
            self.CW_func()
        return ctrl.CurrMenu
    def PressedCCW(self,ctrl):
        if self.CCW_func is not None:
            self.CCW_func()
        return ctrl.CurrMenu


class M_Device_List_Encoder_obj(M_Generic_Encoder_obj):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.devlist = []
    def PressedEC(self,ctrl):
        return ctrl.CurrMenu
    def PressedCW(self,ctrl):
        if len(self.devlist) == 0:
            return ctrl.CurrMenu
        elif self.index < (len(self.devlist)-1):
            self.index += 1
        config.PrintToSocket(r'*s0-%s/%s:*d3-%s\r' % (
                            self.index+1,
                            len(self.devlist),
                            self.devlist[self.index].properties["Name"]))
        return ctrl.CurrMenu
    def PressedCCW(self,ctrl):
        if len(self.devlist) == 0:
            return ctrl.CurrMenu
        elif self.index > 0:
            self.index -= 1
        config.PrintToSocket(r'*s0-%s/%s:*d3-%s\r' % (
                            self.index+1,
                            len(self.devlist),
                            self.devlist[self.index].properties["Name"]))
        return ctrl.CurrMenu
    def printFirstDev(self):
        if len(self.devlist) == 0:
            pass
        else:
            config.PrintToSocket(r'*s0-%s/%s:*d3-%s\r' % (
                self.index + 1,
                len(self.devlist),
                self.devlist[0].properties["Name"]))


config.M_R1_Power   = M_R1_Power_class()
config.M_R1_Media   = M_R1_Media_class()
config.M_R1_Connect = M_R1_Connect_class()
config.M_R1_Yes     = M_R1_Yes_class()
config.M_R1_No      = M_R1_No_class()

config.M_R2_Scan    = M_R2_Scan_class()
config.M_R2_Devices = M_R2_Devices_class()
config.M_R2_Save    = M_R2_Save_class()
config.M_R2_Back    = M_R2_Back_class()

config.M_R3_Play    = M_R3_Play_class()
config.M_R3_Pause   = M_R3_Pause_class()
config.M_R3_Prev    = M_R3_Prev_class()
config.M_R3_Next    = M_R3_Next_class()

config.M_Encoder    = M_Device_List_Encoder_obj()
# AAA000 = Menu.MenuObj(func1     = config.M_R1_Power.Pressed,
#                       func2     = config.M_R1_Media.Pressed,
#                       func3     = config.M_R1_Connect.Pressed,
#                       func4     = config.M_R1_Yes.Pressed,
#                       func5     = config.M_R1_No.Pressed,
#                       funcEC    = config.M_Encoder.selectIndex,
#                       funcCW    = config.M_Encoder.increaseIndex,
#                       funcCCW   = config.M_Encoder.decreaseIndex)
#No Power Menu
AAA000 = Menu.MenuObj(func1     = config.M_R1_Power.Pressed,
                      func2     = None,
                      func3     = None,
                      func4     = None,
                      func5     = None,
                      funcEC    = None,
                      funcCW    = None,
                      funcCCW   = None)