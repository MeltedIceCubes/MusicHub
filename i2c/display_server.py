# echo-server.py

import socket
import sys
import threading
import time
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

sys.path.insert(0, '/home/pi/Desktop/GitHub/MusicHub/i2c')
import display_control1 as display_control


DispLock = threading.Lock()
DisplayData = [None for i in range(10)]
EXIT_CHECK = [False,]
def main():
    global DisplayData
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()

        # Set up thread
        Disp_Thread = threading.Thread(target = DisplayPrinter)
        Disp_Thread.start()
        with conn:
            print(f"Connected by {addr}")
            while True:
                # try:
                data = conn.recv(1024)
                if not data:
                    break
                # conn.sendall(data)
                # print(f"Server Received {data!r}")
                data = data.decode()
                if data.endswith('\\r'):
                    data = data.replace('\\r', '')
                    # print(data, end = '\r')
                    DispLock.acquire()
                    DisplayData = data
                    DispLock.release()
                else:
                    print(data)
                # print(data.decode())
                # except:
                #     pass
    print("Connection ended from client side")
    EXIT_CHECK[0] = True
    Disp_Thread.join()


def DisplayPrinter():
    global DisplayData, EXIT_CHECK
    PastDisplayData = None
    DisplayManager = display_control.DisplayManager_class()
    while EXIT_CHECK[0] == False:
        if not DispLock.locked():
            if DisplayData != PastDisplayData:
                DisplayManager.Update(DisplayData)
                PastDisplayData = DisplayData
            DisplayManager.printItems()
            # print(DisplayData, end = '\r')
            time.sleep(0.1)


if __name__ == "__main__":
    main()
    # display_control.printinghello()