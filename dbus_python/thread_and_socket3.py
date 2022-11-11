import threading
from gpio import buttons_polling2 as buttons
import menu_list4 as Menu
import menu_items1 as DispMenu
import dbus_Bluetooth10 as Bluetooth
import config
import logging
logging.basicConfig(format = '%(message)s',level = logging.DEBUG)



# *********************************************************
# ***               Socket Configuration                ***
# *********************************************************
import socket

class Controller_Class:
    def __init__(self):
        self.ButtonScan = buttons.InputManagerObj()
        self.MenuFunctions = None
        self.CurrMenu = Menu.MenuObj()
    def mainLoop(self):
        '''
        @info : - Main function loop.
                - Pass button parse object to functions that need it.
        @return : None. Just exit loop when Global is quitting.
        '''
        self.CurrMenu = DispMenu.AAA000
        # self.CurrMenu = Menu.MenuObj(func1 = self.BluetoothObj.Curr_Dongle.Power_Toggle,
        #                              func2 = self.BluetoothObj.Curr_Dongle.Scan_On)
        logging.debug("|  Power  |         |         |         |         |")
        while not config.EXIT_PROGRAM:
            ButtonOutput = self.getButtonInput()  #Get Input choice as string
            if ButtonOutput != None:
                # Get function from Key press
                FunctionToExecute = Menu.ParseButton(ButtonOutput,self.CurrMenu)
                # Check if function is callable
                if callable(FunctionToExecute):
                    # Run function
                    self.CurrMenu = FunctionToExecute(self)
                    # self.CurrMenu.printMenu()

            # Check for state changes in Bluetooth devices.
            # config.BtController.GetDongleVolumes()
        config.BtController.shutdown()

    def getButtonInput(self):
        '''
        @info : scan for one cycle of input.
        @return : return button string OR None
        '''
        self.ButtonScan.PollInput()  # Poll one cycle of input
        if self.ButtonScan.NewOutput == True: # Check for new out from buttons
            return self.ButtonScan.SingleOutput
        else:
            return None

    def parseExecutedFunctionReturn(self):
        pass



def ExitChecker():
    while not config.EXIT_PROGRAM:
        message = input("Press enter to quit\n\n")
        if message == "Z":
            config.EXIT_PROGRAM = True
            break



def main():
    # Set up socket connection to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as LocalSocketOutput:
        # Make socket reusable
        LocalSocketOutput.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Connect to socket
        LocalSocketOutput.connect((config.HOST, config.PORT))
        config.SocketOutput = LocalSocketOutput

        # Initialize main controller object
        Controller = Controller_Class()
        # Initialize Bluetooth Object
        config.BtController = Bluetooth.Bluetooth_Object_Manager()

        ExitChecker_Thread = threading.Thread(target=ExitChecker)
        Controller_Thread  = threading.Thread(target = Controller.mainLoop)


        ExitChecker_Thread.start()
        Controller_Thread.start()

        ExitChecker_Thread.join()
        Controller_Thread.join()

if __name__ == "__main__":
    logging.debug("Starting Program")
    main()
    logging.debug("Ending Program")