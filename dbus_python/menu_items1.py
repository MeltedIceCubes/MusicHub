#!/usr/bin/env python3.9
import menu_list4 as Menu
import config
import logging
import time
logging.basicConfig(format = '%(message)s',level = logging.DEBUG)
# *********************************************************
# ***             Button Menu Definitions               ***
# *********************************************************
#           C1        C2        C3        C4        C5
#       ---------------------------------------------------
#  R1   |  Power  |  Media  | Connect |  Yes    |   No    |
#       |---------|---------|---------|---------|---------|
#  R2   |  Scan   | Devices |         | Delete  |  Back   |
#       |---------|---------|---------|---------|---------|
#  R3   |  Prev   |  Play   |  Next   |         |         |
#       ---------------------------------------------------


class M_Generic_Display_obj:
    """
            ***  Generic Display Menu Object ***
    """
    def __init__(self):
        self.MenuEnabled = True
    def Pressed(self, ctrl):
        print("Running : %s" %self.__class__.__name__)
        config.PrintToSocket(r'*s0-K:*d2-Morris-Takamoto*s8-:K\r')
        return ctrl.CurrMenu
    def UpdateData(self, **data):
        if "Enable" in data:
            self.MenuEnabled = data["Enable"]
        print(self.MenuEnabled)
    def MakeDefR1Menu(self):
        if config.BtController.Curr_Dongle.Power_Check(): #Powered On case
            config.M_Encoder = M_Dongle_Select_Encoder_obj()
            return Menu.MenuObj(
                func1=config.M_R1_Power.Pressed,
                func2=config.M_R1_Media.Pressed,
                func3=config.M_R1_Connect.Pressed,
                funcEC=config.M_Encoder.PressedEC,
                funcCW=config.M_Encoder.PressedCW,
                funcCCW=config.M_Encoder.PressedCCW)
        else:
            config.M_Encoder = M_Dongle_Select_Encoder_obj()
            return Menu.MenuObj(
                func1=config.M_R1_Power.Pressed,
                funcEC=config.M_Encoder.PressedEC,
                funcCW=config.M_Encoder.PressedCW,
                funcCCW=config.M_Encoder.PressedCCW)

    def MakeDefR2Menu(self):
        return Menu.MenuObj(
            func1=config.M_R2_Scan.Pressed,
            func2=config.M_R2_Devices.Pressed,
            func4=config.M_R2_Delete.Pressed,
            func5=config.M_R2_Back.Pressed,)
    def MakeYesNoMenu(self):
        return Menu.MenuObj(func4=config.M_R1_Yes.Pressed, func5=config.M_R1_No.Pressed)

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
        logging.debug("|         |         |         |   Yes   |   No    |")
        return self.Set_YesNoMenu()

    def Set_YesNoMenu(self):
        config.M_R1_Yes.Function = config.BtController.Curr_Dongle.Power_On
        config.M_R1_Yes.NextMenu = self.MakeDefR1Menu
        config.M_R1_No.Function  = config.BtController.Curr_Dongle.Power_Off
        config.M_R1_No.NextMenu  = self.MakeDefR1Menu
        return self.MakeYesNoMenu()

class M_R1_Media_class(M_Generic_Display_obj):
    """
            ***  Media Menu Object  ***
    Resp:
    - Give access to Media controls for current bluetooth object
    """

    def Pressed(self, ctrl):
        config.BtController.Curr_Dongle.get_media_controls()
        if config.BtController.Curr_Dongle.MediaControl.MediaController == None:
            print("No Media Controller")
        if config.BtController.Curr_Dongle.MediaControl.MediaPlayer == None:
            print("No Media Player")
        if config.BtController.Curr_Dongle.MediaControl.MediaTransporter == None:
            print("No Media Transport")
        config.PrintToSocket(r'*d0-Media Mode\r')
        logging.debug("|  Prev  |Play/Pause| Next    |         |  Back   |")
        return self.MakeMediaMenu()
    def MakeMediaMenu(self):
        config.M_R2_Back.NextMenu.append(self.MakeDefR1Menu)
        config.M_Encoder = M_Media_Control_Encoder_obj()
        return Menu.MenuObj(
            func1  = config.M_R3_Prev.Pressed,
            func2  = config.M_R3_Plause.Pressed,
            func3  = config.M_R3_Next.Pressed,
            func5  = config.M_R2_Back.Pressed,
            funcEC = config.M_Encoder.PressedEC,
            funcCW = config.M_Encoder.PressedCW,
            funcCCW= config.M_Encoder.PressedCCW)

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
        logging.debug("|  Scan   | Devices |         | Delete  |  Back   |")
        config.M_R2_Back.NextMenu.append(self.MakeDefR1Menu)
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
        return self.NextMenu()

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
        logging.debug("|  Scan   | Devices |         | Delete  |  Back   |")
        return ctrl.CurrMenu

class M_R2_Devices_class(M_Generic_Display_obj):
    """
            ***  Device Menu Object  ***
    Resp:
    - Show avaliable devices (After scan or whitelist)
    """
    def __init__(self):
        super().__init__()
    def Pressed(self, ctrl):
        # Refresh list
        config.BtController.Curr_Dongle.find_connectable_devices()
        # Make  list of connectable devices for encoder selection
        config.M_Encoder = M_Device_List_Encoder_obj()
        config.M_Encoder.devlist = list(config.BtController.Curr_Dongle.device_list)
        config.M_Encoder.Devices_printFirstDev()
        config.M_R2_Back.ResetNextMenus()
        config.M_R2_Back.NextMenu.append(self.MakeDefR2Menu)
        config.M_R2_Back.NextMenu.append(self.MakeDefR1Menu)
        logging.debug("|         |         |         |         |  Back   | EClick = Select")
        return self.MakeDeviceMenu()
    def MakeDeviceMenu(self):
        return Menu.MenuObj(
            func5  = config.M_R2_Back.Pressed,
            funcEC = config.M_Encoder.PressedEC,
            funcCW = config.M_Encoder.PressedCW,
            funcCCW= config.M_Encoder.PressedCCW)

class M_R2_Delete_class(M_Generic_Display_obj):
    """
            ***  Delete Menu Object  ***
    Resp:
    - Path : Connect->Devices->Delete
        - Guide user to deleet device from whitelist
    """
    def __init__(self):
        super().__init__()
    def Pressed(self, ctrl):
        config.BtController.Curr_Dongle.find_connectable_devices()
        if len(config.BtController.Curr_Dongle.device_list) == 0:
            config.PrintToSocket(r'*s0-No Devices\r')
            time.sleep(0.4)
            return ctrl.CurrMenu
        else:
            config.M_Encoder = M_Delete_List_Encoder_obj()
            config.M_Encoder.devlist = list(config.BtController.Curr_Dongle.device_list)
            config.M_Encoder.Devices_printFirstDev()
            config.M_R2_Back.ResetNextMenus()
            config.M_R2_Back.NextMenu.append(self.MakeDefR2Menu)
            config.M_R2_Back.NextMenu.append(self.MakeDefR1Menu)
            logging.debug("|         |         |         |         |  Back   | EClick = Select")
            return self.MakeDeviceMenu()
    def MakeDeviceMenu(self):
        return Menu.MenuObj(
            func5=config.M_R2_Back.Pressed,
            funcEC=config.M_Encoder.PressedEC,
            funcCW=config.M_Encoder.PressedCW,
            funcCCW=config.M_Encoder.PressedCCW)

class M_R2_Back_class(M_Generic_Display_obj):
    """
            ***  Back Menu Object  ***
    Resp:
    - Adapt to other menu's needs to respond to prompts
    """
    def __init__(self):
        super().__init__()
        self.NextMenu = list()

    def Pressed(self,ctrl):
        config.PrintToSocket(r'*s0-Going Back\r')
        try:
            Next_Menu = self.NextMenu.pop(0)()
        except IndexError:
            Next_Menu = ctrl.CurrMenu
        return Next_Menu
    def ResetNextMenus(self):
        self.NextMenu = list()

class M_R3_Play_class(M_Generic_Display_obj):
    """
            ***  Play Menu Object  ***
    Resp:
    - Media device play control
    """
    def __init__(self):
        super().__init__()
    def Pressed(self, ctrl):
        config.BtController.Curr_Dongle.MediaControl.Play_Media()
        return ctrl.CurrMenu

class M_R3_Pause_class(M_Generic_Display_obj):
    """
            ***  Pause Menu Object  ***
    Resp:
    - Media device pause control
    """
    def __init__(self):
        super().__init__()

    def Pressed(self, ctrl):
        config.BtController.Curr_Dongle.MediaControl.Pause_Media()
        return ctrl.CurrMenu

class M_R3_Plause_class(M_Generic_Display_obj):
    """
            ***  Play/Pause Menu Object  ***
    Resp:
    - Media device play/pause control
    """

    def __init__(self):
        super().__init__()

    def Pressed(self, ctrl):
        config.BtController.Curr_Dongle.MediaControl.Plause_Media()
        return ctrl.CurrMenu

class M_R3_Prev_class(M_Generic_Display_obj):
    """
            ***  Prev Menu Object  ***
    Resp:
    - Media device previous control
    """
    def __init__(self):
        super().__init__()
    def Pressed(self, ctrl):
        config.BtController.Curr_Dongle.MediaControl.Prev_Media()
        return ctrl.CurrMenu

class M_R3_Next_class(M_Generic_Display_obj):
    """
            ***  Next Menu Object  ***
    Resp:
    - Media device next control
    """
    def __init__(self):
        super().__init__()
    def Pressed(self, ctrl):
        config.BtController.Curr_Dongle.MediaControl.Next_Media()
        return ctrl.CurrMenu

class M_Generic_Encoder_obj:
    """
            ***  Generic Encoder Menu Object ***
    """
    def __init__(self):
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

class M_Dongle_Select_Encoder_obj(M_Generic_Encoder_obj):
    def __init__(self,):
        super().__init__()
        self.defaultIndex = 3
        self.Dongle1Dict = {"index" : 3,
                            "DongleTarget" : config.BtController.Hub_Dongle1}
        self.Dongle2Dict = {"index" : 6,
                            "DongleTarget" : config.BtController.Hub_Dongle2}
        self.Dongle3Dict = {"index" : 9,
                            "DongleTarget" : config.BtController.Hub_Dongle3}
        self.DongleDictList =  [self.Dongle1Dict,
                                self.Dongle2Dict,
                                self.Dongle3Dict]
        self.index = None
        self.CheckStartIndex()
    def PressedEC(self,ctrl):
        for Dongle in self.DongleDictList:
            if self.index == Dongle["index"]:
                # print("Found Dongle for index")
                config.BtController.Curr_Dongle = Dongle["DongleTarget"]
                print(config.BtController.Curr_Dongle.Name)
                break
            else: 
                pass
        return ctrl.CurrMenu
    def PressedCW(self,ctrl):
        if self.index >=23:
            self.index = 0
        else:
            self.index += 1
        config.PrintToSocket(r'*s0-%s/23\r' %str(self.index))
        return ctrl.CurrMenu
    def PressedCCW(self,ctrl):
        if self.index <= 0:
            self.index = 23
        else:
            self.index -= 1
        config.PrintToSocket(r'*s0-%s/23\r' % str(self.index))
        return ctrl.CurrMenu
    def CheckStartIndex(self):
        for Dongle in self.DongleDictList:
            if config.BtController.Curr_Dongle == Dongle["DongleTarget"]:
                self.index = Dongle["index"]
                return
        self.index = self.defaultIndex
        return


class M_Device_List_Encoder_obj(M_Generic_Encoder_obj):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.devlist = []
    def PressedEC(self,ctrl): #Connct to indexed device
        config.PrintToSocket(r'*d0-Pairing to : %s\r' % self.devlist[self.index].properties["Name"])
        result = config.BtController.Curr_Dongle.pair_and_connect(self.devlist[self.index])
        if not result:
            config.PrintToSocket(r'*d0-Failed Pairing : %s\r' %self.devlist[self.index].properties["Name"])
        elif result:
            config.PrintToSocket(r'*d0-Paired : %s\r' % self.devlist[self.index].properties["Name"])
        return config.M_R2_Devices.MakeDefR2Menu()
    def PressedCW(self,ctrl): #Increase indexPaired :
        if len(self.devlist) == 0:
            return ctrl.CurrMenu
        elif self.index < (len(self.devlist)-1):
            self.index += 1
        config.PrintToSocket(r'*s0-%s/%s:*d4-%s\r' % (
                            self.index+1,
                            len(self.devlist),
                            self.devlist[self.index].properties["Name"]))
        return ctrl.CurrMenu
    def PressedCCW(self,ctrl): #Decrease index
        if len(self.devlist) == 0:
            return ctrl.CurrMenu
        elif self.index > 0:
            self.index -= 1
        config.PrintToSocket(r'*s0-%s/%s:*d4-%s\r' % (
                            self.index+1,
                            len(self.devlist),
                            self.devlist[self.index].properties["Name"]))
        return ctrl.CurrMenu
    def Devices_printFirstDev(self):
        if len(self.devlist) == 0:
            pass
        else:
            config.PrintToSocket(r'*s0-%s/%s:*d4-%s\r' % (
                self.index + 1,
                len(self.devlist),
                self.devlist[0].properties["Name"]))
    # def NoDevices(self):
    #     if len(self.devlist) == 0:
        

class M_Delete_List_Encoder_obj(M_Device_List_Encoder_obj):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.devlist = []
    def PressedEC(self, ctrl):
        config.PrintToSocket(r'*s0-Del?:*d5-%s\r' % self.devlist[self.index].properties["Name"])
        # Go to Yes/No Menu
        
        # Yes-> Actually delete.
        # No-> go back to Connect menu.
        return self.Set_YesNoMenu()
    def PressedCW(self,ctrl):
        return super().PressedCW(ctrl)

    def PressedCCW(self, ctrl):
        return super().PressedCW(ctrl)
    # def PressedCCW(self,ctrl):
    # def Devices_printFirstDev(self):
    def Set_YesNoMenu(self):
        config.M_R1_Yes.Function = self.Delete_Device
        config.M_R1_Yes.NextMenu = self.MakeDefR2Menu
        config.M_R1_No.Function  = self.DoNothing
        config.M_R1_No.NextMenu  = self.MakeDefR2Menu
        return Menu.MenuObj(func4=config.M_R1_Yes.Pressed, func5=config.M_R1_No.Pressed)
    def Delete_Device(self): # for Yes
        object_path = self.devlist[self.index].deviceObj.object_path
        try:
            config.BtController.Curr_Dongle.Dongle.remove_device(object_path)
            logging.debug("Removed %s" %object_path)
        except:
            logging.debug("Failed to remove %s" % object_path)
    # Dongle..remove_device(straggler)
    def DoNothing(self): # for No
        pass
    def MakeDefR2Menu(self):
        return Menu.MenuObj(func1=config.M_R2_Scan.Pressed,
                            func2=config.M_R2_Devices.Pressed,
                            func4=config.M_R2_Delete.Pressed,
                            func5=config.M_R2_Back.Pressed,)


class M_Media_Control_Encoder_obj(M_Generic_Encoder_obj):
    def __init__(self):
        super().__init__()
    def PressedEC(self,ctrl):
        config.BtController.Curr_Dongle.MediaControl.VolMute_Media()
        return ctrl.CurrMenu
    def PressedCW(self,ctrl):
        config.BtController.Curr_Dongle.MediaControl.VolUp_Media()
        return ctrl.CurrMenu
    def PressedCCW(self,ctrl):
        config.BtController.Curr_Dongle.MediaControl.VolDn_Media()
        return ctrl.CurrMenu

def InitMenus():
    config.M_R1_Power   = M_R1_Power_class()
    config.M_R1_Media   = M_R1_Media_class()
    config.M_R1_Connect = M_R1_Connect_class()
    config.M_R1_Yes     = M_R1_Yes_class()
    config.M_R1_No      = M_R1_No_class()

    config.M_R2_Scan    = M_R2_Scan_class()
    config.M_R2_Devices = M_R2_Devices_class()
    config.M_R2_Delete  = M_R2_Delete_class()
    config.M_R2_Back    = M_R2_Back_class()

    config.M_R3_Plause  = M_R3_Plause_class()
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
    # AAA000 = M_Generic_Display_obj().MakeDefR1Menu(Powered = False)
        #
        # Menu.MenuObj(func1     = config.M_R1_Power.Pressed,
        #                   func2     = None,
        #                   func3     = None,
        #                   func4     = None,
        #                   func5     = None,
        #                   funcEC    = None,
        #                   funcCW    = None,
        #                   funcCCW   = None)