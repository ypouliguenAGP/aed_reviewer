import sqlite3
import datetime
from helpers import get_results, intToBool
import config


def ratesGenericDetails(cursor, sts, table_name, api_name):
    cursor.execute(f'select * from {table_name}')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]][api_name] = {
            "bps": row['bps'],
            "enabled": intToBool(row['enabled']),
            "pps": row['pps']
        }
    return sts

def boolGenericDetails(cursor, sts, table_name, api_name):
    cursor.execute(f'select * from {table_name}')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]][api_name] = { "enabled": intToBool(row['enabled']) }
    return sts


def regexDetails(cursor, sts, table_name, api_name):
    cursor.execute(f'select * from {table_name}')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]][api_name] = { "statement": [] }
        if row['statement'] is None:
            continue
        for entry in row['statement'].splitlines():
             sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]][api_name]['statement'].append(entry)
    return sts

def getProtectionDetails(cursor, pgs, sts):
    
    # Filter
    cursor.execute('select * from cm_filter')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['filter'] = { "statement": [] }
        for entry in row['statement'].splitlines():
             sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['filter']['statement'].append(entry)

    
    ########### Rates

    sts = ratesGenericDetails(cursor, sts, 'cm_fragmentation', 'fragmentation')
    sts = ratesGenericDetails(cursor, sts, 'cm_udp_flood', 'udpFlood')
    sts = ratesGenericDetails(cursor, sts, 'cm_zombie', 'zombie')

    # ICMP
    cursor.execute('select * from cm_detect')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['detectIcmp'] = {
            "bps": row['icmp_bps'],
            "enabled": intToBool(row['icmp_enabled']),
            "pps": row['icmp_rate']
        }
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['detectSyn'] = {
            "synAckDeltaRate": row['syn_ack_delta_rate'],
            "enabled": intToBool(row['syn_enabled']),
            "synRate": row['syn_rate']
        }

    # Flex Zombie
    cursor.execute('select * from cm_flex_zombie_config')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if 'zombie' not in sts[row['server_type']]['protectionLevels']['common']:
            sts[row['server_type']]['protectionLevels']['common']['zombie'] = {
                'flexible': {}
        }
        sts[row['server_type']]['protectionLevels']['common']['zombie']['flexible'][f"{row['zombie_id']}"] = {
            "description": row['description'],
            "filter": [f"{row['filter']}"],
        }        


    cursor.execute('select * from cm_flex_zombie_rate')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if 'flexible' not in sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['zombie']:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['zombie']['flexible'] = {}
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['zombie']['flexible'][f"{row['zombie_id']}"] = {
            "bps": row['bps'],
            "enabled": intToBool(row['enabled']),
            "pps": row['pps']
        }


    



    
    
    
    
    
    # DNS  Regex
    sts = regexDetails(cursor, sts, 'cm_dns_regex', 'dnsRegex')
    # cursor.execute('select * from cm_dns_regex')
    # results = get_results(cursor)
    # for row in results:
    #     if row['server_type'] not in sts:
    #         continue
    #     sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsRegex'] = { "statement": [] }
    #     if row['statement'] is None:
    #         continue
    #     for entry in row['statement'].splitlines():
    #          sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsRegex']['statement'].append(entry)

    

    # DNS Auth
    sts = boolGenericDetails(cursor, sts, 'cm_dns_auth', 'dnsAuth')
        
    # DNS Malform
    sts = boolGenericDetails(cursor, sts, 'cm_dns_malform', 'dnsMalform')
    
    # DNS dnsNonexistent
    try:
        cursor.execute('select * from cm_dnszap')
        results = get_results(cursor)
        for row in results:
            if row['server_type'] not in sts:
                continue
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsNonexistent'] = {
                    "enabled": intToBool(row['enabled']),
                    "enforced": intToBool(row['enforced'])
                }
    except:
        print('No DNS ZAP')
        
    # DNS Amp
    try:
        cursor.execute('select * from cm_dnsdaze_ra')
        results = get_results(cursor)
        for row in results:
            if row['server_type'] not in sts:
                continue
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsAmp'] = {  "enabled": intToBool(row['enabled']) }
    except:
        print('No DNS daze_ra')

    # DNS Rate
    cursor.execute('select * from cm_dns_query')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if row['enabled'] == 0:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsQuery'] = { 'rate': 0 }
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsQuery'] = { 'rate': row['rate'] }
        
    # DNS NXDomain
    cursor.execute('select * from cm_dns_nxdomain')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if row['enabled'] == 0:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsNxdomain'] = { 'rate': 0 }
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['dnsNxdomain'] = { 'rate': row['rate'] }

    ##### SIP
    cursor.execute('select * from cm_sip_request')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if row['enabled'] == 0:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['sipRequest'] = { 'rate': 0 }
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['sipRequest'] = { 'rate': row['rate'] }

    sts = boolGenericDetails(cursor, sts, 'cm_sip_malform', 'sipMalform')


    #### TCP
    # SYN
    cursor.execute('select * from cm_syn_auth')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['synAuth'] = {
            'enabled': intToBool(row['enabled']),
            'automationEnabled': intToBool(row['automation_enabled']),
            'automationThreshold': row['automation_threshold'],
            'httpAuthEnabled': intToBool(row['http_auth_enabled']),
            'javascriptEnabled': intToBool(row['javascript_enabled']),
            'outOfSeqEnabled': intToBool(row['out_of_seq_enabled']),
            'softResetEnabled': intToBool(row['soft_reset_enabled']),
            'dstPorts': []
         }
    
    cursor.execute('select * from cm_syn_auth_ports')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if 'synAuth' not in sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]:
            continue 
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['synAuth']['dstPorts'].append(row['port'])

    # TCP Reset
    cursor.execute('select * from cm_idle_reset')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['idleReset'] = {
            'enabled': intToBool(row['enabled']),
            'idleTimeout': row['idle_timeout'],
            'initTimeout': row['init_timeout'],
            'initSize': row['init_size'],
            'numIdles': row['num_idles'],
            'headerTime': row['header_time'],
            'bitRate': row['rate_interval'],
            'track_long_lived': intToBool(row['track_long_lived']),
        }
    
    # TCP Conn Limit
    cursor.execute('select * from cm_connlimit')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['connlimit'] = {
            'enabled': intToBool(row['enabled']),
            'connLimit': row['conn_limit'],
            'blacklistEnabled': intToBool(row['blacklist_enabled']),
        }


    # TLS Malformed
    cursor.execute('select * from cm_tls_malform')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['tlsMalform'] = {
            "enabled": intToBool(row['enabled']),
            "cipher_limit": row['cipher_limit'],
            "extension_limit": row['extension_limit'],
            "compression_limit": row['compression_limit'],
            "max_hello_length": row['max_hello_length'],
            "max_early_close": row['max_early_close'],
            "max_pend_secs": row['max_pend_secs'],
            "min_pend_secs": row['min_pend_secs'],
            "clients_can_alert": intToBool(row['clients_can_alert']),
            "early_whitelist": intToBool(row['early_whitelist']),
        }
       
    ##### HTTP
    cursor.execute('select * from cm_http_malform')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['httpMalform'] = {'enabled': intToBool(row['enabled'])}
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['botnet'] = {
            "basic": intToBool(row['basic']),
            "segment": intToBool(row['segment']),
            "signatures": intToBool(row['signatures'])
        }
    


    sts = boolGenericDetails(cursor, sts, 'cm_http_proxy_detect', 'httpProxyDetect')
    
    cursor.execute('select * from cm_http_object')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['httpRatelimit'] = {'objectRate': row['rate']}
    
    cursor.execute('select * from cm_http_request')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if 'httpRatelimit' not in sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['httpRatelimit'] = {}
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['httpRatelimit']['requestRate'] = row['rate']
        
    sts = regexDetails(cursor, sts, 'cm_http_regex', 'httpRegex')

    # APP Behavior
    cursor.execute('select * from cm_appbehavior')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if row['enabled'] == 0:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['appbehavior'] = {'interruptCnt': 0} 
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['appbehavior'] = {'interruptCnt': row['interrupt_cnt']}
        


    # GENERIC
    sts = boolGenericDetails(cursor, sts, 'cm_webcrawler_whitelist', 'webcrawler')
    sts = boolGenericDetails(cursor, sts, 'cm_private_address', 'privateAddress')
    sts = boolGenericDetails(cursor, sts, 'cm_multicast', 'multicast')


    # Shaping
    cursor.execute('select * from cm_shaping')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['shaping'] = {
            "bps": row['bps'],
            "enabled": intToBool(row['enabled']),
            "pps": row['pps'],
            "filter": [f"{row['filter']}"]
        }

    # Payload Regex

    cursor.execute('select * from cm_regex')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['regex'] = { 
            "denylistEnable": intToBool(row['blacklist_enable']),
            "enabled": intToBool(row['enabled']),
            "includeHeaders": intToBool(row['include_headers']),
            "matchSrcPort": intToBool(row['match_src_port']),
            "pattern": [row['pattern']],
            "tcpPorts": [],
            "udpPorts": [],
        }

    cursor.execute('select * from cm_regex_ports')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if 'regex' not in sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]:
            continue
        if row['is_tcp'] == 1:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['regex']['tcpPorts'].append(row['port'])
        else:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['regex']['udpPorts'].append(row['port'])
        # if row['statement'] is None:
        #     continue
        # for entry in row['statement'].splitlines():
        #      sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]][api_name]['statement'].append(entry)
    

    cursor.execute('select * from cm_geoip')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if row['enabled'] == 0:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['ipLocationPolicing'] = {'enabled': intToBool(row['enabled'])}
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['ipLocationPolicing'] = {
            "enabled": intToBool(row['enabled']),
            "otherAction": row['other_action'],
            "countries": []
        }
        if row['other_pps'] is not None:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['ipLocationPolicing']["otherPps"] = row['other_pps']
        if row['other_bps'] is not None:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['ipLocationPolicing']["otherBps"] = row['other_bps']

    cursor.execute('select * from cm_geoip_countries')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if 'ipLocationPolicing' not in sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]:
            continue
        data = { "country": row['country']}
        if row['action'] == 'allow_all':
            data['allow'] = True
        elif row['action'] == 'drop_all':
            data['allow'] = False
        elif row['action'] == 'rate_limit':
            if row['bps'] is not None:
                data['bps'] = row['bps']
            if row['pps'] is not None:
                data['pps'] = row['pps']
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['ipLocationPolicing']['countries'].append(data)


    # Reputation
    cursor.execute('select * from cm_reputation')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['reputation'] = {
            "customConfidence": row['confidence'],
            "deepScrubbing": intToBool(row['deep_scrubbing']),
            "enabled": intToBool(row['enabled']),
            "useCustom": intToBool(row['use_custom']),
            "categories": {},
            "asertConfidence": config.REPUTATION_DEFAULT[row['security_level']] 
        }

    cursor.execute('select * from cm_reputation_categories')
    results = get_results(cursor)
    for row in results:
        if row['server_type'] not in sts:
            continue
        if 'reputation' not in sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]:
            continue
        sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['reputation']['categories'][config.REPUTATION_CAT[row['category_id']]] = {
            "enabled": intToBool(row['enabled']),
            "confidence": row['confidence'],
        }
        if row['confidence'] is not None:
            sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['reputation']['categories'][config.REPUTATION_CAT[row['category_id']]]['confidence'] = row['confidence']
        else:
            if sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['reputation']['useCustom']:
                sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['reputation']['categories'][config.REPUTATION_CAT[row['category_id']]]['confidence'] = \
                    sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['reputation']['customConfidence']
            else:
                sts[row['server_type']]['protectionLevels'][config.PROTECTION_LEVEL[row['security_level']]]['reputation']['categories'][config.REPUTATION_CAT[row['category_id']]]['confidence'] = \
                    config.REPUTATION_DEFAULT[row['security_level']]

        
    return sts