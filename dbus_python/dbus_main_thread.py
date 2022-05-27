import dbus_Bluetooth7 as bluez_dbus
import time
import threading

BREAK_MAIN_LOOP = False
START_TIME = 0

class process:
    def __init__(self, sleep_time, name):
        self.sleep_time = sleep_time
        self.start_time = 0
        self.name = name
    def timer(self):
        self.start_time = 1000 * time.time()
        time.sleep(self.sleep_time)
        print("%s : %d -> %d" % (self.name, (self.start_time - START_TIME), (1000 * time.time() - START_TIME)))

class UI_thread:
    def __init__(self):
        print("Press Z at any time to quit")
        BREAK_MAIN_LOOP = False
        self._observers = []
    def waitForInput(self):
        global BREAK_MAIN_LOOP
        x = input()

        for callback in self._observers:
            print('announcing change')
            callback()

        if x == "Z":
            print("Stopped at : %d" %(time.time() * 1000))
            BREAK_MAIN_LOOP = True


def SomethingHappened():
    print("Something happened")

if __name__ == '__main__':
    print("Main Thread : Start")

    ui_func = UI_thread()
    ui_func._observers.append(SomethingHappened)
    func1 = process(0.3, "f1")
    ui_thread = threading.Thread(target=ui_func.waitForInput)
    ui_thread.start()

    while BREAK_MAIN_LOOP != True:
        thread1 = threading.Thread(target = func1.timer)
        thread1.start()
        # print(ui_thread.is_alive)
        if ui_thread.is_alive() == False:
            print("thread died")
            ui_thread = threading.Thread(target=ui_func.waitForInput)
            ui_thread.start()
        thread1.join()

    print("Main Thread : End")




    # UI_thread()