import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time, threading

EXIT_BUTTON = False

def timeMS():
    return (int(time.time()*1000))

DEBOUNCE_TIME = 50 # (ms)
PRESS_TIME    = 0 # (ms)

# ButtonList       = [None, None, None, None, None, None]
# BtnPinList       = [11,   13,   15,   16,   18,   40]
# ButtonOutputIDs  = ["B1", "B2", "B3", "B4", "B5", "EC"]
# ButtonOutputs    = [0,    0,    0,    0,    0,    0]
# ButtonSingleOutput = None
# ButtonSingleOutputPrev = None


#
# def initializeButtons():
#     global ButtonList, BtnPinList
#     for i in range(len(ButtonList)):
#         ButtonList[i] = ButtonObj(BtnPinList[i])

class ButtonManagerObj:
    ButtonNumber = 6

    def __init__(self):
        self.ButtonList = []
        self.ButtonPinList     = [11, 13, 15, 16, 18, 40]
        self.ButtonOutputIDs   = ["B1", "B2", "B3", "B4", "B5", "EC"]
        self.ButtonOutputs     = [0,    0,    0,    0,    0,    0]
        self.ButtonOutputsPrev = [0,    0,    0,    0,    0,    0]
        self.ButtonSingleOutput = None
        self.ButtonSingleOutputPrev = None
        for i in range(len(self.ButtonPinList)):
            self.ButtonList.append(ButtonObj(self.ButtonPinList[i]))
            GPIO.setup(self.ButtonPinList[i], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    def ProcessButtons(self):
        # Iterate through buttons,
        for i in range(len(self.ButtonList)):
            #if Output is detected,
            if 1 == self.ButtonList[i].Output:
                # Store into ButtonOutputs array.
                self.ButtonOutputs[i] = 1
                # If SingleOutput is not outputting anything and the previous OutputArray is all clear of inputs.
                if (self.ButtonSingleOutput == None) and (True == all(o == 0 for o in self.ButtonOutputsPrev)):
                    # This button ID is assigned to SingleOutput.
                    self.ButtonSingleOutput = self.ButtonOutputIDs[i]
            else:
                self.ButtonOutputs[i] = 0
                if self.ButtonSingleOutput == self.ButtonOutputIDs[i]:
                    self.ButtonSingleOutput = None
        if self.ButtonSingleOutputPrev != self.ButtonSingleOutput:
        # if self.ButtonSingleOutputPrev == None:
            print(self.ButtonSingleOutput)
            self.ButtonSingleOutputPrev = self.ButtonSingleOutput
        self.ButtonOutputsPrev = list(self.ButtonOutputs)
        # print(self.ButtonOutputsPrev)


class ButtonObj:
    def __init__(self, pinNum, debounceTime = DEBOUNCE_TIME, pressTime = PRESS_TIME):
        now = timeMS()
        self.PinNum = pinNum

        self.DebTimer = now
        self.DebDuration = debounceTime

        self.PressTimer = now

        self.pinRead = 0
        self.Output = 0

    def isPressed(self):
        self.pinRead = GPIO.input(self.PinNum)
        if True == self.DebounceCheck():
            # Invert output if it was actually a press
            if 0 == self.Output:
                self.Output = 1
                # print(self.PinNum)
            elif 1 == self.Output:
                self.Output = 0

    def DebounceCheck(self): # True == Real button press
        if self.pinRead != self.Output: # New state detected
            now = timeMS()
            if (now < self.DebTimer + self.DebDuration): # Debounce detected
                return False
            else:
                self.DebTimer = now
                return True


class EncoderManagerObj:
    def __init__(self):
        self.EncPinList = [36, 38]
        self.Encoder = EncoderObj(self.EncPinList[0],self.EncPinList[1])
        for i in range(len(self.EncPinList)):
            GPIO.setup(self.EncPinList[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

class EncoderObj:
    def __init__(self,clkPin,dtPin):
        self.clkPin  = clkPin
        self.dtPin   = dtPin
        self.ClkPinState      = 0
        self.LastClkPinState  = 0
        self.Output  = 0

    def isRotated(self):
        ClkPinRead = GPIO.input(self.clkPin)
        dtPinRead = GPIO.input(self.dtPin)
        if ClkPinRead != self.LastClkPinState:
            if (ClkPinRead == 1) and (dtPinRead ==0):
                print("CW")
            elif (ClkPinRead == 1) and (dtPinRead==1):
                print("CCW")
        self.LastClkPinState = ClkPinRead

class PollingManagerObj:
    def __init__(self,BtnManager, EncManager):
        self.BtnMgr = BtnManager
        self.EncMgr = EncManager

    def ButtonPolling(self):
        global EXIT_BUTTON
        while not EXIT_BUTTON:
            for i in range(len(self.BtnMgr.ButtonList)):
                self.BtnMgr.ButtonList[i].isPressed()
                self.EncMgr.Encoder.isRotated()
            self.BtnMgr.ProcessButtons()

def ExitChecker():
    global EXIT_BUTTON
    while not EXIT_BUTTON:
        message = input("Press enter to quit\n\n")
        if message == "Z":
            EXIT_BUTTON = True

def main():
    # Ignore warning for now
    GPIO.setwarnings(False)

    # Use physical pin numbering
    GPIO.setmode(GPIO.BOARD)
    

    ButtonManager = ButtonManagerObj()
    # initializeButtons()

    EncoderManager = EncoderManagerObj()
    # initializeEncoder()
    PollingManager = PollingManagerObj(ButtonManager, EncoderManager)

    # GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Set up threads
    Button_Thread = threading.Thread(target = PollingManager.ButtonPolling)
    ExitChecker_Thread = threading.Thread(target = ExitChecker)

    Button_Thread.start()
    ExitChecker_Thread.start()

    Button_Thread.join()
    ExitChecker_Thread.join()

    # Clean up
    GPIO.cleanup()


if __name__ == "__main__":
    main()
