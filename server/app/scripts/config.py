

RESSOURCES_PATH = 'ressources/'
LEGACY = 'legacy/'
FOLDER_NAME = ''


EXPORT_PATH = 'exports/'
EXPORT_INDENT=2

MAX_DUMPS_STATS_ELEMENTS = 12

PROTECTION_LEVEL = {
    1: 'low',
    2: 'medium',
    3: 'high'
}

BANDWIDTH_ALERT_MODES = {
    0: 'disabled',
    1: 'alert_static',
    2: 'alert_global',
    3: 'auto_level_static',
    4: 'auto_level_global',
}

NOTIFICATION = {
    'type': {
        1: 'system',
        2: 'cloud',
        3: 'protection',
        4: 'deployment',
        5: 'blocked_host',
        6: 'bandwidth',
        7: 'change_log',
    },
    'facility': {
        24: 'daemon',
        128: 'local0',
        136: 'local1',
        144: 'local2',
        152: 'local3',
        160: 'local4',
        168: 'local5',
        176: 'local6',
        184: 'local7',
        8: 'user',
    },
    'severity': {
        1: 'alert',
        2: 'crit',
        7: 'debug',
        0: 'emerg',
        3: 'err',
        6: 'info',
        5: 'notice',
        4: 'warning',
    }
}

REPUTATION_CAT = {
    1: 'Email Threats',
    2: 'Location Based Threats',
    3: 'Campaigns and Targeted Attacks',
    4: 'Command and Control',
    5: 'DDoS Reputation',
    6: 'Malware',
    7: 'Mobile',
}

REPUTATION_DEFAULT = {
    1: 80, # Low
    2: 60, # Medium
    3: 20 # High
}

PARENT_TYPE = {
    0: "Generic Server",
    1: "Web Server",
    2: "DNS Server",
    3: "Mail Server",
    4: "VOIP Server",
    5: "VPN Server",
    6: "RLogin Server",
    7: "File Server",
}

PROTO = {
    6: 'TCP',
    17: 'UDP'
}

NETMASKS = {
    '0.0.0.0': 0,
    '255.0.0.0': 8,
    '255.128.0.0': 9,
    '255.192.0.0': 1,
    '255.224.0.0': 11,
    '255.240.0.0': 12,
    '255.248.0.0': 13,
    '255.252.0.0': 14,
    '255.254.0.0': 15,
    '255.255.0.0': 16,
    '255.255.128.0': 17,
    '255.255.192.0': 18,
    '255.255.224.0': 19,
    '255.255.240.0': 2,
    '255.255.248.0': 21,
    '255.255.252.0': 22,
    '255.255.254.0': 23,
    '255.255.255.0': 24,
    '255.255.255.128': 25,
    '255.255.255.192': 26,
    '255.255.255.224': 27,
    '255.255.255.240': 28,
    '255.255.255.248': 29,
    '255.255.255.252': 30,
    '255.255.255.254': 31,
    '255.255.255.255': 32,
}