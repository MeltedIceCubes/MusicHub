import dbus_Bluetooth7 as bluez_dbus
import time

import threading

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


if __name__ == "__main__":
    print("Starting Main")
    START_TIME = time.time() * 1000
    print("%d" % START_TIME)
    func1 = process(0.1, "f1")
    func2 = process(0.2, "f2")
    func3 = process(0.3, "f3")
    print("enter main loop")
    while True:
        thread1 = threading.Thread(target=func1.timer)
        thread2 = threading.Thread(target=func2.timer)
        thread3 = threading.Thread(target=func3.timer)
        thread1.start()
        thread2.start()
        thread3.start()
        thread1.join()
        thread2.join()
        thread3.join()

    print("End Of Line @ %dms" % (1000 * time.time() - START_TIME))

if __name__ != '__main__':
    print(bluez_dbus.MAC_LIST)