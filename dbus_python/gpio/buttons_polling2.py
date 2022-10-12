import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time, threading

EXIT_BUTTON = False

def timeMS():
    return (int(time.time()*1000))

DEBOUNCE_TIME = 50 # (ms)
PRESS_TIME    = 0 # (ms)

ENC_CLK_PIN = 36
ENC_DT_PIN = 38


class InputManagerObj:
    def __init__(self):
        # Ignore warning for now
        GPIO.setwarnings(False)

        # Use physical pin numbering
        GPIO.setmode(GPIO.BOARD)

        
        self.Inputs = []
        self.ButtonPinList   = [11,    13,   15,   16,   18,   40]
        self.EncoderPinList  = [                                    36,   38]
        self.Outputs         = [ 0,    0,    0,    0,    0,    0,    0,    0]
        self.Prev_Outputs    = [ 0,    0,    0,    0,    0,    0,    0,    0]
        self.OutputIDs       = ["B1", "B2", "B3", "B4", "B5", "EC", "CW", "CCW"]
        # Initialize Buttons
        for b in range(len(self.ButtonPinList)):
            self.Inputs.append(ButtonObj(self.ButtonPinList[b]))

        # Initialize Encoder
        self.Inputs.append(EncoderObj(self.EncoderPinList[0],
                                      self.EncoderPinList[1]))

        self.SingleOutput = None
        self.Prev_SingleOutput = None
        self.NewOutput = False

    def UpdateInputs(self):
        # Update Button Inputs
        for a in range(len(self.ButtonPinList)):
            self.Inputs[a].Update() # Get input status
            self.Outputs[a] = self.Inputs[a].OutputVal

        #Update Encoder Input
        index = len(self.ButtonPinList) # set the index after all the buttons
        self.Inputs[index].Update()
        self.Outputs[index] = self.Inputs[index].OutputVal[0] #CW
        self.Outputs[index+1] = self.Inputs[index].OutputVal[1] #CCW

    def ProcessInputs(self):
        for index, out in enumerate(self.Outputs):
            if out == 1:
                if (None == self.SingleOutput) and (True == all( 0 == p for p in self.Prev_Outputs)):
                    self.SingleOutput = self.OutputIDs[index]
            else:
                if self.SingleOutput == self.OutputIDs[index]:
                    self.SingleOutput = None

        if self.Prev_SingleOutput != self.SingleOutput:
            if self.SingleOutput != None:
                print(self.SingleOutput)
            self.Prev_SingleOutput = self.SingleOutput
            self.NewOutput = True
        else:
            self.NewOutput = False
        self.Prev_Outputs = list(self.Outputs)
        

    def CleanUp(self):
        GPIO.cleanup()

    def PollInputLoop(self):
        global EXIT_BUTTON
        while not EXIT_BUTTON:
            self.UpdateInputs()
            self.ProcessInputs()

    def PollInput(self):
        self.UpdateInputs()
        self.ProcessInputs()



class ButtonObj:
    def __init__(self, pinNum, debounceTime = DEBOUNCE_TIME, pressTime = PRESS_TIME):
        self.PinNum = pinNum
        GPIO.setup(pinNum, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


        now = timeMS()
        self.DebTimer = now
        self.DebDuration = debounceTime

        self.pinRead = 0
        self.OutputVal = 0

    def Update(self): # was isPressed
        self.pinRead = GPIO.input(self.PinNum)
        if True == self.DebounceCheck():
            # Invert output if it was actually a press
            if 0 == self.OutputVal:
                self.OutputVal = 1
                # print(self.PinNum)
            elif 1 == self.OutputVal:
                self.OutputVal = 0

    def DebounceCheck(self): # True == Real button press
        if self.pinRead != self.OutputVal: # New state detected
            now = timeMS()
            if (now < self.DebTimer + self.DebDuration): # Debounce detected
                return False
            else:
                self.DebTimer = now
                return True

class EncoderObj:
    def __init__(self,clkPin,dtPin):
        global ENC_CLK_PIN, ENC_DT_PIN
        self.clkPin = ENC_CLK_PIN
        self.dtPin = ENC_DT_PIN

        GPIO.setup(self.clkPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dtPin,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.ClkPinState      = 0
        self.LastClkPinState  = 0
        self.OutputVal = [0,0] # [ CW, CCW ]

    def Update(self):
        ClkPinRead = GPIO.input(self.clkPin)
        dtPinRead = GPIO.input(self.dtPin)
        if ClkPinRead != self.LastClkPinState:
            if (ClkPinRead == 1) and (dtPinRead ==0):
                # print("CW")
                self.OutputVal = [1,0]
            elif (ClkPinRead == 1) and (dtPinRead==1):
                # print("CCW")
                self.OutputVal = [0,1]
        else:
            self.OutputVal = [0,0]
        self.LastClkPinState = ClkPinRead

class PollingManagerObj:
    def __init__(self,BtnManager, EncManager):
        self.BtnMgr = BtnManager
        self.EncMgr = EncManager



def ExitChecker():
    global EXIT_BUTTON
    while not EXIT_BUTTON:
        message = input("Press enter to quit\n\n")
        if message == "Z":
            EXIT_BUTTON = True



def main():
    InputScan = InputManagerObj()

    # Set up threads
    Button_Thread = threading.Thread(target = InputScan.PollInputLoop)
    ExitChecker_Thread = threading.Thread(target = ExitChecker)

    Button_Thread.start()
    ExitChecker_Thread.start()

    Button_Thread.join()
    ExitChecker_Thread.join()

    InputScan.CleanUp()



if __name__ == "__main__":
    main()
