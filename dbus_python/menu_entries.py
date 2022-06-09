"""
 *** Menu Structure ***

Dongle Select :
    - Dongle 1
    - Dongle 2
    - Dongle 3

Dongle Select/Dongle# :
    - Initialize (if not initialized.)
        - yes/no
        - back
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
        - Back
"""
Dongle_select_msg = ['Select Dongle : ',
                     '  1 : Dongle 1',
                     '  2 : Dongle 2',
                     '  3 : Dongle 3']
Dongle_select_select = ['1','2','3']

Power_msg = ['Power Mode :',
                    '  1 : On',
                    '  2 : Off',
                    '  0 : Back']
Power_select = ['1','2','0']

Discoverable_msg = ["Discoverable: ",
                    "  1 : On",
                    "  2 : Off",
                    "  0 : Back"]
Discoverable_select = ['1','2','0']

Media_control_msg = ['Media Controls:',
                     '  1 : Play',
                     '  2 : Pause',
                     '  3 : Next',
                     '  4 : Previous',
                     '  5 : Vol Up',
                     '  6 : Vol Dn'
                     '  0 : Back']
Media_control_select = ['1','2','3','4','5','6','0']

