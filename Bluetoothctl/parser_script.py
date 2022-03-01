import sys
import re
import os
if __name__ =="__main__":
    args_passed = "Null"
    fifo_prev = ''
    while True:
        p = open("pipe0","r")
        print(p.read())

