import sqlite3
import json
import subprocess
import re
import datetime
from changelog import getDBLogs
from helpers import get_results, intToBool, get_results_list
from protections import getProtectionDetails
from dumps import processPacketDump, packetStats
from aed_config import processSavedConfig
import config
import argparse
import os
import copy
import sys


parser = argparse.ArgumentParser(description='Basic argparse example.')
# have at least one argument
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('--ressource',
                    '-r',
                    dest='ressource',
                    default=None,
                    required=True,
                    help='Diagfile Folder')

requiredNamed.add_argument('--export',
                    '-e',
                    dest='export',
                    default='exports/default/',
                    help='Export Folder')


# parse the arguments
args = parser.parse_args()
config.FOLDER_NAME = args.ressource

if args.export[-1] != '/':
    config.EXPORT_PATH = args.export+'/'
else:
    config.EXPORT_PATH = args.export



heath = {
    'disk': {},
}

CMD = f"grep 'Total_LBAs_Written' -A 7 {config.FOLDER_NAME}/smartctl_sdc.txt"
p = subprocess.run(CMD, shell=True, stdout=subprocess.PIPE)
for entry in p.stdout.decode().splitlines():
    heath['disk'][entry.split(' ')[1]] = ' '.join(entry.split(' ')[2:]).lstrip()
print(json.dumps(heath, indent=2))


inbound = {
  "denied-hosts": [],
  "allowed-hosts": [],
  "denied-countries": [],
  "denied-domains": [],
  "denied-urls": [],
  "mfl": {} 
}

outbound = {
  "denied-hosts": [],
  "allowed-hosts": [],
  "denied-countries": [],
}

conn_cfg = sqlite3.connect(f'{config.FOLDER_NAME}/tuba/cfg.db')
cur_cfg = conn_cfg.cursor()

conn_events = sqlite3.connect(f'{config.FOLDER_NAME}/tuba/events.db')
cur_events = conn_events.cursor()

# Deny and Allow list
cur_cfg.execute('SELECT * from pg_host_black_white_list')
results = get_results(cur_cfg)
for row in results:
    obj = {
        "annotation": row['annotation'], 
        "cid": [
            -1
        ], 
        "hostAddress": row['host_addr'], 
        "pgid": [
            row['pgid']
        ], 
        "updateTime": row['update_tstamp']
    }
    if row['drop_pass'] == 'drop':
        inbound['denied-hosts'].append(obj)
    else:
        inbound['allowed-hosts'].append(obj)



# OTF Deny and Allow list
cur_cfg.execute('SELECT * from otf_host_black_white_list')
results = get_results(cur_cfg)
for row in results:
    obj = {
        "annotation": row['annotation'], 
        "hostAddress": row['host_addr'], 
        "updateTime": row['update_tstamp']
    }
    if row['drop_pass'] == 'drop':
        outbound['denied-hosts'].append(obj)
    else:
        outbound['allowed-hosts'].append(obj)


# Deny list Country
cur_cfg.execute('SELECT * from pg_geoip_black_list_countries')
results = get_results(cur_cfg)
for row in results:
    inbound["denied-countries"].append(
    {
      "annotation": row['annotation'], 
      "country": row['country'], 
      "pgid": row['pgid'], 
      "updateTime": row['update_tstamp']
    })


cur_cfg.execute('SELECT * from otf_geoip_black_list_countries')
results = get_results(cur_cfg)
for row in results:
    outbound["denied-countries"].append(
    {
      "annotation": row['annotation'], 
      "country": row['country'], 
      "updateTime": row['update_tstamp']
    })

# MFL
cur_cfg.execute('SELECT * from filter_list')
results = get_results(cur_cfg)
mfl = {}
inbound["mfl"]['v4'] = []
inbound["mfl"]['v6'] = []
for row in results:
    for entry in row['v4'].splitlines():
        inbound["mfl"]['v4'].append(entry)
    for entry in row['v6'].splitlines():
        inbound["mfl"]['v6'].append(entry)


# PGs & STs
cur_cfg.execute('select * from pg join pg_prefix ON pg.pgid=pg_prefix.pgid;')
results = get_results(cur_cfg)
pgs = {}
sts = {}
for row in results:
    if row['pgid'] not in pgs:
        pgs[row['pgid']] = {
            "name": row['name'],
            "active": row['active'],
            "description": row['description'],
            "security_level": row['security_level'],
            "server_type": row['server_type'],
            "prefixes": [row['prefix']],
            "is_ipv6": row['is_ipv6'],
            "create_tstamp": row['create_tstamp'],
            "alert_thresholds": {},
            "pgid": row['pgid'],
        }
    if row['server_type'] not in sts:
        sts[row['server_type']] = copy.deepcopy(config.ST_SHELL)
        sts[row['server_type']]['server_type'] = row['server_type']
    else:
        pgs[row['pgid']]['prefixes'].append(row['prefix'])

#  Profile Capture
cur_cfg.execute('select pg.pgid,histogram_config.server_type,histogram_config.enabled,histogram_config.start_time,histogram_config.stop_time from histogram_config join pg ON pg.server_type=histogram_config.server_type')
results = get_results(cur_cfg)
for row in results:
    if row['server_type'] not in sts:
        continue
    if row['stop_time'] is None:
        sts[row['server_type']]['profile_capture'] = None
        continue
    sts[row['server_type']]['profile_capture'] = {
        'start_time': row['start_time'],
        'stop_time': row['stop_time'],
        'duration': row['stop_time']-row['start_time'],
        'ongoing': intToBool(row['enabled'])
    }
    pgs[row['pgid']]['profile_capture'] = sts[row['server_type']]['profile_capture']

cur_cfg.execute('select st.server_type,st.parent_type,st.server_name,cid.cid from st join cid ON st.server_type=cid.id')
results = get_results(cur_cfg) 
for row in results:
    if row['server_type'] not in sts:
        continue
    sts[row['server_type']]['parentType'] = row['parent_type']
    sts[row['server_type']]['serverName'] = row['server_name']
    sts[row['server_type']]['cid'] = row['cid']
    

# Alert Bandwidth Thresholds

cur_cfg.execute('select * from pg_bandwidth_alert_config')
results = get_results(cur_cfg)
for row in results:
    if row['pgid'] not in pgs:
        print(f"{row['pgid']} not in pgs")
        continue
    if row['local_alert_type'] == 200:
        pgs[row['pgid']]['alert_thresholds']['total'] = {
            'mode': config.BANDWIDTH_ALERT_MODES[row['enable_mode']],
            'bps': row['threshold_bps'],
            'pps': row['threshold_pps'],
        }
    elif row['local_alert_type'] == 203:
        pgs[row['pgid']]['alert_thresholds']['drop'] = {
            'mode': config.BANDWIDTH_ALERT_MODES[row['enable_mode']],
            'bps': row['threshold_bps'],
            'pps': row['threshold_pps'],
        }
    elif row['local_alert_type'] == 201:
        pgs[row['pgid']]['alert_thresholds']['botnet'] = {
            'mode': config.BANDWIDTH_ALERT_MODES[row['enable_mode']],
            'bps': row['threshold_bps'],
            'pps': row['threshold_pps'],
        }


cur_events.execute('select * from pg_baselines')
results = get_results(cur_events)
for row in results:
    if row['pgid'] not in pgs:
        print(f"{row['pgid']} not in pgs")
        continue
    if row['local_alert_type'] == 200:
        type = 'total'
    elif row['local_alert_type'] == 201:
        type = 'botnet'
    elif row['local_alert_type'] == 203:
        type = 'drop'

    pgs[row['pgid']]['alert_thresholds'][type]['baseline'] = {
        'days': row['days'],
        'bps': row['bps'],
        'pps': row['pps'],
    }


CLASS_ID = {
    98: 'total',
    102: 'blocked',
}

UNIT_CONVERSION = {
    '': 1,
    'K': 1000,
    'M': 1000*1000,
    'G': 1000*1000*1000,
}

cur_events.execute('select * from user_alerts ORDER BY start_time ASC')
results = get_results(cur_events)
value_pattern = r" was ([\d]+(?:\.[\d]{2}){0,1}) ([K|M|G]{0,1})([a-z]+)\."
# print(pgs)
for row in results:
    
    if row['classid'] == 98:
        type = 'total'
    elif row['classid'] == 100:
        type = 'botnet'
    elif row['classid'] == 102:
        type = 'drop'
    elif row['classid'] == 103:
        type = 'automation'
    else:
        continue
    
    if row['pgid'] is None:
        # print(f"PG er exist - {datetime.datetime.fromtimestamp(row['start_time'])}")
        continue
    if row['pgid'] not in pgs:
        print(f"{row['pgid']} not in pgs")
        continue
    if 'alerts' not in pgs[row['pgid']]:
        pgs[row['pgid']]['alerts'] = {}
        if row['pgid'] == 526:
            print('Adding Alerts')
    if type not in pgs[row['pgid']]['alerts']:
        if row['pgid'] == 526:
            print(f'Adding {type}')
        pgs[row['pgid']]['alerts'][type] = []

    if row['pgid'] == 526:
        print(f'Alerts: {row}')
    if type == 'automation':
        if row['pgid'] == 526:
            print(len(pgs[row['pgid']]['alerts'][type]))
        pgs[row['pgid']]['alerts'][type].append({
            'stop_time':row['stop_time'],
            'start_time':row['start_time'],
            'detail': row['info']
        })
        if row['pgid'] == 526:
            print(len(pgs[row['pgid']]['alerts'][type]))
        continue
    
    

    
    result = re.search(value_pattern, row['info'])
    try:
        value = float(result.group(1))
        pgs[row['pgid']]['alerts'][type].append({
            # 'start_time': datetime.datetime.fromtimestamp(row['start_time']),
            # 'stop_time': datetime.datetime.fromtimestamp(row['stop_time']),
            'stop_time':row['stop_time'],
            'start_time':row['start_time'],
            'rate': value*UNIT_CONVERSION[result.group(2)],
            'unit': result.group(3)
        })
    except:
        print(f"Error rendering user_alert {row['id']}")
        print(row)
        continue



sts = getProtectionDetails(cur_cfg, pgs, sts)


global_alerting = {}
cur_cfg.execute('select * from baseline_alerting_config')
results = get_results(cur_cfg)
for row in results:
    if row['local_alert_type'] == 200:
        type = 'total'
    elif row['local_alert_type'] == 201:
        type = 'botnet'
    elif row['local_alert_type'] == 203:
        type = 'drop'
    
    global_alerting[type] = {
        'enabled': intToBool(row['enabled']),
        'percent': row['percent'],
        'ignore_bps': row['ignore_bps'],
        'ignore_pps': row['ignore_pps']
    }





# Notification Dest

notification_dests = {
    'syslog': [],
    'snmp': [],
    'email': []
}


cur_cfg.execute('select * from notification_dest')
results = get_results(cur_cfg)

for row in results:

    cur_cfg.execute(f"select type from notification_config where ndid={row['id']}")
    notification_config_results = get_results_list(cur_cfg)
    types_human = []
    for type_id in notification_config_results:
        types_human.append(config.NOTIFICATION['type'][type_id])

    obj = {
        'id': row['id'],
        'type': row['type'],
        'creator': row['creator'],
        'tstamp': row['tstamp'],
        'types': types_human
    }
    

    if row['syslog_host'] is not None:
        for key in row:
            if key.startswith("syslog"):
                if key == "syslog_severity":
                    obj[key[7:]] = config.NOTIFICATION['severity'][row[key]]
                    continue
                if key == "syslog_facility":
                    obj[key[7:]] = config.NOTIFICATION['facility'][row[key]]
                    continue
                obj[key[7:]] = row[key]
        notification_dests['syslog'].append(obj)
    elif row['snmp_host'] is not None:
        for key in row:
            if key.startswith("snmp"):
                obj[key[5:]] = row[key]
        notification_dests['snmp'].append(obj)
    elif row['email_to'] is not None:
        for key in row:
            if key.startswith("email"):
                obj[key[6:]] = row[key]
        notification_dests['email'].append(obj)


# HTTP PROXY
cur_cfg.execute('select * from http_proxy')
results = get_results(cur_cfg)
http_proxy = []
for row in results:
    if row['host'] is not None:
        http_proxy.append(row)


# Global Config
cur_cfg.execute('select * from registry')
results = get_results(cur_cfg)
global_config = {}
for row in results:
    global_config[row['key']] = row['json_object']

# Interfaces
cur_cfg.execute('select * from interfaces')
results = get_results(cur_cfg)
interfaces = {}
for row in results:
    interfaces[row['gid']] = row
    if row['iface_alert_type'] == 2:
        interfaces[row['gid']]['alert_enabled'] = True
    else:
        interfaces[row['gid']]['alert_enabled'] = False
    interfaces[row['gid']]['enable_port_mirroring'] = intToBool(row['enable_port_mirroring'])



# Feeds

conn_feed = sqlite3.connect(f'{config.FOLDER_NAME}/tuba/feed.db')
cur_feed = conn_feed.cursor()
cur_feed.execute('select * from webcrawler_engine')
results = get_results(cur_feed)
webcrawlers = {}
webcrawlers_enabled = 0
for row in results:
    webcrawlers[row['crawler_id']] = {
        'name': row['engine_name'],
        'enabled': intToBool(row['enabled'])
    }
    if webcrawlers[row['crawler_id']]['enabled']:
        webcrawlers_enabled += 1
print(f"Web Crawlers enabled: {round(webcrawlers_enabled/len(webcrawlers)*100)}%")


conn_feed.close()



# print(json.dumps(inbound, indent=2))
# print(json.dumps(pgs, indent=2))
# # print(json.dumps(global_alerting, indent=2))
# # print(json.dumps(global_config, indent=2))


conn_cfg.close()
conn_events.close()

changes = getDBLogs(
    list(pgs.keys()),
    list(sts.keys()),
    )


# Retriving Interfaces and IP Access
ipAccesses = processSavedConfig()

# getSyslog()

# Format PG List as table
pgs_formated = {
    "protection-groups": []
}
for pg in pgs:
    pgs_formated["protection-groups"].append(pgs[pg])

def formater(name, source):
    formated = {f"{name}": []}
    for key in source:
        formated[f"{name}"].append(source[key])
    return formated


# Writting to Files

if not os.path.exists(config.EXPORT_PATH):
    os.makedirs(config.EXPORT_PATH)

if not os.path.exists(f'{config.EXPORT_PATH}{config.LEGACY}'):
    os.makedirs(f'{config.EXPORT_PATH}{config.LEGACY}')

with open(f"{config.EXPORT_PATH}{config.LEGACY}export.pg", "w") as outfile:
    json.dump(formater("protection-groups",pgs), outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}pgs.json", "w") as outfile:
    json.dump(pgs, outfile, indent=config.EXPORT_INDENT)


with open(f"{config.EXPORT_PATH}{config.LEGACY}export.st", "w") as outfile:
    json.dump(formater("server-types",sts), outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}sts.json", "w") as outfile:
    json.dump(sts, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}server_types.json", "w") as outfile:
    json.dump(sts, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}{config.LEGACY}export.ibh", "w") as outfile:
    json.dump({"denied-hosts": inbound['denied-hosts']}, outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}{config.LEGACY}export.ibc", "w") as outfile:
    json.dump({"denied-countries": inbound['denied-countries']}, outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}{config.LEGACY}export.iwh", "w") as outfile:
    json.dump({"allowed-hosts": inbound['allowed-hosts']}, outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}{config.LEGACY}export.mfl", "w") as outfile:
    json.dump(inbound['mfl'], outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}/master_filter_list.json", "w") as outfile:
    json.dump(inbound['mfl'], outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}{config.LEGACY}export.obh", "w") as outfile:
    json.dump({"denied-hosts": outbound['denied-hosts']}, outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}{config.LEGACY}export.ibc", "w") as outfile:
    json.dump({"denied-countries": outbound['denied-countries']}, outfile, indent=config.EXPORT_INDENT)
with open(f"{config.EXPORT_PATH}{config.LEGACY}export.owh", "w") as outfile:
    json.dump({"allowed-hosts": outbound['allowed-hosts']}, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}interfaces.json", "w") as outfile:
    json.dump(interfaces, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}changes.json", "w") as outfile:
    json.dump(changes, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}webcrawlers.json", "w") as outfile:
    json.dump(webcrawlers, outfile, indent=config.EXPORT_INDENT)

# Legacy
with open(f"{config.EXPORT_PATH}{config.LEGACY}export.at", "w") as outfile:
    json.dump(global_alerting, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}global_alerting.json", "w") as outfile:
    json.dump(global_alerting, outfile, indent=config.EXPORT_INDENT)
    

with open(f"{config.EXPORT_PATH}global.json", "w") as outfile:
    json.dump(global_config, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}http_proxy.json", "w") as outfile:
    json.dump(http_proxy, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}notification_dests.json", "w") as outfile:
    json.dump(notification_dests, outfile, indent=config.EXPORT_INDENT)

with open(f"{config.EXPORT_PATH}ip_access.json", "w") as outfile:
    json.dump(ipAccesses, outfile, indent=config.EXPORT_INDENT)

if not os.path.exists(f"{config.EXPORT_PATH}/stats/dumps/"):
    os.makedirs(f"{config.EXPORT_PATH}/stats/dumps/")
for pg_id in pgs:
    entries = processPacketDump(pg_id)
    print(f"{len(entries)} Packets for PG {pg_id}")
    with open(f"{config.EXPORT_PATH}/stats/dumps/{pg_id}.json", "w") as outfile:
        json.dump(entries, outfile, indent=config.EXPORT_INDENT)
    with open(f"{config.EXPORT_PATH}/stats/dumps/{pg_id}_stats.json", "w") as outfile:
        json.dump(packetStats(entries), outfile, indent=config.EXPORT_INDENT)