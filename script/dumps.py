import os
import config
import re
import sys


def processPacketDump(pg_id):

    if not os.path.exists(f"{config.FOLDER_NAME}/stats/dumps/{pg_id}.log"):
        print(f"File {config.FOLDER_NAME}/stats/dumps/{pg_id}.log does not exit")

        return False

    entries = []        
    with open(f"{config.FOLDER_NAME}/stats/dumps/{pg_id}.log") as f:
        position = 1
        entry = {'#': position}
        for line in f:
            if line == "\n":
                entries.append(entry)
                position += 1
                # print(entry)
                entry = {'#': position}
                continue
            if 'bytes RX on' in line:
               result = re.search("^([0-9]+) bytes RX.*", line)
               if result is None:
                   continue
               entry['len'] = result.groups()[0]
            elif line.startswith('  ip'):
                if '(TCP)' in line or '(UDP)' in line:
                    result = re.search("ip ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) +\(([0-9]{1,5})\) .+ ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) +\(([0-9]{1,5})\) proto +((?:6|17))", line)
                    if result is None:
                        result = re.search("ip ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) .+ ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) +proto +([0-9]{1,3})", line)
                        entry['src_ip'] = result.groups()[0]
                        entry['dst_ip'] = result.groups()[1]
                        entry['proto'] = result.groups()[2]
                        continue   
                    entry['src_ip'] = result.groups()[0]
                    entry['src_port'] = result.groups()[1]
                    entry['dst_ip'] = result.groups()[2]
                    entry['dst_port'] = result.groups()[3]
                    entry['proto'] = result.groups()[4]
                else:
                    result = re.search("ip ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) .+ ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) +proto +([0-9]{1,3})", line)
                    entry['src_ip'] = result.groups()[0]
                    entry['dst_ip'] = result.groups()[1]
                    entry['proto'] = result.groups()[2]
            elif line.startswith(' tcp '):
                result = re.search("^ tcp ((:?.|[A-Z]){8}) .+", line)
                entry['tcp_flags'] = result.groups()[0].replace('.', '')
            elif ' by ' in line:
                result = re.search("^((:?pass|drop)) by (:?pktengine|countermeasure|blacklist)", line)
                entry['action'] = result.groups()[0]
            elif 'geo address matches' in line:
                result = re.search(" ([A-Z]{2}) +", line)
                entry['src_country'] = result.groups()[0]
    return entries


def packetStats(entries):
    srcIPsPPS = packetElementStats(entries, 'src_ip', 'pps')
    srcIPsBPS = packetElementStats(entries, 'src_ip', 'bps')
    dstIPsPPS = packetElementStats(entries, 'dst_ip', 'pps')
    dstIPsBPS = packetElementStats(entries, 'dst_ip', 'bps')
    dstProtoPPS = packetElementStats(entries, 'proto', 'pps')
    dstProtoBPS = packetElementStats(entries, 'proto', 'bps')
    srcPortPPS = packetElementStats(entries, 'src_port', 'pps')
    srcPortBPS = packetElementStats(entries, 'src_port', 'bps')
    dstPortPPS = packetElementStats(entries, 'dst_port', 'pps')
    dstPortBPS = packetElementStats(entries, 'dst_port', 'bps')
    countryPPS = packetElementStats(entries, 'src_country', 'pps')
    countryBPS = packetElementStats(entries, 'src_country', 'bps')
    actionPPS = packetElementStats(entries, 'action', 'pps')
    actionBPS = packetElementStats(entries, 'action', 'bps')
    return {
        'src_ip': {
            'pps': srcIPsPPS,
            'bps': srcIPsBPS,
        }, 
        'dst_ip': {
            'pps': dstIPsPPS,
            'bps': dstIPsBPS,
        },
        'proto': {
            'pps': dstProtoPPS,
            'bps': dstProtoBPS,
        },
        'src_port': {
            'pps': srcPortPPS,
            'bps': srcPortBPS,
        },
        'dst_port': {
            'pps': dstPortPPS,
            'bps': dstPortBPS,
        },
        'src_country': {
            'pps': countryPPS,
            'bps': countryBPS,
        },
        'action': {
            'pps': actionPPS,
            'bps': actionBPS,
        },
    }



# def packetElementStats(entries, element_name='src_ip'):
#     srcElements = {}
#     for entry in entries:
#         if element_name not in entry:
#             continue
#         if entry[element_name] not in srcElements:
#             srcElements[entry[element_name]] = {'p':0, 'b':0}
#         srcElements[entry[element_name]]['p'] += 1
#         srcElements[entry[element_name]]['b'] += int(entry['len'])
#     return srcElements

def packetElementStats(entries, element_name, unit='bps'):
    srcElements = {}
    for entry in entries:
        if element_name not in entry:
            continue
        if 'port' in element_name:
            entry_name = f"{config.PROTO[int(entry['proto'])]}/{entry[element_name]}"
        else:
            entry_name = entry[element_name]
        if entry_name not in srcElements:
            srcElements[entry_name] = 0
        if unit == 'pps':
            srcElements[entry_name] += 1
        else:
            srcElements[entry_name] += int(entry['len'])

    
    selected_elements = []
    for srcElement in srcElements:
        selected_elements.append((srcElement, srcElements[srcElement]))
    selected_elements.sort(key=lambda x: x[1], reverse=True)
    if len(selected_elements) <= config.MAX_DUMPS_STATS_ELEMENTS:
        return selected_elements
    # Calculating others count
    total_other = 0
    for selected_element in selected_elements[config.MAX_DUMPS_STATS_ELEMENTS:len(selected_elements)]:
        total_other += selected_element[1]
    return selected_elements[:config.MAX_DUMPS_STATS_ELEMENTS] + [('others', total_other)]




    return srcElements