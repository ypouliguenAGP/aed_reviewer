import os
import re
import sqlite3
import json
from .config import PROTO, MAX_DUMPS_STATS_ELEMENTS


def _parse_line(line):
    """Parse a single 'Blocked host ...' line into a dict."""
    entry = {}

    # IP address
    m = re.search(r'Blocked host ([\d.]+)', line)
    entry['host_ip'] = m.group(1) if m else None

    # First / last block epoch
    m = re.search(r'first time blocked:\s+\S+ \(EPOCH:\s*(\d+)\)', line)
    entry['first_block_time'] = int(m.group(1)) if m else None

    m = re.search(r'last time blocked:\s+\S+ \(EPOCH:\s*(\d+)\)', line)
    entry['last_block_time'] = int(m.group(1)) if m else None

    # Attack categories  – stored as JSON list
    m = re.search(r"attack categories:\s*(\[.*?\])", line)
    if m:
        try:
            entry['attack_categories'] = json.dumps(json.loads(m.group(1).replace("'", '"')))
        except Exception:
            entry['attack_categories'] = m.group(1)
    else:
        entry['attack_categories'] = None

    # Protocol – use the lowest/only value
    m_low    = re.search(r'lowest protocol seen:\s*(\S+)', line)
    m_single = re.search(r',\s*protocol:\s*(\S+)', line)
    if m_low:
        entry['protocol'] = m_low.group(1).rstrip(',')
    elif m_single:
        entry['protocol'] = m_single.group(1).rstrip(',')
    else:
        entry['protocol'] = None

    # Destination ports
    m = re.search(r'lowest destination port seen:\s*(\d+)', line)
    entry['lowest_dst_port'] = int(m.group(1)) if m else None

    m = re.search(r'highest destination port seen:\s*(\d+)', line)
    entry['highest_dst_port'] = int(m.group(1)) if m else None

    # Single destination port (when no range)
    if entry['lowest_dst_port'] is None and entry['highest_dst_port'] is None:
        m = re.search(r'destination port:\s*(\d+)', line)
        if m:
            entry['lowest_dst_port'] = int(m.group(1))
            entry['highest_dst_port'] = int(m.group(1))

    # Destination IP addresses
    m = re.search(r'lowest destination IP address seen:\s*([\d.]+)', line)
    entry['lowest_dst_ip'] = m.group(1) if m else None

    m = re.search(r'highest destination IP address seen:\s*([\d.]+)', line)
    entry['highest_dst_ip'] = m.group(1) if m else None

    # Single destination IP (when no range)
    if entry['lowest_dst_ip'] is None and entry['highest_dst_ip'] is None:
        m = re.search(r'destination IP address:\s*([\d.]+)', line)
        if m:
            entry['lowest_dst_ip'] = m.group(1)
            entry['highest_dst_ip'] = m.group(1)

    # PG IDs – stored as JSON list
    m = re.search(r'PG IDs:\s*(\[[\d,\s]+\])', line)
    if m:
        try:
            entry['pg_ids'] = json.dumps(json.loads(m.group(1)))
        except Exception:
            entry['pg_ids'] = m.group(1)
    else:
        entry['pg_ids'] = None

    return entry


def _create_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS blocked_hosts (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            host_ip           TEXT,
            first_block_time  INTEGER,
            last_block_time   INTEGER,
            attack_categories TEXT,
            protocol          TEXT,
            lowest_dst_port   INTEGER,
            highest_dst_port  INTEGER,
            lowest_dst_ip     TEXT,
            highest_dst_ip    TEXT,
            pg_ids            TEXT
        )
    """)
    conn.execute("DELETE FROM blocked_hosts")
    conn.commit()
    return conn


def extrackBlockedHosts(FOLDER_NAME):
    log_path = f"{FOLDER_NAME}/inputs/tuba/blocked_hosts.log"
    if not os.path.exists(log_path):
        print(f"File {log_path} does not exist")
        raise FileNotFoundError(f"File {log_path} does not exist")

    db_path = f"{FOLDER_NAME}/blocked_hosts.db"
    conn = _create_db(db_path)

    rows = []
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('Blocked host'):
                continue
            try:
                entry = _parse_line(line)
                rows.append((
                    entry['host_ip'],
                    entry['first_block_time'],
                    entry['last_block_time'],
                    entry['attack_categories'],
                    entry['protocol'],
                    entry['lowest_dst_port'],
                    entry['highest_dst_port'],
                    entry['lowest_dst_ip'],
                    entry['highest_dst_ip'],
                    entry['pg_ids'],
                ))
            except Exception as e:
                print(f"Error parsing line: {line}\n{e}")
                continue

    conn.executemany("""
        INSERT INTO blocked_hosts
            (host_ip, first_block_time, last_block_time, attack_categories,
             protocol, lowest_dst_port, highest_dst_port,
             lowest_dst_ip, highest_dst_ip, pg_ids)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()

    print(f"Inserted {len(rows)} entries into {db_path}")
    return db_path
