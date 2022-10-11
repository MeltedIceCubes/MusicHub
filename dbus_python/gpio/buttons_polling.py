import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time, threading

EXIT_BUTTON = False

def timeMS():
    return (int(time.time()*1000))

DEBOUNCE_TIME = 50 # (ms)
PRESS_TIME    = 0 # (ms)

ButtonList       = [None, None, None, None, None, None]
BtnPinList       = [11,   13,   15,   16,   18,   40]
ButtonOutputIDs  = ["B1", "B2", "B3", "B4", "B5", "EC"]
ButtonOutputs    = [0,    0,    0,    0,    0,    0]
ButtonSingleOutput = None
ButtonSingleOutputPrev = None
Encoder     = None
EncPinList  = [36,   38]

class ButtonManagerObj:
    def __init__(self, pinNum, debounceTime = DEBOUNCE_TIME, pressTime = PRESS_TIME):
        now = timeMS()
        self.PinNum = pinNum

        self.DebTimer = now
        self.DebDuration = debounceTime

        self.PressTimer = now
        self.PressDuration = pressTime

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
        self.clkPin  = EncPinList[0]
        self.dtPin   = EncPinList[1]
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


def initializeButtons():
    global ButtonList, BtnPinList
    for i in range(len(ButtonList)):
        ButtonList[i] = ButtonManagerObj(BtnPinList[i])

def initializeEncoder():
    global Encoder
    Encoder = EncoderManagerObj()

def ProcessButtons():
    global ButtonList, ButtonOutputs, ButtonOutputIDs, ButtonSingleOutput, ButtonSingleOutputPrev
    #This will cause the left most button to be processed first.
    # but, that's okay...
    for i in range(len(ButtonList)):
        if 1 == ButtonList[i].Output:
            ButtonOutputs[i] = 1
            if ButtonSingleOutput == None:
                ButtonSingleOutput = ButtonOutputIDs[i]
        else:
            ButtonOutputs[i] = 0
            if ButtonSingleOutput == ButtonOutputIDs[i]:
                ButtonSingleOutput = None
    if ButtonSingleOutputPrev != ButtonSingleOutput:
        print(ButtonSingleOutput)
        ButtonSingleOutputPrev=ButtonSingleOutput


    # print(ButtonOutputs)




def ButtonPolling():
    global EXIT_BUTTON
    global ButtonList, Encoder
    # output =
    while not EXIT_BUTTON:
        for i in range(len(ButtonList)):
            ButtonList[i].isPressed()
            Encoder.isRotated()
        ProcessButtons()


def ExitChecker():
    global EXIT_BUTTON
    while not EXIT_BUTTON:
        message = input("Press enter to quit\n\n")
        if message == "Z":
            EXIT_BUTTON = True


def main():

    initializeButtons()

    initializeEncoder()


    # Ignore warning for now
    GPIO.setwarnings(False)

    # Use physical pin numbering
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Set up threads
    Button_Thread = threading.Thread(target = ButtonPolling)
    ExitChecker_Thread = threading.Thread(target = ExitChecker)

    Button_Thread.start()
    ExitChecker_Thread.start()

    Button_Thread.join()
    ExitChecker_Thread.join()

    # Clean up
    GPIO.cleanup()


if __name__ == "__main__":
    main()
