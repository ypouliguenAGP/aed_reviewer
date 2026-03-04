import sqlite3
from flask import Flask, send_file, Response, make_response, Blueprint, request, jsonify, abort, g
from datetime import datetime
from app import app
import json
import os
import gzip
import re
import shutil
import tarfile
from ..scripts.main import processAEDConfig
import string
import random
from cryptography.fernet import Fernet
from functools import wraps
import base64
import subprocess
import ipaddress
import hashlib
import time


def apply_filter(packet, filter_str):
    """
    Apply a pcap-like filter to a packet.
    Supported syntax:
    - 'dst port 80' / 'src port 443'
    - 'dst port 1024..65535' (range)
    - 'dst net 192.168.1.0/24' / 'src net 10.0.0.0/8'
    - 'proto tcp' / 'proto udp' / 'proto 6'
    - 'src ip 192.168.1.1' / 'dst ip 10.0.0.1'
    - 'action drop' / 'action pass'
    - 'country FR' / 'country US'
    - 'flags S' / 'flags SA' / 'flags A'
    - Logical operators: 'and', 'or'
    - Negation: 'not dst port 80'
    
    Packet structure example:
    {
        "#": 2,
        "len": "242",
        "src_ip": "15.1.1.1",
        "src_port": "4500",
        "dst_ip": "192.168.1.1",
        "dst_port": "4500",
        "proto": "17",
        "src_country": "FR",
        "action": "pass",
        "tcp_flags": "S" (optional, for TCP)
    },
    {
        "#": 3,
        "len": "394",
        "src_ip": "213.0.185.5",
        "dst_ip": "194.50.38.6",
        "proto": "50",
        "src_country": "ES",
        "action": "pass"
    },
    {
        "#": 4,
        "len": "154",
        "src_ip": "213.0.185.5",
        "dst_ip": "194.50.38.6",
        "proto": "50",
        "src_country": "ES",
        "action": "pass"
    },
    {
        "#": 5,
        "len": "242",
        "src_ip": "15.188.46.43",
        "src_port": "4500",
        "dst_ip": "194.50.38.6",
        "dst_port": "4500",
        "proto": "17",
        "src_country": "FR",
        "action": "pass"
    },
    {
        "#": 6,
        "len": "654",
        "src_ip": "63.33.240.206",
        "src_port": "443",
        "dst_ip": "194.50.38.6",
        "dst_port": "31098",
        "proto": "6",
        "tcp_flags": "AP",
        "src_country": "IE",
        "action": "pass"
    }
    """
    if not filter_str or filter_str.strip() == '':
        return True

    filter_str = filter_str.strip().lower()

    # Split by 'or' first (lower precedence)
    if ' or ' in filter_str:
        parts = filter_str.split(' or ')
        return any(apply_filter(packet, part.strip()) for part in parts)

    # Split by 'and' (higher precedence)
    if ' and ' in filter_str:
        parts = filter_str.split(' and ')
        return all(apply_filter(packet, part.strip()) for part in parts)

    # Handle negation
    if filter_str.startswith('not '):
        return not apply_filter(packet, filter_str[4:].strip())

    tokens = filter_str.split()
    if not tokens:
        return True

    def to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # proto <protocol>
    if tokens[0] == 'proto' and len(tokens) >= 2:
        proto_map = {'tcp': '6', 'udp': '17', 'icmp': '1', 'gre': '47', 'esp': '50'}
        target_proto = tokens[1]
        if target_proto in proto_map:
            target_proto = proto_map[target_proto]
        return str(packet.get('proto', '')).lower() == target_proto

    # action <action>
    if tokens[0] == 'action' and len(tokens) >= 2:
        return str(packet.get('action', '')).lower() == tokens[1]

    # country <country_code>
    if tokens[0] == 'country' and len(tokens) >= 2:
        return str(packet.get('src_country', '')).lower() == tokens[1].lower()

    # flags <tcp_flags> (partial match)
    if tokens[0] == 'flags' and len(tokens) >= 2:
        tcp_flags = str(packet.get('tcp_flags', '')).lower()
        return tokens[1].lower() in tcp_flags

    # src/dst port <port> or <port_range>
    if len(tokens) >= 3 and tokens[0] in ('src', 'dst') and tokens[1] == 'port':
        direction = tokens[0]
        port_field = 'src_port' if direction == 'src' else 'dst_port'
        port_value = to_int(packet.get(port_field))
        if port_value is None:
            return False
        port_filter = tokens[2]

        if '..' in port_filter:
            try:
                low, high = port_filter.split('..')
                return int(low) <= port_value <= int(high)
            except ValueError:
                return False
        try:
            return port_value == int(port_filter)
        except ValueError:
            return False

    # src/dst net <cidr>
    if len(tokens) >= 3 and tokens[0] in ('src', 'dst') and tokens[1] == 'net':
        direction = tokens[0]
        ip_field = 'src_ip' if direction == 'src' else 'dst_ip'
        ip_value = packet.get(ip_field)
        if not ip_value:
            return False
        try:
            network = ipaddress.ip_network(tokens[2], strict=False)
            ip_addr = ipaddress.ip_address(ip_value)
            return ip_addr in network
        except ValueError:
            return False

    # src/dst ip <ip> (exact match)
    if len(tokens) >= 3 and tokens[0] in ('src', 'dst') and tokens[1] == 'ip':
        direction = tokens[0]
        ip_field = 'src_ip' if direction == 'src' else 'dst_ip'
        return str(packet.get(ip_field, '')).lower() == tokens[2]

    # len <operator><value> (e.g., len >100, len <=1500, len 64..1500)
    if tokens[0] == 'len' and len(tokens) >= 2:
        len_value = to_int(packet.get('len'))
        if len_value is None:
            return False
        len_filter = tokens[1]

        if '..' in len_filter:
            try:
                low, high = len_filter.split('..')
                return int(low) <= len_value <= int(high)
            except ValueError:
                return False
        if len_filter.startswith('>='):
            return len_value >= int(len_filter[2:])
        if len_filter.startswith('<='):
            return len_value <= int(len_filter[2:])
        if len_filter.startswith('>'):
            return len_value > int(len_filter[1:])
        if len_filter.startswith('<'):
            return len_value < int(len_filter[1:])
        try:
            return len_value == int(len_filter)
        except ValueError:
            return False

    return True


bp = Blueprint('aed_reviewer', __name__, static_folder='static/aed_reviewer', static_url_path='/static/aed_reviewer/')

def key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'aed_id' in request.view_args:
            return {'success': False}
        # If exports does not exist
        if not os.path.exists(f"{app.config['EXPORT_PATH']}{request.view_args['aed_id']}"):
            return {'success': False, 'error': '498r'}
        # If cookie key is not provided
        if not request.view_args['aed_id'] in request.cookies:
            return {'success': False, 'error': '545b'}
        # Retrieve key
        # with open(f"{app.config['EXPORT_PATH']}{request.view_args['aed_id']}/fernet.key",'rb') as key_file:
        #     key = key_file.read()
        key = request.cookies.get(request.view_args['aed_id'])
        # check if key is correctly encoded
        try:
            base64.urlsafe_b64decode(key)
        except:
            return {'success': False, 'error': '445c'}
        g.fernet = Fernet(key)
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def catch_all(path):
    print('running catchall')
    return send_file('static/aed_reviewer/index.html')

@bp.route('/assets/<path:path>')
def assets_get(path):
    return send_file(f'static/aed_reviewer/assets/{path}')

@bp.after_request
def after_request_func(response):
    print(request.endpoint)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@bp.post('/api/aed/validation')
def aed_validation():
    # POST should include JSON payload with 'aed_id' and 'aed_password'
    data = request.get_json()
    if not data or 'aed_id' not in data or 'aed_password' not in data:
        return {'success': False, 'message': 'missing parameters'}


    # Checking if exist
    if not os.path.exists(f"{app.config['EXPORT_PATH']}{data['aed_id']}"):
        return {'success': False, 'message': 'project does not exist'}
    # If cookie key is provided
    key = data['aed_password']
    # check if key is correctly encoded
    try:
        base64.urlsafe_b64decode(key)
    except:
        return {'success': False, 'error': 'AED Key format error'}
    
    try:
        g.fernet = Fernet(key)
        with open(f"{app.config['EXPORT_PATH']}{data['aed_id']}/global.json") as f:
            decrypted = g.fernet.decrypt(f.read())
        global_config = json.loads(decrypted)
    except:
        return {'success': False, 'error': 'Key Error'}

    resp = make_response(jsonify({'success':True, 'name':global_config['system_name']}) )
    resp.set_cookie(data['aed_id'], key, path=f"/aed_reviewer/api/{data['aed_id']}/", max_age=3600*24*30)
    return resp

@bp.get('/api/aed/add_project')
def aed_add_project():
    alphabet = string.ascii_lowercase + string.digits
    project_id = 'aed-'+''.join(random.choices(alphabet, k=8))
    
    os.mkdir(os.path.join(app.config['EXPORT_PATH'], project_id))
    os.mkdir(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs'))
    print(project_id)
    return {'success': True, 'project_id': project_id}

@bp.post('/api/aed/upload')
def aed_upload():  
    # Get the list of files from webpage 
    files = request.files.getlist("file")
    print(request)
    print(request.form)
    project_id = request.form.get('project_id')
    # Iterate for each file in the files List, and Save them

    for file in files: 
        if re.search("^DiagFile-.*\.tbz2$", file.filename):
            file.save(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', "DiagFile.tbz2"))
        elif re.search(".*\.tar\.bz2$", file.filename):
            file.save(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', "AEDToolKit.tar.bz2"))
        else:
            continue
    return {'success': True, 'message': f'{len(files)} files uploaded successfully', 'aed_id':project_id}

@bp.get('/api/<string:aed_id>/uncompress')
def aed_uncompress(aed_id):
    saved_file = {
        'DiagFile': "DiagFile.tbz2",
        'AEDToolKit': "AEDToolKit.tar.bz2",
    }
    try:
        print('Extracting AEDToolKit')
        with tarfile.open(os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', saved_file['AEDToolKit']), 'r:bz2') as tar:
            for member in tar.getmembers():
                if re.search(".+\.stats\/.*\.[json|log]", member.name):
                    member_name = member.name
                    member.name = os.path.basename(member.name)
                    print(f"Extracting {member.name} to {os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', "stats", member_name.split('/')[-2])}")
                    tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', "stats", member_name.split('/')[-2]))
        tar.close()
    except:
        pass

    file_list = ['config_show_saved','ifconfig.txt','licenses.txt','hardware.txt','ntp.txt','pkgs.txt','backup.log',
                 'syslog','syslog.0.gz','syslog.1.gz','syslog.2.gz','syslog.3.gz','syslog.4.gz',
                 'tuba/tuba.db','tuba/cfg.db','tuba/events.db','tuba/feed.db','tuba/log.db','smartctl_sdc.txt']
    base = None
    print('Extracting DiagFile')
    with tarfile.open(os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', saved_file['DiagFile']), 'r:bz2') as tar:
        base = tar.getmembers()[0].name.split('/')[0]
        
        for file_name in file_list:
            try:
                member = tar.getmember(f"{base}/{file_name}")
                member.name = file_name
                print(f"Extracting {member.name} to {os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs')}")
                tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs'))
            except KeyError:
                print(f"Warning: File '{base}/{file_name}' not found in the tar archive.")
        for member in tar.getmembers():
            # Extract statusdump files
            if re.search(".+statusdump_history\/statusdump\.[0-9]+\.txt\.bz2", member.name):
                member_name = member.name
                member.name = os.path.basename(member.name)
                print(f"Extracting {member.name} to {os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', 'tuba', 'statusdump_history')}")
                tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', 'tuba', 'statusdump_history'))
    return {'success': True, 'message': f'files uncompresses successfully', 'aed_id':aed_id}
    

@bp.get('/api/<string:aed_id>/parse')
def aed_parse(aed_id):
    fernet_key = processAEDConfig(os.path.abspath(os.path.join(app.config['EXPORT_PATH'], aed_id)))
    # try:
    # folders_to_copy = ['attacks','traffic','locations','protocols','services']
    # for folder in folders_to_copy:
    #     print(folder)
    #     print(f"Creating {os.path.join(app.config['EXPORT_PATH'], aed_id, "stats", folder)}")
    #     os.makedirs(os.path.join(app.config['EXPORT_PATH'], aed_id, "stats", folder), exist_ok=True)
    #     obj = os.scandir(os.path.abspath(os.path.join(app.config['EXPORT_PATH'], aed_id, "inputs", "stats", folder)))
    #     for entry in obj:
    #         if not entry.is_file():
    #             continue
    #         if not entry.name.endswith('.json'):
    #             continue
    #         # print(entry.path)
    #         shutil.copyfile(entry.path, os.path.join(app.config['EXPORT_PATH'], aed_id, "stats", folder, entry.name))
    #         print(f"Coying to {os.path.join(app.config['EXPORT_PATH'], aed_id, "stats", folder, entry.name)}")
        # print(f'Copying folder {folder}')
        
        # shutil.copytree(os.path.abspath(os.path.join(app.config['EXPORT_PATH'], aed_id, "inputs", "stats", folder)), os.path.join(app.config['EXPORT_PATH'], aed_id, "stats", folder), dirs_exist_ok=True)
    # shutil.rmtree(os.path.join(app.config['EXPORT_PATH'], aed_id, "inputs"), ignore_errors=True)
    # except:
    #     pass
    resp = make_response(jsonify({'success': True, 'aed_id':aed_id, 'key': fernet_key.decode("utf-8")}))
    resp.set_cookie(aed_id, fernet_key.decode("utf-8"), path=f"/aed_reviewer/api/{aed_id}/", max_age=3600*24*30)
    # shutil.rmtree(os.path.join(app.config[''], aed_id, "inputs"), ignore_errors=True)
    return resp

@bp.get('/api/<string:aed_id>/statusdump_parse')
def statusdump_parse(aed_id):
    print(f"Parsing statusdump for AED ID: {aed_id}")

    input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', app.config['EXPORT_PATH'], aed_id, 'inputs'))
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', app.config['EXPORT_PATH'], aed_id))
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'statusdump_parse'))
    print("Running statusdump_parse")
    print([f"{script_path} -i {input_path} -o {output_path}"])

    try:
        result = subprocess.run(
            [script_path, '-i', input_path, '-o', output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("statusdump_parse output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("statusdump_parse failed:", e.stderr)
        return {'success': False, 'error': 'statusdump_parse failed', 'details': e.stderr}


    resp = make_response(jsonify({'success': True, 'aed_id':aed_id, 'message': 'statusdump_parse completed successfully'}))
    return resp



@bp.post('/api/aed/add')
def aed_add():  
    print(request)
    # Get the list of files from webpage 
    print(request.files)
    files = request.files.getlist("file")
    print(request)
    # Iterate for each file in the files List, and Save them
    saved_file = {
        'DiagFile': None,
        'AEDToolKit': None,
    }
    alphabet = string.ascii_lowercase + string.digits
    project_id = 'aed-'+''.join(random.choices(alphabet, k=8))
    
    print(project_id)
    os.mkdir(os.path.join(app.config['EXPORT_PATH'], project_id))
    os.mkdir(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs'))
    for file in files: 
        if re.search("^DiagFile-.*\.tbz2$", file.filename):
            saved_file['DiagFile'] = "DiagFile.tbz2"
            file.save(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', saved_file['DiagFile']))
        elif re.search(".*\.tar\.bz2$", file.filename):
            saved_file['AEDToolKit'] = "AEDToolKit.tar.bz2"
            file.save(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', saved_file['AEDToolKit']))
        else:
            continue
    for (key, value) in saved_file.items():
        if value is None:
            shutil.rmtree(os.path.join(app.config['EXPORT_PATH'], project_id), ignore_errors=True)
            return {'success': False, 'message': f'{key} Missing'}
        
    # Processing Files
    print('Extracting AEDToolKit')
    with tarfile.open(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', saved_file['AEDToolKit']), 'r:bz2') as tar:
        for member in tar.getmembers():
            if re.search(".+\.stats\/.*\.[json|log]", member.name):
                member_name = member.name
                member.name = os.path.basename(member.name)
                tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', "stats", member_name.split('/')[-2]))
    tar.close()

    file_list = ['config_show_saved','ifconfig.txt','licenses.txt','hardware.txt','ntp.txt','pkgs.txt','backup.log',
                 'syslog','syslog.0.gz','syslog.1.gz','syslog.2.gz','syslog.3.gz','syslog.4.gz',
                 'tuba/tuba.db','tuba/cfg.db','tuba/events.db','tuba/feed.db','tuba/log.db','smartctl_sdc.txt', 'tuba/statusdump_history/']
    base = None
    print('Extracting DiagFile')
    with tarfile.open(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', saved_file['DiagFile']), 'r:bz2') as tar:
        for member in tar.getmembers():
            base = member.name.split('/')[0]
            print(member.name)
            print(os.path.basename(member.name))
        for file_name in file_list:
            try:
                member = tar.getmember(f"{base}/{file_name}")
                member.name = file_name
                tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs'))
            except KeyError:
                print(f"Warning: File '{base}/{file_name}' not found in the tar archive.")
    
    print('Processing Input Files')
    processAEDConfig(os.path.abspath(os.path.join(app.config['EXPORT_PATH'], project_id)))
    # Copy Stats Folders
    folders_to_copy = ['attacks','traffic','locations','protocols','services']
    for folder in folders_to_copy:
        print(f'Copying folder {folder}')
        shutil.copytree(os.path.abspath(os.path.join(app.config['EXPORT_PATH'], project_id, "inputs", "stats", folder)), os.path.join(app.config['EXPORT_PATH'], project_id, "stats", folder))

    # shutil.rmtree(os.path.join(app.config['EXPORT_PATH'], project_id), ignore_errors=True)
    return {'success': True, 'message': f'{len(files)} files uploaded successfully', 'aed_id':project_id}
    
@bp.get('/api/<string:aed_id>/system_name')
@key_required
def system_name_get(aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}{aed_id}/global.json"):
        return {'success': False, 'error': '498r'}
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/global.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    global_config = json.loads(decrypted)
    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/global.json") as f:
    #     global_config = json.load(f)
    if 'system_name' not in global_config:
        return {'success': False}
    return jsonify({'success':True, 'name':global_config['system_name']})

@bp.get('/api/<string:aed_id>/protection_groups')
@key_required
def pgs_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/pgs.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

def pgs_list(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/pgs.json") as f:
        decrypted = g.fernet.decrypt(f.read())   
    pgs_id = {} 
    pgs = json.loads(decrypted)
    for pg in pgs:
        pgs_id[pg] = pgs[pg]['name']
    return pgs_id


@bp.get('/api/<string:aed_id>/master_filter_list')
@key_required
def mfl_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/master_filter_list.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    mfl = json.loads(decrypted)
    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/master_filter_list.json") as f:
    #     mfl = json.load(f)
    if 'v4' not in mfl:
        return {'success': False}
    return mfl['v4']

@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>')
@key_required
def pg_details_get(pg_id, aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/pgs.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    pgs = json.loads(decrypted)
    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/pgs.json") as f:
    #     pgs = json.load(f)
    if pg_id not in pgs:
        return {'success': False, 'message': f'PG {pg_id} not found'}
    data = pgs[pg_id]
    print(f"Associated Server Type is {pgs[pg_id]['server_type']}")
    # Find Server Type
    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/sts.json") as f:
    #     sts = json.load(f)
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/sts.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    sts = json.loads(decrypted)
    if f"{pgs[pg_id]['server_type']}" not in sts:
        return {'success': False, 'message': f'ST associated with {pg_id} not found'}
    data['protections'] = sts[f"{pgs[pg_id]['server_type']}"]
    if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats"):
        data['stats'] = True
    return {'success': True, 'data':data}

@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/traffic_locations/<string:period>')
@key_required
def prepare_traffic_location(pg_id, aed_id, period='1d'):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats"):
        return {'success': False} 
    # Locations
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json"):
        print(f"File {app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json does not exist")
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json") as f:
        decrypted = g.fernet.decrypt(f.read())
        locations = prepare_location_data(json.loads(decrypted)['ip-locations'])
        # locations = prepare_location_data(json.load(f)['ip-locations'])
    return locations
        


@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/traffic/<string:period>')
@key_required
def prepare_traffic(pg_id, aed_id, period='1d'):
    stats = {}
    if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats"):
        # Traffic
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/traffic/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/traffic/{pg_id}_{period}.json") as f:
                # stats['traffic'] = prepare_traffic_data(json.load(f)['timeseries-data'][0])
                decrypted = g.fernet.decrypt(f.read())
                stats['traffic'] = prepare_traffic_data(json.loads(decrypted)['timeseries-data'][0])
        # Services
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/attacks/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/attacks/{pg_id}_{period}.json") as f:
                # stats['attacks'] = prepare_attack_data(json.load(f)['attack-categories']['timeseries'])
                decrypted = g.fernet.decrypt(f.read())
                stats['attacks'] = prepare_attack_data(json.loads(decrypted)['attack-categories']['timeseries'])
        # Locations
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json") as f:
                # stats['locations'] = prepare_location_data(json.load(f)['ip-locations'])
                decrypted = g.fernet.decrypt(f.read())
                stats['locations'] = prepare_location_data(json.loads(decrypted)['ip-locations'])
                
        # Services
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/services/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/services/{pg_id}_{period}.json") as f:
                # stats['services'] = prepare_services_data(json.load(f)['services'])
                decrypted = g.fernet.decrypt(f.read())
                stats['services'] = prepare_services_data(json.loads(decrypted)['services'])
        # Protocols
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/protocols/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/protocols/{pg_id}_{period}.json") as f:
                # stats['protocols'] = prepare_protocol_data(json.load(f)['protocols'])
                decrypted = g.fernet.decrypt(f.read())
                stats['protocols'] = prepare_protocol_data(json.loads(decrypted)['protocols'])
    return stats

def prepare_traffic_data(traffic):
    data = {
        'bps': {
            'Passed': [],
            'Dropped': [],
        },
        'pps': {
            'Passed': [],
            'Dropped': [],
        },
    }
    for index, item in enumerate(traffic['times']):
        data['bps']['Passed'].append([item[0]*1000,traffic['bpsPassed'][index]])
        data['bps']['Dropped'].append([item[0]*1000,traffic['bpsDropped'][index]])
        data['pps']['Passed'].append([item[0]*1000,traffic['ppsPassed'][index]])
        data['pps']['Dropped'].append([item[0]*1000,traffic['ppsDropped'][index]])
    return data

def prepare_attack_data(traffic):
    data = {}
    for attack in traffic['data']:
        data[attack['acName']] = {
            'bps': [],
            'pps': [],
        }
        for i in range(len(traffic['times'])):
            data[attack['acName']]['pps'].append([traffic['times'][i][0]*1000,attack['ppsDropped'][i]])
            data[attack['acName']]['bps'].append([traffic['times'][i][0]*1000,attack['bpsDropped'][i]])
    return data

def prepare_location_data(traffic):
    data = {}
    print(len(traffic['data']))
    for country in traffic['data']:
        data[country['country']] = {
            'bps': {
                'Total': [],
                'Passed': [],
                'Dropped': [],
            },
            'pps': {
                'Total': [],
                'Passed': [],
                'Dropped': [],
            },
        }
        for i in range(len(traffic['times'])):
            data[country['country']]['pps']['Total'].append([traffic['times'][i][0]*1000,country['pps'][i]])
            data[country['country']]['bps']['Total'].append([traffic['times'][i][0]*1000,country['bps'][i]])
            data[country['country']]['bps']['Dropped'].append([traffic['times'][i][0]*1000,country['bpsDropped'][i]])
            data[country['country']]['bps']['Passed'].append([traffic['times'][i][0]*1000,country['bpsPassed'][i]])
            data[country['country']]['pps']['Dropped'].append([traffic['times'][i][0]*1000,country['ppsDropped'][i]])
            data[country['country']]['pps']['Passed'].append([traffic['times'][i][0]*1000,country['ppsPassed'][i]])
    return data

def prepare_protocol_data(traffic):
    data = {}
    for protocol in traffic['totals']:
        if protocol['protoName'] is None:
            proto_name = 'NULL'
        else:
            proto_name = protocol['protoName']
        data[proto_name] = {
            'bps': [],
            'pps': [],
        }
        for i in range(len(traffic['times'])):
            data[proto_name]['pps'].append([traffic['times'][i][0]*1000,protocol['pps'][i]])
            data[proto_name]['bps'].append([traffic['times'][i][0]*1000,protocol['bps'][i]])
    return data

def prepare_services_data(traffic):
    data = {}

    for service_position, service in enumerate(traffic['totals']):
        if service['protoName'] is None:
            continue
        if service['portHi'] is None:
            service_name = service['protoName']
        elif service['portHi'] == service['portLo']:
            service_name = f"{service['protoName']}/{service['portLo']}"
        else:
            service_name = f"{service['protoName']}/{service['portLo']}-{service['portHi']}"

        data[service_name] = {
            'bps': [],
            'pps': [],
        }
        for i in range(len(traffic['times'])):
            data[service_name]['pps'].append([traffic['times'][i][0]*1000,traffic['pps'][service_position][i]])
            data[service_name]['bps'].append([traffic['times'][i][0]*1000,traffic['bps'][service_position][i]])
    return data

@bp.get('/api/<string:aed_id>/server_types')
@key_required
def sts_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/sts.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))
    

@bp.get('/api/<string:aed_id>/global_alerting')
@key_required
def global_alerting_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/global_alerting.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))


@bp.get('/api/<string:aed_id>/interfaces')
@key_required
def interfaces_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/interfaces.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/interfaces_mgt')
@key_required
def interfaces_mgt_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/interfaces_mgt.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/ip_routes')
@key_required
def ip_routes_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/ip_routes.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))



@bp.get('/api/<string:aed_id>/ip_access')
@key_required
def ip_access_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/ip_access.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/hardware')
@key_required
def hardware_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/hardware.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/global')
@key_required
def global_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/global.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/http_proxy')
@key_required
def http_proxy_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/http_proxy.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/licenses')
@key_required
def licenses_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/licenses.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/crawlers')
@key_required
def crawlers_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/webcrawlers.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))


@bp.get('/api/<string:aed_id>/notifications')
@key_required
def notifications_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/notification_dests.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))

@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/changes/')
@key_required
def pg_logs_get(pg_id, aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json"):
        return {'success': False}
    # Find associated Server Type
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/pgs.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    pgs = json.loads(decrypted)

    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/pgs.json") as f:
    #     pgs = json.load(f)
    if pg_id not in pgs:
        return {'success': False, 'message': f'PG {pg_id} not found'}
    st_id = pgs[pg_id]['server_type']
    print(f"Associated Server Type is {st_id}")

    with open(f"{app.config['EXPORT_PATH']}{aed_id}/changes.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    data = json.loads(decrypted)
    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json") as f:
    #         data = json.load(f)
    events = []
    if pg_id in data['pg']:
        events += data['pg'][pg_id]
    print(type(st_id))
    if f"{st_id}" in data['st']:
        print(f"{len(data['st'][f"{st_id}"])} Changes found for ST {st_id}")
        events += data['st'][f"{st_id}"]
    return events


@bp.get('/api/<string:aed_id>/change_types/')
def log_types_get(aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json"):
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/changes.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    data = json.loads(decrypted)
    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json") as f:
    #     data = json.load(f)
        
    event_types = []
    for type_selected in data:
        event_types.append(type_selected)
    return jsonify(event_types)
        

@bp.get('/api/<string:aed_id>/changes/')
def logs_get(aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json"):
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/changes.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    data = json.loads(decrypted)
    events = []
    for type_selected in data:
        if type(data[type_selected]) is dict:
            for event_gid in data[type_selected]:
                events = events + data[type_selected][event_gid]
        else:
            events = events + data[type_selected]
    return events
                                                                                                                          

@bp.post('/api/<string:aed_id>/changes/')
@key_required
def logs_post(aed_id):
    max_items = 300
    request_data = request.get_json()
    if 'subtype' not in request_data or 'search_str' not in request_data:
        return {'success': False, 'message': f"Missing fields"}
    subtype = request_data['subtype']
    search_str = request_data['search_str'].lower()
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json"):
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}{aed_id}/changes.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    data = json.loads(decrypted)
    events = []
    if subtype == '*':
        for type_selected in data:
            if type(data[type_selected]) is dict:
                for event_gid in data[type_selected]:
                    events = events + search_event(search_str, data[type_selected][event_gid])
            else:
                events = events + search_event(search_str, data[type_selected])
        
    else:
        if subtype not in data:
            return {'success': False, 'message': f"Subtype {subtype} does not exist"}
        
        if type(data[subtype]) is dict:
                for event_gid in data[subtype]:
                    events = events + search_event(search_str, data[subtype][event_gid])
        else:
            events = events + search_event(search_str, data[subtype])

    events.sort(key=lambda x:x['tstamp'], reverse=True)
    return events[:max_items]

def search_event(search_str, events):
    selected_events = []
    for event in events:
        if search_str in event['message'].lower() or search_str in event['username'].lower():
            selected_events.append(event)
            continue
    return selected_events
    

@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/dumps/')
@key_required
def pg_dumps_get_compressed(pg_id, aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}.json"):
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    data = json.loads(decrypted)

    # with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}.json") as f:
    #     data = json.load(f)

    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


@bp.post('/api/<string:aed_id>/dumps/')
@key_required
def dumps_get_compressed(aed_id):
    # We will look in all file in dumps folder
    # User will submit as a POST request (JSON) an fcap filter string
    # For exemple # 
    # - 'dst port 80 and src port 1024..65535'
    # - 'dst net 192.168.1.0/24 and dst port 80'
    # - 'proto tcp'
    # We will apply this filter on all dumps files and return the merged result as a compressed JSON file
    # Results are paginated with 5000 packets per page
    

    
    PAGE_SIZE = 5000
    CACHE_TTL = 3600  # Cache expires after 1 hour
    from_cache = False
    
    request_data = request.get_json()
    if 'filter' not in request_data:
        return {'success': False, 'message': f"Missing filter field"}
    filter_str = request_data['filter']
    page = request_data.get('page', 1)
    use_cache = request_data.get('use_cache', True)
    
    dumps_folder = f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/"
    if not os.path.exists(dumps_folder):
        return {'success': False, 'message': f"No dumps available"}
    
    # Get PGs List to add to each packet for info purposes
    pgs = pgs_list(aed_id)
    
    # # Generate cache key based on filter string
    cache_key = hashlib.md5(filter_str.encode()).hexdigest()
    cache_file = os.path.join(dumps_folder, f"_cache_{cache_key}.json")
    
    # Clean up old cache files (older than CACHE_TTL)
    for fname in os.listdir(dumps_folder):
        if fname.startswith('_cache_') and fname.endswith('.json'):
            fpath = os.path.join(dumps_folder, fname)
            if time.time() - os.path.getmtime(fpath) > CACHE_TTL:
                try:
                    os.remove(fpath)
                except:
                    pass
    
    # # Check if cache exists and is valid
    merged_data = None
    if use_cache and os.path.exists(cache_file):
        try:
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < CACHE_TTL:
                with open(cache_file, 'r') as f:
                    merged_data = json.load(f)
                    print(f"Cache hit for filter '{filter_str}' (age: {cache_age:.2f} seconds)")
                    from_cache = True
        except:
            pass
    
    # If no cache, perform the search and cache the results
    if merged_data is None:
        merged_data = []
        for file_name in os.listdir(dumps_folder):
            if not file_name.endswith('.json') or file_name.startswith('_cache_') or '_stats.json' in file_name:
                continue
            with open(os.path.join(dumps_folder, file_name)) as f:
                decrypted = g.fernet.decrypt(f.read())
            data = json.loads(decrypted)
            print(f"Processing dump file: {os.path.join(dumps_folder, file_name)}, Number of packets: {len(data)}")
            # Retrive ID from filename (ex: 350.json -> 350)
            file_id = os.path.splitext(file_name)[0]
            if file_id in pgs:
                pg_name = pgs[file_id]
            else:
                pg_name = "Unknown"


            for packet in data:
                if apply_filter(packet, filter_str):
                    packet['pg_id'] = file_id
                    packet['pg_name'] = pg_name
                    merged_data.append(packet)
        
        # Save to cache file
        try:
            with open(cache_file, 'w') as f:
                json.dump(merged_data, f)
        except:
            pass
    
    # Calculate pagination
    total_packets = len(merged_data)
    total_pages = (total_packets + PAGE_SIZE - 1) // PAGE_SIZE if total_packets > 0 else 1
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_data = merged_data[start_idx:end_idx]
    
    result = {
        'packets': page_data,
        'from_cache': from_cache,
        'pagination': {
            'page': page,
            'page_size': PAGE_SIZE,
            'total_packets': total_packets,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    content = gzip.compress(json.dumps(result).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response




# @bp.get('/api/protection_groups/<string:pg_id>/dumps/')
# def pg_dumps_get(pg_id):
#     if not os.path.exists(f"{app.config['SOURCE_PATH']}/stats/dumps/{pg_id}.json"):
#         return {'success': False}
#     return send_file(f"../{app.config['SOURCE_PATH']}/stats/dumps/{pg_id}.json")

@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/dump_stats/')
@key_required
def pg_dump_stats_get(pg_id, aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}_stats.json"):
        print(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}_stats.json does not exit")
        return {'success': False}
    # return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}_stats.json")
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}_stats.json") as f:
        decrypted = g.fernet.decrypt(f.read())
    return jsonify(json.loads(decrypted))


@bp.get('/api/<string:aed_id>/statusdump/interfaces')
def statusdump_intf_get(aed_id):
    # Open the sqlite3 interface_stats.db
    db_path = os.path.join(app.config['EXPORT_PATH'], aed_id, 'interface_stats.db')
    if not os.path.exists(db_path):
        return {'success': False, 'message': 'Database does not exist'}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # select distinct iface from interface_stats
    cursor.execute('SELECT DISTINCT iface FROM interface_stats')
    data = cursor.fetchall()
    conn.close()
    result = []
    for row in data:
        result.append(row[0])
    return jsonify({'success': True, 'data': result})

@bp.get('/api/<string:aed_id>/statusdump/interfaces/max')
def statusdump_intf_max_get(aed_id):
    # Open the sqlite3 interface_stats.db
    db_path = os.path.join(app.config['EXPORT_PATH'], aed_id, 'interface_stats.db')
    if not os.path.exists(db_path):
        return {'success': False, 'message': 'Database does not exist'}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # select distinct iface from interface_stats
    cursor.execute('SELECT iface, MAX(rx_offered_rate_bps) FROM interface_stats GROUP BY iface')
    cursor.execute("""
    SELECT iface, rx_offered_rate_bps, MIN(date) as date
    FROM interface_stats i
    WHERE rx_offered_rate_bps = (
        SELECT MAX(rx_offered_rate_bps) FROM interface_stats WHERE iface = i.iface
    )
    GROUP BY iface
    """)
    data = cursor.fetchall()
    conn.close()
    result = {}
    for row in data:
        result[row[0]] = {'max': row[1], 'date': row[2]}
    return jsonify({'success': True, 'data': result})
    

@bp.get('/api/<string:aed_id>/statusdump/interface/<string:iface>/<string:unit>')
def statusdump_int_get(aed_id, iface, unit='bps'):
    # Get optional start_date and last_date query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    # Steps in minutes
    step = request.args.get('step', default=300, type=int)
    if step < 60:
        return {'success': False, 'message': 'Step must be at least 60 seconds'}

    db_path = os.path.join(app.config['EXPORT_PATH'], aed_id, 'interface_stats.db')
    if not os.path.exists(db_path):
        return {'success': False, 'message': 'Database does not exist'}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build SQL query with optional date filtering
    params = [iface]
    date_filter = ''
    if start_date and end_date:
        date_filter = ' AND date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    elif start_date:
        date_filter = ' AND date >= ?'
        params.append(datetime.fromtimestamp(int(start_date)).strftime('%Y-%m-%d %H:%M:%S'))
    elif end_date:
        date_filter = ' AND date <= ?'
        params.append(datetime.fromtimestamp(int(end_date)).strftime('%Y-%m-%d %H:%M:%S'))


    # Aggregate into 5-minute buckets and compute average rx_offered_rate_bps
    query = (
        f"SELECT datetime(CAST(CAST(strftime('%s', date) / {step} AS INTEGER) * {step} AS INTEGER),'unixepoch') as bucket, "
        f"AVG(rx_offered_rate_{unit}), AVG(tx_transmitted_rate_{unit}) "
        "FROM interface_stats WHERE iface=?"
        + date_filter +
        f" GROUP BY CAST(strftime('%s', date) / {step} AS INTEGER) "
        "ORDER BY bucket"
    )
    print(query)

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    result = []
    for row in data:
        result.append([date_to_timestamp(row[0]), round(row[1]), round(row[2])])
        # result.append([row[0], row[1], row[2]])
    return jsonify({'success': True, 'data': result})


@bp.get('/api/<string:aed_id>/statusdump/pair/<int:pair>/<string:unit>')
def statusdump_pair_get(aed_id, pair, unit='bps'):
    # Get optional start_date and last_date query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    # Steps in minutes
    step = request.args.get('step', default=300, type=int)
    if step < 60:
        return {'success': False, 'message': 'Step must be at least 60 seconds'}

    db_path = os.path.join(app.config['EXPORT_PATH'], aed_id, 'interface_stats.db')
    if not os.path.exists(db_path):
        return {'success': False, 'message': 'Database does not exist'}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build SQL query with optional date filtering
    params_ext = [f'ext{pair}']
    params_int = [f'int{pair}']
    date_filter = ''
    if start_date and end_date:
        date_filter = ' AND date BETWEEN ? AND ?'
        params_ext.extend([start_date, end_date])
        params_int.extend([start_date, end_date])
    elif start_date:
        date_filter = ' AND date >= ?'
        params_ext.append(datetime.fromtimestamp(int(start_date)).strftime('%Y-%m-%d %H:%M:%S'))
        params_int.append(datetime.fromtimestamp(int(start_date)).strftime('%Y-%m-%d %H:%M:%S'))
    elif end_date:
        date_filter = ' AND date <= ?'
        params_ext.append(datetime.fromtimestamp(int(end_date)).strftime('%Y-%m-%d %H:%M:%S'))
        params_int.append(datetime.fromtimestamp(int(end_date)).strftime('%Y-%m-%d %H:%M:%S'))


    # Aggregate into 5-minute buckets and compute average rx_offered_rate_bps
    query = (
        f"SELECT datetime(CAST(CAST(strftime('%s', date) / {step} AS INTEGER) * {step} AS INTEGER),'unixepoch') as bucket, "
        f"AVG(rx_offered_rate_{unit}), AVG(tx_transmitted_rate_{unit}) "
        "FROM interface_stats WHERE iface=?"
        + date_filter +
        f" GROUP BY CAST(strftime('%s', date) / {step} AS INTEGER) "
        "ORDER BY bucket"
    )

    cursor.execute(query, params_ext)
    data_ext = cursor.fetchall()

    cursor.execute(query, params_int)
    data_int = cursor.fetchall()

    conn.close()
    result = []
    for i in range(min(len(data_ext), len(data_int))):
        
        result.append([date_to_timestamp(data_ext[i][0]), round(data_ext[i][1]), round(data_int[i][2]), round(data_ext[i][2]), round(data_int[i][1])])
        # result.append([row[0], row[1], row[2]])
    return jsonify({'success': True, 'data': result, '_comment': 'Columns are: [timestamp, ext_rx, int_tx, ext_tx, int_rx]'})

@bp.get('/api/<string:aed_id>/statusdump/traffic/combined/<string:unit>')
def statusdump_traffic_combined_get(aed_id, unit='bps'):
    # Get optional start_date and last_date query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    # Steps in minutes
    step = request.args.get('step', default=300, type=int)
    if step < 60:
        return {'success': False, 'message': 'Step must be at least 60 seconds'}

    db_path = os.path.join(app.config['EXPORT_PATH'], aed_id, 'interface_stats.db')
    if not os.path.exists(db_path):
        return {'success': False, 'message': 'Database does not exist'}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build SQL query with optional date filtering
    params = []
    date_filter = ''
    if start_date and end_date:
        date_filter = ' AND date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    elif start_date:
        date_filter = ' AND date >= ?'
        params.append(datetime.fromtimestamp(int(start_date)).strftime('%Y-%m-%d %H:%M:%S'))
    elif end_date:
        date_filter = ' AND date <= ?'
        params.append(datetime.fromtimestamp(int(end_date)).strftime('%Y-%m-%d %H:%M:%S'))


    # Query to combine the rx from all ext* interaces
    query_in = (
        f"SELECT datetime(CAST(strftime('%s', date) AS INTEGER),'unixepoch'), SUM(rx_offered_rate_{unit}) as total_rx "
        "FROM interface_stats WHERE iface LIKE 'ext%'"
        + date_filter +
        " GROUP BY date "
        "ORDER BY date"
    )

    query_out = (
        f"SELECT datetime(CAST(strftime('%s', date) AS INTEGER),'unixepoch'), SUM(rx_offered_rate_{unit}) as total_rx "
        "FROM interface_stats WHERE iface LIKE 'int%'"
        + date_filter +
        " GROUP BY date "
        "ORDER BY date"
    )

    cursor.execute(query_in, params)
    data_in = cursor.fetchall()

    cursor.execute(query_out, params)
    data_out = cursor.fetchall()


    conn.close()
    result = []
    for i in range(min(len(data_in), len(data_out))):
        result.append([date_to_timestamp(data_in[i][0]), round(data_in[i][1]), round(data_out[i][1])])
        # result.append([row[0], row[1], row[2]])
    return jsonify({'success': True, 'data': result, '_comment': 'Columns are: [timestamp, total_rx, total_tx]'})

def date_to_timestamp(date_str):
    return int(datetime.timestamp(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S'))*1000)