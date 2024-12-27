from flask import Flask, send_file, Response
from datetime import datetime

app = Flask(__name__)
app = Flask(__name__,
            static_url_path='', 
            static_folder='static/web',
            template_folder='templates')

@app.get('/api/protection_groups')
def pgs_get():
    return send_file('../exports/DINUM/bd2/pgs.json')

@app.get('/api/server_types')
def sts_get():
    return send_file('../exports/DINUM/bd2/sts.json')

@app.get('/api/global_alerting')
def global_alerting_get():
    return send_file('../exports/DINUM/bd2/global_alerting.json')
