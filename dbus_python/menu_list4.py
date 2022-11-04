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


class MenuObj():
    def __init__(self,
                 func1=None,
                 func2=None,
                 func3=None,
                 func4=None,
                 func5=None,
                 funcEC=None,
                 funcCW=None,
                 funcCCW=None,
                ):
        self.B1 = func1
        self.B2 = func2
        self.B3 = func3
        self.B4 = func4
        self.B5 = func5
        self.EC = funcEC
        self.CW = funcCW
        self.CCW = funcCCW
    def printMenu(self):
        if self.B1 != None:
            config.PrintToSocket("\n1 : O")
        else:
            config.PrintToSocket("\n1 : X")
        if self.B2 != None:
            config.PrintToSocket("2 : O")
        else:
            config.PrintToSocket("2 : X")
        if self.B3 != None:
            config.PrintToSocket("3 : O")
        else:
            config.PrintToSocket("3 : X")
        if self.B4 != None:
            config.PrintToSocket("4 : O")
        else:
            config.PrintToSocket("4 : X")
        if self.B5 != None:
            config.PrintToSocket("5 : O\n")
        else:
            config.PrintToSocket("5 : X\n")

def ParseButton(input , functions : MenuObj):
    '''
    @info : input => Controller_Class.getButtonInput()'s output
                    to get button inputs from keys
            functions => class MenuObj
                        list of executable functions
    @return : selected function and it's parameters.
                func :  none if not registered in MenuObj.
                param : if none -> empty list so that it is iterable
                        for later functions.
    '''
    func = None
    if input == "B1":
        func = functions.B1
    elif input == "B2":
        func = functions.B2
    elif input == "B3":
        func = functions.B3
    elif input == "B4":
        func = functions.B4
    elif input == "B5":
        func = functions.B5
    elif input == "EC":
        func = functions.EC
    elif input == "CW":
        func = functions.CW
    elif input == "CCW":
        func = functions.CCW
    return func

