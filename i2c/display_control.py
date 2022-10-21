import re
MAX_MSG_LEN = 10
class text_mode_item:
    def __init__(self,mode,index,message):
        self.mode= mode
        self.start_index = int(index)
        self.message = message
def split_text(message):
    item_list = []
    display_items = []
    split_items = re.split(r'(\*\w\d\-)',message)
    if split_items:
        for item in split_items:
            if item == '':
                continue
            item_list.append(item)
        for i in range(0,len(item_list),2):
            match = re.search(r'(\*)(\w)(\d)(\-)', item_list[i])
            display_items.append(text_mode_item(match.group(2),
                                                match.group(3),
                                                item_list[i+1]))
        for i in display_items:
            print("%s@%s : %s" %(i.mode, i.start_index, i.message))
        return display_items
    return None # bad message recieved

def DisplayMessage(message):
    global MAX_MSG_LEN
    DisplayOutput = [" " for i in range(10)]
    message_objects = split_text(message)
    if message_objects == None: # make sure message is OK
        return None
    while True:
        # print(data, end='\r')
        # for obj in message_objects message_objects =
        pass

        print(''.join(DisplayOutput), end= '\r')

def calc_spaces(message_objs):
    DisplayOutput = [None for i in range(10)]
    ModeSortKeys = {'s': 1,'d':2,'b':3} # custom dictionary
    ordered_message_objs = sorted(message_objs, key = lambda x : (ModeSortKeys[x.mode]))

    for obj in ordered_message_objs:
        for i in range(len(obj.message)):
            print("Before :")
            print(DisplayOutput)
            if ((obj.start_index + i) > MAX_MSG_LEN-1) or\
                (DisplayOutput[obj.start_index + i] != None):
                pass
            else:
                DisplayOutput[obj.start_index + i] = obj.message[i]
            # y[3:len(x)] = x
    print("Done")

def main():
    message = r'*s0-K:*d2-Morris-Takamoto*s8-:K'
    message_objs = split_text(message)
    calc_spaces(message_objs)
    print("done")
if __name__ == "__main__":
    main()