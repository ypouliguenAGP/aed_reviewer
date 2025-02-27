import sqlite3
import datetime
from app.scripts.helpers import get_results
import os
import sys
import re

# ChangeLog

changes = {
    'pg': {},
    'st': {},
    'mfl': [],
}

def getDBLogs(pgs, sts, FOLDER_NAME):
    print(f'Openning {FOLDER_NAME}/tuba/log.db')
    conn_log = sqlite3.connect(f'{FOLDER_NAME}/tuba/log.db')
    cur_log = conn_log.cursor()
    # Protection Group
    cur_log.execute('select * from changelog where subsystem=="Protection Group"')
    results = get_results(cur_log)
    for row in results:
        if row['gid'] not in pgs:
            # print(f"PG {row['gid']} no longer exist - {datetime.datetime.fromtimestamp(row['tstamp'])}")
            continue
        if row['gid'] not in changes['pg']:
            changes['pg'][row['gid']] = []
        changes['pg'][row['gid']].append(row)

    # Server Type
    cur_log.execute('select * from changelog where subsystem=="Server Type"')
    results = get_results(cur_log)
    for row in results:
        if row['gid'] not in sts:
            print(f"ST {row['gid']} no longer exist - {datetime.datetime.fromtimestamp(row['tstamp'])}")
            continue
        if row['gid'] not in changes['st']:
            changes['st'][row['gid']] = []
        changes['st'][row['gid']].append(row)

    # Master Filter List
    cur_log.execute('select * from changelog where subsystem=="Master Filter Lists"')
    results = get_results(cur_log)
    for row in results:
        changes['mfl'].append(row)

    # System
    changes['system'] = []
    cur_log.execute('select * from changelog where subsystem=="System"')
    results = get_results(cur_log)
    for row in results:
        changes['system'].append(row)

    changes['backup'] = []
    cur_log.execute('select * from changelog where subsystem=="Backup"')
    results = get_results(cur_log)
    for row in results:
        changes['backup'].append(row)
    
    changes['aif'] = []
    cur_log.execute('select * from changelog where subsystem=="ATLAS Intelligence Feed"')
    results = get_results(cur_log)
    for row in results:
        changes['aif'].append(row)

    changes['cloud_signaling'] = []
    cur_log.execute('select * from changelog where subsystem=="Cloud Signaling"')
    results = get_results(cur_log)
    for row in results:
        changes['cloud_signaling'].append(row)

    changes['filesystem'] = []
    cur_log.execute('select * from changelog where subsystem=="Filesystem"')
    results = get_results(cur_log)
    for row in results:
        changes['filesystem'].append(row)
    
    conn_log.close()
    return changes



# def getSyslog():
#     print('Retriving syslogs')
#     # Retriving mgmt interface mac addresses
#     if not os.path.exists(f"{config.FOLDER_NAME}/syslog"):
#         print(f"File {config.FOLDER_NAME}/syslog does not exit")
#     with open(f"{config.FOLDER_NAME}/syslog") as f:
#         for line in f:
#             result = re.search("^(.+)\s(.+)\s(.+)\[\d\]: (.+)", line)
#             if result is None:
#                 print(line)
#                 continue
#             print(result.groups())
#     sys.exit(1)