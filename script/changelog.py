import sqlite3
import datetime
from helpers import get_results
import config 

# ChangeLog

changes = {
    'pg': {},
    'st': {},
    'mfl': [],
}

def getLogs(pgs, sts):
    conn_log = sqlite3.connect(f'{config.RESSOURCES_PATH}log.db')
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

    conn_log.close()
    return changes