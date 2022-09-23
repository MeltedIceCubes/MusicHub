# echo-client.py

import socket, time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

msg_cnt = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True: 
        msg = ("Hello World : %s" %msg_cnt)
        b = msg.encode('utf-8')
        s.sendall(b)
        data = s.recv(1024)
        if data: 
            print(f"Received {data!r}")
            msg_cnt = msg_cnt + 1
        time.sleep(5)