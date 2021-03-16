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

SCOPES = ["https://www.googleapis.com/auth/postmaster.readonly"]
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

# setup the postmaster API service and fetch the list of domains
service = build("gmailpostmastertools", "v1beta1", credentials=creds)
domains_resource = service.domains()
domains = domains_resource.list().execute()

class PostMasterDomain(Resource):
    def get(self, name):
        if not domains:
             return "No domains found."
        else:
            for domain in domains["domains"]:
                if domain["name"] == "domains/" + name  :
                    return domain, 200

class PostMasterTraffic(Resource):
    def get(self, name):
            try:
                traffic_stats_resource = domains_resource.trafficStats().list(
                    parent="domains/" + name
                )
                traffic_stats = traffic_stats_resource.execute()
                return traffic_stats
            except Exception as e:
                return str(e), 404 

api.add_resource(PostMasterDomain, '/postmaster/domain/<name>')
api.add_resource(PostMasterTraffic, '/postmaster/traffic/<name>') 

if __name__ == '__main__':
    app.run(debug=True)
