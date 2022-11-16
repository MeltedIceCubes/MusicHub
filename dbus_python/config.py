EXIT_PROGRAM = False
SocketOutput = None
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
BtController = None
# *********************************************************
# ***             Button Menu Definitions               ***
# *********************************************************
#           C1        C2        C3        C4        C5
#       ---------------------------------------------------
#  R1   |  Power  |  Media  | Connect |   Yes   |    No   |
#       |---------|---------|---------|---------|---------|
#  R2   |   Scan  | Devices |   Save  |         |   Back  |
#       |---------|---------|---------|---------|---------|
#  R3   |   Play  |  Pause  |   Prev  |   Next  |         |
#       ---------------------------------------------------
M_R1_Power   = None
M_R1_Media   = None
M_R1_Connect = None
M_R1_Yes     = None
M_R1_No      = None

M_R2_Scan    = None
M_R2_Devices = None
M_R2_Delete  = None
M_R2_Back    = None

M_R3_Prev    = None
M_R3_Plause  = None
M_R3_Next    = None

M_Encoder    = None


def PrintToSocket(message:str):
    SocketOutput.sendall(message.encode('utf-8'))