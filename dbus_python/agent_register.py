import dbus
import time

BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"
DISPLAY_ONLY         = "DisplayOnly"
DISPLAY_YES_NO       = "DisplayYesNo"
KEYBOARD_ONLY        = "KeyboardOnly"
NO_INPUT_NO_OUTPUT   = "NoInputNoOutput"
KEYBOARD_DISPLAY     = "KeyboardDisplay"



#https://stackoverflow.com/questions/70903233/register-a-bluetooth-agent-with-python-dbus-to-hci1-not-hci0
if __name__ == '__main__':
    bus = dbus.SystemBus()
    obj = bus.get_object(BUS_NAME, "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")

    path = "/test/agent"
    path1 = "/test1/agent1"
    manager.RegisterAgent(path, NO_INPUT_NO_OUTPUT)
    manager.RequestDefaultAgent(path)
    time.sleep(5)
    manager.UnregisterAgent(path)
    time.sleep(5)
    manager.RegisterAgent(path1, DISPLAY_ONLY)
    manager.RequestDefaultAgent(path1)
    time.sleep(5)
