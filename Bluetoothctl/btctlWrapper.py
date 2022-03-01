

import time
import pexpect
import subprocess
import sys
import re

class BluetoothctlError(Exception):
    """This exception is raised, when bluetoothctl fails to start."""
    pass


class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self):
        subprocess.check_output("rfkill unblock bluetooth", shell=True)
        self.process = pexpect.spawnu("bluetoothctl", echo=False,timeout=1)
        state = self.process.expect(["Agent registered",".*",pexpect.EOF])
        print(state)
        
        
    def clear_start(self):
        try:
            out = self.get_output(" ")
        except:
            pass
        else:
            res = self.process.expect(["Agent registered",".*",pexpect.EOF])
            return res
        
        
    def send(self, command, pause=0):
        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["bluetooth", pexpect.EOF]):
            raise Exception(f"failed after {command}")

    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.send(*args, **kwargs)
        return self.process.before.split("\r\n")

    def agent_off(self):
        try:
            out = self.get_output("agent off")
        except BleutoothctlError as e:
           print(e)
           return None
        else:
            res = self.process.expect(["Agent unregistered",".*",pexpect.EOF])
            return res

if __name__ =="__main__":
    blue=Bluetoothctl()
    blue.clear_start()
    blue.agent_off()
    blue.agent_off()
    blue.agent_off()
    
#https://gist.github.com/castis/0b7a162995d0b465ba9c84728e60ec01




