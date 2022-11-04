import re
import time

MAX_MSG_LEN = 10


# // TODO make a new class for each display mode
# // TODO Fix conflict of overlapping texts
# TODO Fix for empty string codes
def Create_Display_Item(mode, index, message):
    ModeSortKeys = {'s': Static_Display_Item,
                    'b': Blink_Display_Item,
                    'd': Dynamic_Display_Item,
                    'B': Fast_Blink_Display_Item}
    # 1: Static(s)
    # 2: Blink(b)
    # 3: Dynamic(d)
    try:
        mode = ModeSortKeys[mode]
    except:
        mode = ModeSortKeys['s']  # default to static
    return mode(index, message)


class Generic_Display_Item:
    def __init__(self, index: str, message: str):
        self.start_index = int(index)
        self.end_index = MAX_MSG_LEN
        self.message = message
        self.str_index = 0
        self.mode = 2

    def InsertLetters(self, CurrOutput):
        NewOutput = list(CurrOutput)
        # Iterate through message
        for i in range(len(self.message)):
            # check if index is more than the message length
            if ((self.start_index + i) > MAX_MSG_LEN - 1) or \
                    (NewOutput[self.start_index + i] != None):
                pass
            elif (self.start_index + i) >= self.end_index:
                break
            else:
                if (self.str_index + i) < len(self.message):
                    # where in the message to append from
                    NewOutput[self.start_index + i] = \
                        self.message[self.str_index + i]
                else:  # Over the message length
                    NewOutput[self.start_index + i] = " "
            # Check if all slots are filled:
            if (not None in NewOutput):
                break

        self.UpdateStrDisplay()
        return NewOutput

    def UpdateStrDisplay(self):
        pass
    def UpdateTime(self):
        self.now = int(time.time() * 1000)

class Static_Display_Item(Generic_Display_Item):
    def __init__(self, index: str, message: str):
        super().__init__(index, message)
        self.mode = 1

    def InsertLetters(self, CurrOutput):
        output = super().InsertLetters(CurrOutput)
        return output

    def UpdateStrDisplay(self):
        super().UpdateStrDisplay()


class Blink_Display_Item(Generic_Display_Item):
    def __init__(self, index: str, message: str):
        super().__init__(index, message)
        self.mode = 2
        self.save_message = message
        self.hidden = False
        self.blinkRate = 1000  # ms
        self.lastToggle = 0  # how many ms ago it toggled
        self.now = 0
        self.UpdateTime()

    def InsertLetters(self, CurrOutput):
        output = super().InsertLetters(CurrOutput)
        return output

    def UpdateStrDisplay(self):
        self.UpdateTime()
        if (self.now - self.lastToggle) > self.blinkRate:
            self.lastToggle = self.now
            if self.hidden == False:
                self.hidden = True  # toggle
                self.message = " " * len(self.save_message)
            else:
                self.hidden = False
                self.message = self.save_message




class Dynamic_Display_Item(Generic_Display_Item):
    def __init__(self, index: str, message: str):
        super().__init__(index, message)
        self.mode = 3
        self.now = 0
        self.advanceRate = 300
        self.UpdateTime()
        self.lastAdvance = self.now + 500
    def InsertLetters(self, CurrOutput):
        output = super().InsertLetters(CurrOutput)
        return output

    def UpdateStrDisplay(self):
        self.UpdateTime()
        if (self.now - self.lastAdvance) > self.advanceRate:
            self.lastAdvance = self.now
            if (self.str_index < (len(self.message))):
                self.str_index += 1
            else:
                self.str_index = 0



class Fast_Blink_Display_Item(Blink_Display_Item):
    def __init__(self, index: str, message: str):
        super().__init__(index, message)
        self.blinkRate = 200
        self.mode = 4

def split_text(message):
    """
    Split the passed message and create xxx_Display_Items.
    """
    display_items = []
    try:
        split_items = re.split(r'(\*\w\d\-)', message)
    except:
        split_items = None
    # split_items = re.split(r'\*\w\d\-', message)

    if split_items:
        split_items.pop(0)
        for i in range(0, len(split_items), 2):
            match = re.search(r'(\*)(\w)(\d)(\-)', split_items[i])
            # display_items.append(text_mode_item(match.group(2),
            #                                     match.group(3),
            #                                     split_items[i+1]))
            display_items.append(
                Create_Display_Item(match.group(2),  # mode
                                    match.group(3),  # start index
                                    split_items[i + 1]  # message
                                    ))
        display_items = sorted(display_items, key=lambda x: x.start_index)
        for i in range(len(display_items)):
            if (i < (len(display_items) - 1)):
                display_items[i].end_index = display_items[i + 1].start_index
            else:
                pass
        return display_items

    return []  # bad message recieved


def display_items_Loop(message_objs):
    ordered_message_objs = sorted(message_objs, key=lambda x: x.start_index)

    while True:
        DisplayOutput = [None for i in range(10)]
        for obj in ordered_message_objs:
            DisplayOutput = obj.InsertLetters(DisplayOutput)
        DisplayOutput = [" " if D == None else D for D in DisplayOutput]
        print(">" + (''.join(DisplayOutput)) + "<", end='\r')
        time.sleep(0.01)

def display_items(message_objs):
    try:
        ordered_message_objs = sorted(message_objs, key=lambda x: x.start_index)

        DisplayOutput = [None for i in range(10)]
        for obj in ordered_message_objs:
            DisplayOutput = obj.InsertLetters(DisplayOutput)
        DisplayOutput = [" " if D == None else D for D in DisplayOutput]
        print(">" + (''.join(DisplayOutput)) + "<", end='\r')
    except:
        pass

class DisplayManager_class:
    def __init__(self):
        self.displayItems = []
    def printItems(self):
        DisplayOutput = [None for i in range(10)]
        for item in self.displayItems:
            DisplayOutput = item.InsertLetters(DisplayOutput)
        DisplayOutput = [" " if D == None else D for D in DisplayOutput]
        print(">" + (''.join(DisplayOutput)) + "<", end='\r')
    def Update(self, message):
        self.displayItems = split_text(message)


def main():
    # message = r'*s0-K:*d2-Morris-Takamoto*s8-:K' # Good example
    # message = r'*b0-K:*d2-Morris*s5-:*d6-Takamoto*s8-:K' #Good example
    # message = r'*b0-*d2-Morris*s5-:*d6-Takamoto*s8-:K' # Bad but working example
    message = r'*B0-K:*d2-Morris-Takamoto'  # working example

    message_objs = split_text(message)

    # display_items(message_objs)
    display_items_Loop(message_objs)
    # print("hihi")


if __name__ == "__main__":
    main()