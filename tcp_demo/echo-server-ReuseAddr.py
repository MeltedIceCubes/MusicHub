# echo-server.py

import socket
import sys
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

sys.path.insert(0, '/home/pi/Desktop/GitHub/MusicHub/i2c')
import display_control

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    # conn.sendall(data)
                    # print(f"Server Received {data!r}")
                    data = data.decode()
                    if data.endswith('\r'):
                        print(data, end = '\r')
                    else:
                        print(data)
                    # print(data.decode())
                except:
                    pass
    print("Connection ended from client side")

if __name__ == "__main__":
    # main()
    display_control.printinghello()