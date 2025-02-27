from flask import Flask, send_file, Response, make_response, Blueprint, request, jsonify, abort
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


bp = Blueprint('aed_reviewer', __name__, static_folder='static/aed_reviewer', static_url_path='/static/aed_reviewer/')


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
    with tarfile.open(os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', saved_file['AEDToolKit']), 'r:bz2') as tar:
        for member in tar.getmembers():
            if re.search(".+\.stats\/.*\.[json|log]", member.name):
                member_name = member.name
                member.name = os.path.basename(member.name)
                tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', "stats", member_name.split('/')[-2]))
    tar.close()

    file_list = ['config_show_saved','ifconfig.txt','licenses.txt','hardware.txt','ntp.txt','pkgs.txt','backup.log',
                 'syslog','syslog.0.gz','syslog.1.gz','syslog.2.gz','syslog.3.gz','syslog.4.gz',
                 'tuba/tuba.db','tuba/cfg.db','tuba/events.db','tuba/feed.db','tuba/log.db','smartctl_sdc.txt']
    base = None
    with tarfile.open(os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs', saved_file['DiagFile']), 'r:bz2') as tar:
        for member in tar.getmembers():
            base = member.name.split('/')[0]
            break
        for file_name in file_list:
            try:
                member = tar.getmember(f"{base}/{file_name}")
                member.name = file_name
                tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], aed_id, 'inputs'))
            except KeyError:
                print(f"Warning: File '{base}/{file_name}' not found in the tar archive.")
    return {'success': True, 'message': f'files uncompresses successfully', 'aed_id':aed_id}
    

@bp.get('/api/<string:aed_id>/parse')
def aed_parse(aed_id):
    processAEDConfig(os.path.abspath(os.path.join(app.config['EXPORT_PATH'], aed_id)))
    folders_to_copy = ['attacks','traffic','locations','protocols','services']
    for folder in folders_to_copy:
        print(f'Copying folder {folder}')
        shutil.copytree(os.path.abspath(os.path.join(app.config['EXPORT_PATH'], aed_id, "inputs", "stats", folder)), os.path.join(app.config['EXPORT_PATH'], aed_id, "stats", folder), dirs_exist_ok=True)
    # shutil.rmtree(os.path.join(app.config['EXPORT_PATH'], aed_id, "inputs"), ignore_errors=True)
    return {'success': True, 'aed_id':aed_id}

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
    with tarfile.open(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', saved_file['AEDToolKit']), 'r:bz2') as tar:
        for member in tar.getmembers():
            if re.search(".+\.stats\/.*\.[json|log]", member.name):
                member_name = member.name
                member.name = os.path.basename(member.name)
                tar.extract(member, path=os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', "stats", member_name.split('/')[-2]))
    tar.close()

    file_list = ['config_show_saved','ifconfig.txt','licenses.txt','hardware.txt','ntp.txt','pkgs.txt','backup.log',
                 'syslog','syslog.0.gz','syslog.1.gz','syslog.2.gz','syslog.3.gz','syslog.4.gz',
                 'tuba/tuba.db','tuba/cfg.db','tuba/events.db','tuba/feed.db','tuba/log.db','smartctl_sdc.txt']
    base = None
    with tarfile.open(os.path.join(app.config['EXPORT_PATH'], project_id, 'inputs', saved_file['DiagFile']), 'r:bz2') as tar:
        for member in tar.getmembers():
            base = member.name.split('/')[0]
            break
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
def system_name_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/global.json") as f:
        global_config = json.load(f)
    if 'system_name' not in global_config:
        return {'success': False}
    return jsonify(global_config['system_name'])

@bp.get('/api/<string:aed_id>/protection_groups')
def pgs_get(aed_id):
     return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/pgs.json")

@bp.get('/api/<string:aed_id>/master_filter_list')
def mfl_get(aed_id):
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/master_filter_list.json") as f:
        mfl = json.load(f)
    if 'v4' not in mfl:
        return {'success': False}
    return mfl['v4']

@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>')
def pg_details_get(pg_id, aed_id):
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/pgs.json") as f:
        pgs = json.load(f)
    if pg_id not in pgs:
        return {'success': False, 'message': f'PG {pg_id} not found'}
    data = pgs[pg_id]
    print(f"Associated Server Type is {pgs[pg_id]['server_type']}")
    # Find Server Type
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/sts.json") as f:
        sts = json.load(f)
    if f"{pgs[pg_id]['server_type']}" not in sts:
        return {'success': False, 'message': f'ST associated with {pg_id} not found'}
    data['protections'] = sts[f"{pgs[pg_id]['server_type']}"]
    if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats"):
        data['stats'] = True
    return {'success': True, 'data':data}

@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/traffic_locations/<string:period>')
def prepare_traffic_location(pg_id, aed_id, period='1d'):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats"):
        return {'success': False} 
    # Locations
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json"):
        print(f"File {app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json does not exist")
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json") as f:
        locations = prepare_location_data(json.load(f)['ip-locations'])
    return locations
        


@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/traffic/<string:period>')
def prepare_traffic(pg_id, aed_id, period='1d'):
    stats = {}
    if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats"):
        # Traffic
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/traffic/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/traffic/{pg_id}_{period}.json") as f:
                stats['traffic'] = prepare_traffic_data(json.load(f)['timeseries-data'][0])
        # Services
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/attacks/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/attacks/{pg_id}_{period}.json") as f:
                stats['attacks'] = prepare_attack_data(json.load(f)['attack-categories']['timeseries'])
        # Locations
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/locations/{pg_id}_{period}.json") as f:
                stats['locations'] = prepare_location_data(json.load(f)['ip-locations'])
        # Services
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/services/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/services/{pg_id}_{period}.json") as f:
                stats['services'] = prepare_services_data(json.load(f)['services'])
        # Protocols
        if os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/protocols/{pg_id}_{period}.json"):
            with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/protocols/{pg_id}_{period}.json") as f:
                stats['protocols'] = prepare_protocol_data(json.load(f)['protocols'])
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
def sts_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/sts.json")
    

@bp.get('/api/<string:aed_id>/global_alerting')
def global_alerting_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/global_alerting.json")


@bp.get('/api/<string:aed_id>/interfaces')
def interfaces_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/interfaces.json")

@bp.get('/api/<string:aed_id>/interfaces_mgt')
def interfaces_mgt_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/interfaces_mgt.json")

@bp.get('/api/<string:aed_id>/ip_routes')
def ip_routes_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/ip_routes.json")


@bp.get('/api/<string:aed_id>/ip_access')
def ip_access_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/ip_access.json")

@bp.get('/api/<string:aed_id>/hardware')
def hardware_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/hardware.json")

@bp.get('/api/<string:aed_id>/global')
def global_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/global.json")

@bp.get('/api/<string:aed_id>/http_proxy')
def http_proxy_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/http_proxy.json")

@bp.get('/api/<string:aed_id>/licenses')
def licenses_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/licenses.json")

@bp.get('/api/<string:aed_id>/crawlers')
def crawlers_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/webcrawlers.json")


@bp.get('/api/<string:aed_id>/notifications')
def notifications_get(aed_id):
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/notification_dests.json")




@bp.get('/api/<string:aed_id>/protection_groups/<string:pg_id>/changes/')
def pg_logs_get(pg_id, aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json"):
        return {'success': False}
    # Find associated Server Type
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/pgs.json") as f:
        pgs = json.load(f)
    if pg_id not in pgs:
        return {'success': False, 'message': f'PG {pg_id} not found'}
    st_id = pgs[pg_id]['server_type']
    print(f"Associated Server Type is {st_id}")

    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json") as f:
            data = json.load(f)
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
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json") as f:
        data = json.load(f)
        
    event_types = []
    for type_selected in data:
        event_types.append(type_selected)
    return jsonify(event_types)
        

@bp.get('/api/<string:aed_id>/changes/')
def logs_get(aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json"):
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json") as f:
        data = json.load(f)
    events = []
    for type_selected in data:
        if type(data[type_selected]) is dict:
            for event_gid in data[type_selected]:
                events = events + data[type_selected][event_gid]
        else:
            events = events + data[type_selected]
    return events
                                                                                                                          

@bp.post('/api/<string:aed_id>/changes/')
def logs_post(aed_id):
    max_items = 300
    request_data = request.get_json()
    if 'subtype' not in request_data or 'search_str' not in request_data:
        return {'success': False, 'message': f"Missing fields"}
    subtype = request_data['subtype']
    search_str = request_data['search_str'].lower()
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json"):
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/changes.json") as f:
            data = json.load(f)
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
def pg_dumps_get_compressed(pg_id, aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}.json"):
        return {'success': False}
    with open(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}.json") as f:
        data = json.load(f)

    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
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
def pg_dump_stats_get(pg_id, aed_id):
    if not os.path.exists(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}_stats.json"):
        print(f"{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}_stats.json does not exit")
        return {'success': False}
    return send_file(f"../{app.config['EXPORT_PATH']}/{aed_id}/stats/dumps/{pg_id}_stats.json")