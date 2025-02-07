from flask import Flask, send_file, Response, make_response, Blueprint
from app import app


@app.get('/')
def home():
    return 'OK default'