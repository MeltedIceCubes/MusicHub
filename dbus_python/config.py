EXIT_PROGRAM = False
SocketOutput = None
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

def PrintToSocket(message:str):
    SocketOutput.sendall(message.encode('utf-8'))