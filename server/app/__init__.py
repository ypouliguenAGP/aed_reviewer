from flask import Flask, send_file, Response, make_response, Blueprint
from datetime import datetime
import json

app = Flask(__name__, static_folder='static', static_url_path="/static/")
app.config.from_file("config.json", load=json.load)

from .routes import default, aed_reviewer
app.register_blueprint(aed_reviewer.bp, name='aed_reviewer', url_prefix="/aed_reviewer")


def create_app():
    return app
