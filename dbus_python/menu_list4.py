import config
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
                 param1 = None,
                 param2 = None,
                 param3 = None,
                 param4 = None,
                 param5 = None,
                 paramEC = None,
                 paramCW = None,
                 paramCCW=None
                ):
        self.B1 = func1
        self.B2 = func2
        self.B3 = func3
        self.B4 = func4
        self.B5 = func5
        self.EC = funcEC
        self.CW = funcCW
        self.CCW = funcCCW
        self.B1_param = param1
        self.B2_param = param2
        self.B3_param = param3
        self.B4_param = param4
        self.B5_param = param5
        self.EC_param = paramEC
        self.CW_param = paramCW
        self.CCW_param = paramCCW


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
    param = None
    if input == "B1":
        func = functions.B1
        param = functions.B1_param
    elif input == "B2":
        func = functions.B2
        param = functions.B2_param
    elif input == "B3":
        func = functions.B3
        param = functions.B3_param
    elif input == "B4":
        func = functions.B4
        param = functions.B4_param
    elif input == "B5":
        func = functions.B5
        param = functions.B5_param
    elif input == "EC":
        func = functions.EC
        param = functions.EC_param
    elif input == "CW":
        func = functions.CW
        param = functions.CW_param
    elif input == "CCW":
        func = functions.CCW
        param = functions.CCW_param
    # func = CheckForRunAttr(func)
    if param == None:
        param = []
        # empty list because calling a executing with None is bad
        # "Value after * must be an iterable, not NoneType" <- FunctionToExecute
    return func, param

def CheckForRunAttr(function):
    '''
    @info : Checks for run method in the passed function
    @return : if Run method exists => function.Run()
                            if not => None
    '''
    FunctionRun = getattr(function,"Run", None)
    if FunctionRun != None:
        return FunctionRun
    else:
        return None

class FunctionReturnClass:
    '''
    @info : First element of FunctionReturn MUST represent MenuObj.
            The rest is interpreted as extra data which will be put into a tuple.
    '''
    def __init__(self, FunctionReturn):
        self.MenuItem = None
        self.data = ()
        tempData = []
        try: # Assuming FunctionReturn is not None
            # check if first element is menu item or not.
            if type(FunctionReturn[0]) ==  MenuObj:
                self.MenuItem = FunctionReturn[0]
            for i in range(1, len(FunctionReturn)):
                tempData.append(FunctionReturn[i])
            self.data = tuple(tempData)
        except: # FunctionReturn was None
            pass

class Menu_YesNoBack():
    def __init__(self,yes = None, no = None ):
        self.yesFunc = yes
        self.noFunc = no
    def Run(self,ctrl):
        exit = False
        selection = ["Y", "-", "-", "-", "N"]
        selection_width = 5
        selection_default = 2
        selection_cursor = "O"
        counter = selection_default  # Y 1 [2] 3 N
        curr_selection = list(selection)
        while not (exit or config.EXIT_PROGRAM) :
            curr_selection = list(selection)
            ButtonOutput = ctrl()
            if ButtonOutput:
                if ButtonOutput == "B5":
                    exit = True
                    break
                if ButtonOutput == "CW":
                    if counter < 4:
                        counter += 1
                elif ButtonOutput == "CCW":
                    if counter >0:
                        counter -= 1
                elif ButtonOutput == "EC":
                    if counter == 0:
                        return x
                        # if self.yesFunc:
                        #     self.yesFunc()
                    elif counter == 4:
                        return x
                        # if self.noFunc:
                        #     self.noFunc()
            curr_selection[counter] = selection_cursor  # Update cursor
            menuOutput = self.make_string(curr_selection)
            config.PrintToSocket(menuOutput)
    def make_string(self, items):
        string = ""
        for i in items:
            string = string + i
        string = string + "\r"
        return string

class Menu_SelectableOptions():
    def __init__(self, options:list, functions=None, params = None):
        self.options    = list(options) # list of strings
        # self.functions  = list(functions) # list of functions
        # self.params     = list(params) # list of whatever needed
        self.selection_index = 1
    def Run(self, ctrl):
        exit = False
        while not (exit or config.EXIT_PROGRAM) :
            ButtonOutput = ctrl()
            if ButtonOutput:
                if ButtonOutput == "B5": # Exit this menu. No selection
                    exit = True
                    break
                if ButtonOutput == "CW":
                    if ((self.selection_index) < (len(self.options))):
                        self.selection_index += 1
                elif ButtonOutput == "CCW":
                    if (self.selection_index > 1):
                        self.selection_index -= 1
                elif ButtonOutput == "EC": # Execute function
                    pass

            menuOutput = "%s/%s:" %(self.selection_index, len(self.options)) + self.options[self.selection_index-1] + "\r"

            config.PrintToSocket(menuOutput)
        return_val = FunctionReturnClass(None)
        return return_val


# TEST MENU OBJECTS
class PrintItems:
    def __init__(self, default = "Kye"):
        self.msg = default
    def Run(self, control, p1 = "None", p2= "None", p3= "None", p4= "None"):
        # print(self.msg)
        print(p1)
        print(p2)
        print(p3)
        print(p4)
        return (AAA111, None)
class returnMenuTest:
    def __init__(self):
        pass
    def Run(self,control):
        control = None # Unused
        print("Back to default Menu")
        return (AAA000,)

class AAA1(PrintItems):
    def __init__(self):
        self.msg = "I'm A1"
class AAA2(PrintItems):
    def __init__(self):
        self.msg = "I'm A2"
class AAA3(PrintItems):
    def __init__(self):
        self.msg = "I'm A3"
class AAA4(PrintItems):
    def __init__(self):
        self.msg = "I'm A4"

class BBB1(PrintItems):
    def __init__(self):
        self.msg = "I'm A1"
class BBB2(PrintItems):
    def __init__(self):
        self.msg = "I'm A2"
class BBB3(PrintItems):
    def __init__(self):
        self.msg = "I'm A3"
class BBB4(PrintItems):
    def __init__(self):
        self.msg = "I'm A4"


# Main Menu
AAA000 = MenuObj(func1 = Menu_SelectableOptions(["Choice 1","Choice 2","Choice 3"]).Run,
                 func2 = Menu_YesNoBack().Run,
                 func3 = AAA3().Run,
                 func4 = AAA4().Run,
                 func5 = returnMenuTest().Run,
                 # param1= ("A1","Layer1"),
                 # param2= ("A2","Layer1"),
                 param3= ("A3","Layer1"),
                 param4= ("A4","Layer1"))

AAA111 = MenuObj(func1 = AAA1().Run,
                 func2 = AAA2().Run,
                 func3 = AAA3().Run,
                 func4 = AAA4().Run,
                 func5 = returnMenuTest().Run,
                 param1= ("B1","Layer2"),
                 param2= ("B2","Layer2"),
                 param3= ("B3","Layer2"),
                 param4= ("B4","Layer2"))
