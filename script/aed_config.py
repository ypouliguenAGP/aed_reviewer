import os
import config
import re
import sys


def processSavedConfig():
    print('Retriving mgmt interface mac addresses')
    # Retriving mgmt interface mac addresses
    if not os.path.exists(f"{config.FOLDER_NAME}/ifconfig.txt"):
        print(f"File {config.FOLDER_NAME}/config_show_saved does not exit")
    int_cursor = None
    interfaces = {}       
    with open(f"{config.FOLDER_NAME}/ifconfig.txt") as f:
        for line in f:
            # print(line)
            if re.match("^mgt[0-9] ", line):
                result = re.search("^(mgt[0-9]) ", line)
                int_cursor = result.groups()[0]
                interfaces[int_cursor] = {}
                continue
            if "Hardware:" in line:
                result = re.search("Hardware: ((?:[0-9A-F]{1,2}:){5}(?:[0-9A-F]{1,2}))", line)
                if result is None:
                    continue
                interfaces[int_cursor]['hw'] = result.groups()[0]
            if "Status:" in line:
                result = re.search("Status: (.*)", line)
                if result is None:
                    continue
                interfaces[int_cursor]['state'] = result.groups()[0]
    

    print('Retriving config_show_saved')
    if not os.path.exists(f"{config.FOLDER_NAME}/config_show_saved"):
        print(f"File {config.FOLDER_NAME}/config_show_saved does not exit")
    ipAccess = {}
    with open(f"{config.FOLDER_NAME}/config_show_saved") as f:
        for line in f:
            # print(line)
            if line.startswith('ip access add '):
                ipAccessProcess(line, ipAccess, interfaces)

    return ipAccess

def ipAccessProcess(line, ipAccess, interfaces):
    result = re.search("^ip access add ([a-z]{3,10}) (.+) (.+)", line)
    if result is None:
        return ipAccess
    if result.groups()[0] not in ipAccess:
        ipAccess[result.groups()[0]] = []
    if result.groups()[1] != 'all':
        for int in interfaces:
            if interfaces[int]['hw'] == result.groups()[1]:
                true_int = int
    else:
        true_int = result.groups()[1]
    ipAccess[result.groups()[0]].append({
        'int': true_int,
        'source': result.groups()[2]
    })
    return ipAccess