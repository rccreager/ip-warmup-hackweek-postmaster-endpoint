from __future__ import print_function

from flask import Flask, request
from flask_restful import Resource, Api

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors

app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)  
