#  Raspberry Pi Master for Arduino Slave
#  i2c_master_pi.py
#  Connects to Arduino via I2C
  
#  DroneBot Workshop 2019
#  https://dronebotworkshop.com
 
from smbus2 import SMBus, i2c_msg
 
addr = 0x8 # bus address
bus = SMBus(1) # indicates /dev/ic2-1
 
 
print ("Enter 1 for ON or 0 for OFF")
while True:
	ledstate = input(">>>>   ")
	if ledstate == "1":
		msg = i2c_msg.write(addr, [0x68, 0x69]) #"hi"
		bus.i2c_rdwr(msg)
	elif ledstate == "0":
		msg = i2c_msg.write(addr, [0x62,0x79,0x65])
		bus.i2c_rdwr(msg)

