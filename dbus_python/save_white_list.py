import logging
import re
logging.basicConfig(format = '%(message)s',level = logging.DEBUG)

FILE_NAME = "white_list.txt"

def append_list(payload, newline = True): # For newly saving devices
    try:
        with open(FILE_NAME, "a") as f:
            f.write(payload)
            if newline==True:
                f.write("\n")
    except FileNotFoundError:
        logging.debug("File does not exist")

class WhiteListItem:
    def __init__(self,alias, objPath, index):
        self.alias = alias
        self.objPath = objPath
        self.index = index

def list_items(): # To use for listing saved devices.
    list_item = []
    try:
        with open(FILE_NAME, "r") as f:
            for i, l in enumerate(f):
                line = l.strip()
                r = re.match("(.*),(.*)",line)
                list_item.append(WhiteListItem(r.group(1), r.group(2), i))
    except FileNotFoundError:
        pass
    return list_item

def find_item(target_alias = None, target_path = None):
    if target_alias == None and target_path == None:
        return None
    # try:
    with open(FILE_NAME, "r") as f:
        for i, l in enumerate(f):
            line = l.strip()
            r = re.match("(.*),(.*)", line)
            if target_alias != None and target_alias == r.group(1):
                return WhiteListItem(r.group(1),r.group(2),i)
            elif target_path != None and target_path == r.group(2):
                return WhiteListItem(r.group(1),r.group(2), i)
    # except FileNotFoundError:
    #     pass
    return None

def delete_item(item :WhiteListItem):
    if item is None:
        return False
    try:
        with open(FILE_NAME, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            for i,line, in enumerate(lines):
                if i != item.index:
                    f.write(line)
        # print(f.readlines()[index])
        return True
    except FileNotFoundError:
        pass

def main():
    # append_list("Bob"   + "," +  "/org/bluez/hci2/dev_AA_65_A6_E5_F0_5F")
    # append_list("Kye"   + "," +  "/org/bluez/hci1/dev_BB_65_A6_E5_F0_69")
    # append_list("Daria" + "," +  "/org/bluez/hci1/dev_CC_65_BB_E5_F0_5F")
    
    
    whitelistobj = find_item(target_alias = "Kye")
    x = delete_item(whitelistobj)
    print(x)
    logging.debug("hihi")





if __name__ == "__main__":
    main()