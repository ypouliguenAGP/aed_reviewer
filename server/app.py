from flask import Flask, send_file, Response
from datetime import datetime
import json
import os

app = Flask(__name__,
            static_url_path='', 
            static_folder='static/web',
            template_folder='templates')
app.config.from_file("config.json", load=json.load)

@app.after_request
def after_request_func(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.get('/api/protection_groups')
def pgs_get():
    return send_file(f"{app.config['SOURCE_PATH']}/pgs.json")

@app.get('/api/protection_groups/<string:pg_id>')
def pg_details_get(pg_id):
    with open(f"{app.config['SOURCE_PATH']}/pgs.json") as f:
        pgs = json.load(f)
    if pg_id not in pgs:
        return {'success': False, 'message': f'PG {pg_id} not found'}
    data = pgs[pg_id]
    print(f"Associated Server Type is {pgs[pg_id]['server_type']}")
    # Find Server Type
    with open(f"{app.config['SOURCE_PATH']}/sts.json") as f:
        sts = json.load(f)
    if f"{pgs[pg_id]['server_type']}" not in sts:
        return {'success': False, 'message': f'ST associated with {pg_id} not found'}
    data['protections'] = sts[f"{pgs[pg_id]['server_type']}"]
    if os.path.exists(f"{app.config['SOURCE_PATH']}/stats"):
        data['stats'] = True
    return {'success': True, 'data':data}

@app.get('/api/protection_groups/<string:pg_id>/traffic/<string:period>')
def prepare_traffic(pg_id, period='1d'):
    stats = {}
    if os.path.exists(f"{app.config['SOURCE_PATH']}/stats"):
        # Traffic
        if os.path.exists(f"{app.config['SOURCE_PATH']}/stats/traffic/{pg_id}_{period}.json"):
            with open(f"{app.config['SOURCE_PATH']}/stats/traffic/{pg_id}_{period}.json") as f:
                stats['traffic'] = prepare_traffic_data(json.load(f)['timeseries-data'][0])
        # Services
        if os.path.exists(f"{app.config['SOURCE_PATH']}/stats/attacks/{pg_id}_{period}.json"):
            with open(f"{app.config['SOURCE_PATH']}/stats/attacks/{pg_id}_{period}.json") as f:
                stats['attacks'] = prepare_attack_data(json.load(f)['attack-categories']['timeseries'])
        # Locations
        if os.path.exists(f"{app.config['SOURCE_PATH']}/stats/locations/{pg_id}_{period}.json"):
            with open(f"{app.config['SOURCE_PATH']}/stats/locations/{pg_id}_{period}.json") as f:
                stats['locations'] = prepare_location_data(json.load(f)['ip-locations'])
        # Services
        if os.path.exists(f"{app.config['SOURCE_PATH']}/stats/services/{pg_id}_{period}.json"):
            with open(f"{app.config['SOURCE_PATH']}/stats/services/{pg_id}_{period}.json") as f:
                stats['services'] = prepare_services_data(json.load(f)['services'])
        # Protocols
        if os.path.exists(f"{app.config['SOURCE_PATH']}/stats/protocols/{pg_id}_{period}.json"):
            with open(f"{app.config['SOURCE_PATH']}/stats/protocols/{pg_id}_{period}.json") as f:
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
        data[protocol['protoName']] = {
            'bps': [],
            'pps': [],
        }
        for i in range(len(traffic['times'])):
            data[protocol['protoName']]['pps'].append([traffic['times'][i][0]*1000,protocol['pps'][i]])
            data[protocol['protoName']]['bps'].append([traffic['times'][i][0]*1000,protocol['bps'][i]])
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

@app.get('/api/server_types')
def sts_get():
    return send_file(f"{app.config['SOURCE_PATH']}/sts.json")
    

@app.get('/api/global_alerting')
def global_alerting_get():
    return send_file(f"{app.config['SOURCE_PATH']}/global_alerting.json")


@app.get('/api/interfaces')
def interfaces_get():
    return send_file(f"{app.config['SOURCE_PATH']}/interfaces.json")

@app.get('/api/crawlers')
def crawlers_get():
    return send_file(f"{app.config['SOURCE_PATH']}/webcrawlers.json")

@app.get('/api/notifications')
def notifications_get():
    return send_file(f"{app.config['SOURCE_PATH']}/notification_dests.json")


@app.get('/api/protection_groups/<string:pg_id>/changes/')
def pg_logs_get(pg_id):
    if not os.path.exists(f"{app.config['SOURCE_PATH']}/changes.json"):
        return {'success': False}
    # Find associated Server Type
    with open(f"{app.config['SOURCE_PATH']}/pgs.json") as f:
        pgs = json.load(f)
    if pg_id not in pgs:
        return {'success': False, 'message': f'PG {pg_id} not found'}
    st_id = pgs[pg_id]['server_type']
    print(f"Associated Server Type is {st_id}")

    with open(f"{app.config['SOURCE_PATH']}/changes.json") as f:
            data = json.load(f)
    events = []
    if pg_id in data['pg']:
        events += data['pg'][pg_id]
    print(type(st_id))
    if f"{st_id}" in data['st']:
        print(f"{len(data['st'][f"{st_id}"])} Changes found for ST {st_id}")
        events += data['st'][f"{st_id}"]
    return events