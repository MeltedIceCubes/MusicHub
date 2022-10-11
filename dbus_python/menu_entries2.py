"""
 *** Menu Structure ***

Dongle Select :
    - Dongle 1
    - Dongle 2
    - Dongle 3

Dongle Select/Dongle# :
    - Power
        - on/off(Toggle)
        - back
    - Scan
        - on/off(Toggle)
        - back
    - Media Controls
        - ... many
        - back
    - Back to dongle select

Dongle Select/Dongle#/MediaControls:
    - Controller:
        - Play/Pause (Toggle)
        - Next
        - Prev
        - VolUp
        - VolDn
        - Back to function select
"""
Dongle_select_msg = [b'Select Dongle : ',
                     b'  1 : Input 1',
                     b'  2 : Input 2',
                     b'  3 : Output']
Dongle_select_choices = ['B1','B2','B3']
Dongle_select_priority = [1,1,1]
# Dongle Select/Dongle# :
#     - Power
#         - on/off(Toggle)
#         - back
#     - Scan
#         - on/off(Toggle)
#         - back
#     - Media Controls
#         - ... many
#         - back
#     - Back to dongle select
Action_select_msg = [b'Action :',
                     b'  1 : Power',
                     b'  2 : Connection',
                     b'  3 : Media',
                     b'  0 : Back']
Action_select_choices = ['B1','B2','B3','B5']
Action_select_priority = [1,1,1,1]

Power_msg = [b'Power Mode :',
                    b'  1 : On',
                    b'  0 : Back']
Power_select = ['B1','B5']
Power_priority = [1,1]

Connection_msg = [b'Connection:',
                        b'  1 : Scan'
                        b'  2 : Devices'
                        b'  0 : Back']
Connection_select = ['B1','B2', 'B5']


Scan_msg = [b'Scan Mode:',
            b'  1 : On',
            b'  0 : Back']
Scan_select = ['B1','B5']
Scan_priority = [1,1]

# Discoverable_msg = ["Discoverable: ",
#                     "  1 : On",
#                     "  2 : Off",
#                     "  0 : Back"]
# Discoverable_select = ['1','2','0']
# Discoverable_priority = [1,1,1]

Media_control_msg = [b'Media Controls:',
                     b'  1 : Play',
                     b'  2 : Pause',
                     b'  3 : Next',
                     b'  4 : Previous',
                     b'  5 : Vol Dn',
                     b'  6 : Vol Up'
                     b'  0 : Back']
Media_control_select = ['B1','B2','B3','B4','CW','CCW','B5']
Media_control_priority=[1,1,1,1,1,1,1]

