import threading
from gpio import buttons_polling2 as buttons
import menu_list4 as Menu
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
        self.BluetoothObj = Bluetooth.Bluetooth_Object_Manager()
        self.CurrMenu = Menu.MenuObj()
    def mainLoop(self):
        '''
        @info : - Main function loop.
                - Pass button parse object to functions that need it.
        @return : None. Just exit loop when Global is quitting.
        '''
        self.CurrMenu = Menu.AAA000
        # self.CurrMenu = Menu.MenuObj(func1 = self.BluetoothObj.Curr_Dongle.Power_Toggle,
        #                              func2 = self.BluetoothObj.Curr_Dongle.Scan_On)
        while not config.EXIT_PROGRAM:
            ButtonOutput = self.getButtonInput()  #Get Input choice

            if ButtonOutput != None:

                print(ButtonOutput)

                # Get function from Key press
                FunctionToExecute, FunctionParams = Menu.ParseButton(ButtonOutput,self.CurrMenu)
                # If that button has a function: (has to be "Run()")
                if callable(FunctionToExecute):
                    # Run Function.Run()
                    ExecutedFunctionReturn = FunctionToExecute(self.getButtonInput, *FunctionParams)
                    # Parse ExecutedFunctionReturn to a managable object
                    parsedFuncReturn = Menu.FunctionReturnClass(ExecutedFunctionReturn)
                    if parsedFuncReturn.MenuItem != None:
                        self.CurrMenu=parsedFuncReturn.MenuItem


                    # TODO : Check if "ExecutedFunctionReturn" is a new menu item.
                    # TODO : ExecutedFunctionReturn might need to pass data back.

        self.BluetoothObj.shutdown()


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

def checkPower(Bt_obj):
    Bt_obj.Power_Check()


def main():
    # Set up socket connection to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as LocalSocketOutput:
        # Make socket reusable
        LocalSocketOutput.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Connect to socket
        LocalSocketOutput.connect((config.HOST, config.PORT))
        config.SocketOutput = LocalSocketOutput

        #TODO INITIALIZE DONGLES
        Controller = Controller_Class()

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