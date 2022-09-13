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
Dongle_select_msg = ['Select Dongle : ',
                     '  1 : Input 1',
                     '  2 : Input 2',
                     '  3 : Output']
Dongle_select_choices = ['1','2','3']
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
Action_select_msg = ['Action :',
                     '  1 : Power',
                     '  2 : Scan',
                     '  3 : Media Controls',
                     '  0 : Back']
Action_select_choices = ['1','2','3','0']
Action_select_priority = [1,1,1,1]

Power_msg = ['Power Mode :',
                    '  1 : On',
                    '  2 : Off',
                    '  0 : Back']
Power_select = ['1','2','0']
Power_priority = [1,1,1]

Scan_msg = ['Scan Mode:',
            '  1 : On',
            '  2 : Off',
            '  0 : Back']
Scan_select = ['1','2','0']
Scan_priority = [1,1,1]

Discoverable_msg = ["Discoverable: ",
                    "  1 : On",
                    "  2 : Off",
                    "  0 : Back"]
Discoverable_select = ['1','2','0']
Discoverable_priority = [1,1,1]

Media_control_msg = ['Media Controls:',
                     '  1 : Play',
                     '  2 : Pause',
                     '  3 : Next',
                     '  4 : Previous',
                     '  5 : Vol Dn',
                     '  6 : Vol Up'
                     '  0 : Back']
Media_control_select = ['1','2','3','4','5','6','0']
Media_control_priority=[1,1,1,1,1,1,1]

