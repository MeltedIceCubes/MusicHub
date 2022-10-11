import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time, threading

Button_Lock = threading.Lock()
EXIT_BUTTON = False
# Button_Events =
# ButtonDebTimers = [None,None,None,None,None]
ButtonList = []

DEBOUNCE_TIME = 0 # (ms)
PRESS_TIME = 0 # (ms)

class ButtonManagerObj:
    def __init__(self, debounceTime = DEBOUNCE_TIME, pressTime = PRESS_TIME):
        now  = TimeMS()
        self.DebTimer = now
        self.DebDuration = debounceTime
        self.PressTimer = now
        self.PressDuration = PRESS_TIME

def TimeMS():
    return (int(time.time()*1000))

def initializeButtons():
    global ButtonList
    for i in range(5):
        ButtonList.append(ButtonManagerObj())

def DebounceTimer(buttons,index, debTime = DEBOUNCE_TIME):
    now = TimeMS()
    if (now < (buttons[index].DebTimer + debTime)):
        # print("Now :  %s\nTimer : %s" %(now, (ButtonDebTimers[0]+debTime)))
        buttons[index].DebTimer = now
        return False
    else:
        buttons[index].DebTimer = now
        return True

def PressTimer():
    now = TimeMS()
#Button Pins = 11,13,15,16,18

B1Sts = False
button_counter = 0
ignore_counter = 0
def button1_callback(gpio_pin):
    global ButtonDebTimers, B1Sts, button_counter, ignore_counter
    curr_state = GPIO.input(gpio_pin)
    print(curr_state)
    if (DebounceTimer(ButtonList,0) == True):
        if B1Sts == False:
            B1Sts = True
            button_counter += 1
            print("Button 1 : %s" %button_counter)

        elif B1Sts == True:
            B1Sts = False
            ignore_counter += 1
            print("Ignore : %s" %ignore_counter)



def button2_callback(gpio_pin):
    print(GPIO.input(gpio_pin))
    print("Button 2")

def button3_callback(gpio_pin):
    if (DebounceTimer(ButtonTimers,2) == True):
        print("Button 3")

def button4_callback(gpio_pin):
    if (DebounceTimer(ButtonTimers,3) == True):
        print("Button 4")

def button5_callback(gpio_pin):
    if (DebounceTimer(ButtonTimers, 4) == True):
        print("Button 5")

def main():
    initializeButtons()

    # Ignore warning for now
    GPIO.setwarnings(False)

    # Use physical pin numbering
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Setup event on pin 10 rising edge
    # GPIO.add_event_detect(11, GPIO.RISING, callback=button1_callback)
    # GPIO.add_event_detect(11, GPIO.BOTH,   callback=button1_callback, bouncetime = 50)
    GPIO.add_event_detect(11, GPIO.BOTH,   callback=button1_callback)
    GPIO.add_event_detect(13, GPIO.RISING, callback=button2_callback)
    GPIO.add_event_detect(15, GPIO.RISING, callback=button3_callback)
    GPIO.add_event_detect(16, GPIO.RISING, callback=button4_callback)
    GPIO.add_event_detect(18, GPIO.RISING, callback=button5_callback)
    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Run until someone presses enter
    message = input("Press enter to quit\n\n")

    # Clean up
    GPIO.cleanup()


if __name__ == "__main__":
    main()
