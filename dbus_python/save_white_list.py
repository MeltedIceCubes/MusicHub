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
    def __init__(self,alias, objPath):
        self.alias = alias
        self.objPath = objPath

def list_items(): # To use for listing saved devices.
    list_item = []
    try:
        with open(FILE_NAME, "r") as f:
            for l in f:
                line = l.strip()
                r = re.match("(.*),(.*)",line)
                list_item.append(WhiteListItem(r.group(1), r.group(2)))
    except FileNotFoundError:
        pass
    return list_item

def find_item(obj_list, target_alias = None, target_path = None):
    if target_alias == None and target_path == None:
        return None
    elif target_path == None:
        for obj in obj_list:
            if obj.alias == target_alias:
                return obj
    elif target_alias == None:
        for obj in obj_list:
            if obj.objPath == target_path:
                return obj
    return False

def delete_item(target_obj):
    pass


    #
    # try:
    #     with open(FILE_NAME, "r+" ) as f:
    #         f.seek(0,2)
    #         f.write("bitch\n")
    # except FileNotFoundError:
    #     logging.debug("file does not exist")
def main():
    # append_list("Bob"   + "," +  "/org/bluez/hci2/dev_AA_65_A6_E5_F0_5F")
    # append_list("Kye"   + "," +  "/org/bluez/hci1/dev_BB_65_A6_E5_F0_69")
    # append_list("Daria" + "," +  "/org/bluez/hci1/dev_CC_65_BB_E5_F0_5F")
    whitelistobj = find_item(list_items(), target_alias = "Kye")
    logging.debug("hihi")





if __name__ == "__main__":
    main()