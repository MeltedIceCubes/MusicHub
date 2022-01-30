# -*- coding: utf-8 -*-

"""
Control bluetoothctl with python using pexpect.
"""

import pexpect
child = pexpect.spawn('bluetoothctl',encoding='utf-8',timeout = 1,echo = False)
child.send("agent off" + "\n")
#words = child.expect(["bluetooth",pexpect.EOF])
words = child.expect("\[bluetooth\]")
#print(child.before.split("\r\n"))
print(child.before)
#print(child.after)

#   *********************
#   ***   Resources   ***
#   *********************
#  API : https://pexpect.readthedocs.io/en/stable/api/pexpect.html
#  Example code : https://gist.github.com/egorf/66d88056a9d703928f93
#  