import os
import re
import sys
from .config import NETMASKS

def processSavedConfig(FOLDER_NAME):
    global_config = {}

    print('Retriving mgmt interface mac addresses')
    # Retriving mgmt interface mac addresses
    if not os.path.exists(f"{FOLDER_NAME}/ifconfig.txt"):
        print(f"File {FOLDER_NAME}/config_show_saved does not exit")
    int_cursor = None
    interfaces = {}       
    with open(f"{FOLDER_NAME}/ifconfig.txt") as f:
        for line in f:
            # print(line)
            if re.match("^ext[0-9] ", line):
                break
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
            if "Inet:" in line:
                print(line)
                result = re.search("Inet: ((?:[0-9]+\.){3}[0-9]+) netmask ((?:[0-9]+\.){3}[0-9]+)", line)
                if result is None:
                    print('IP not found')
                    continue
                interfaces[int_cursor]['ip'] = f"{result.group(1)}/{NETMASKS[result.group(2)]}"
        print(interfaces)

    
    
    

    print('Retriving config_show_saved')
    if not os.path.exists(f"{FOLDER_NAME}/config_show_saved"):
        print(f"File {FOLDER_NAME}/config_show_saved does not exit")
    ipAccess = {}
    ipRoutes = {}
    with open(f"{FOLDER_NAME}/config_show_saved") as f:
        for line in f:
            # print(line)
            if line.startswith('ip access add '):
                ipAccessProcess(line, ipAccess, interfaces)
            if line.startswith('ip route add '):
                ipRouteProcess(line, ipRoutes, interfaces)
            if line.startswith('system name set '):
                result = re.search("^system name set (.+)", line)
                if result is not None:
                    global_config['system_name'] = result.group(1)
            if line.startswith('system timezone set '):
                result = re.search("^system timezone set (.+)", line)
                if result is not None:
                    global_config['timezone'] = result.group(1)
            if line.startswith('system idle set '):
                result = re.search("^system idle set (.+)", line)
                if result is not None:
                    global_config['system_idle'] = result.group(1)
            
            if line.startswith('services ntp server add '):
                result = re.search("^services ntp server add (.+)", line)
                if result is not None:
                    if 'ntp' not in global_config:
                        global_config['ntp'] = result.group(1)
                    else:
                        global_config['ntp'] += ' '+result.group(1)
            if line.startswith('services dns server add '):
                result = re.search("^services dns server add (.+)", line)
                if result is not None:
                    if 'dns' not in global_config:
                        global_config['dns'] = result.group(1)
                    else:
                        global_config['dns'] += ' '+result.group(1)

            if line.startswith('services backup server set '):
                result = re.search("^services backup server set (.+)", line)
                if result is not None:
                    global_config['backup_server'] = result.group(1)
            if line.startswith('services backup schedule full '):
                result = re.search("^services backup schedule full (.+)", line)
                if result is not None:
                    global_config['backup_full'] = result.group(1)
            if line.startswith('services backup schedule incremental '):
                result = re.search("^services backup schedule incremental (.+)", line)
                if result is not None:
                    global_config['backup_incremental'] = result.group(1)
            if line.startswith('services aaa max_login_failures set '):
                result = re.search("^services aaa max_login_failures set (.+)", line)
                if result is not None:
                    global_config['max_login_failures'] = result.group(1)
            if line.startswith('services aaa password_length min '):
                result = re.search("^services aaa password_length min (.+)", line)
                if result is not None:
                    global_config['password_length_min'] = result.group(1)

    # Banner
    banner_flag = False
    global_config['banner'] = ''
    with open(f"{FOLDER_NAME}/config_show_saved") as f:
        for line in f:
            if line.startswith('system banner set'):
                banner_flag = True
                continue
            if line.startswith('services '):
                banner_flag = False
                break
            if banner_flag:
                global_config['banner'] += line+'\n'
            

                

    licenses = retrieve_license(FOLDER_NAME)
    hardware = retrieve_hardware(FOLDER_NAME)



    return interfaces, ipAccess, ipRoutes, licenses, hardware, global_config


# Retrive License

def retrieve_license(FOLDER_NAME):
    licenses = []
    with open(f"{FOLDER_NAME}/licenses.txt") as f:
        for line in f:
            if re.match("dmvd tmp dir contents", line):
                break
            if re.match("^system license ", line):
                continue
            licenses.append(line)
    return licenses


def retrieve_hardware(FOLDER_NAME):
    hardware = []
    with open(f"{FOLDER_NAME}/hardware.txt") as f:
        for line in f:
            hardware.append(line)
    return hardware



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

def ipRouteProcess(line, ipRoutes, interfaces):
    result = re.search("^ip route add ([^\s]+) ([^\s]+) ([^\s]+)", line)
    if result is None:
        return ipRoutes
    if result.groups()[1] not in ipRoutes:
        ipRoutes[result.groups()[1]] = []
    for int in interfaces:
        if interfaces[int]['hw'] == result.groups()[2]:
            true_int = int
   
    ipRoutes[result.groups()[1]].append({
        'int': true_int,
        'destination': result.groups()[0]
    })
    return ipRoutes

