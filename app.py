from __future__ import print_function
from flask import Flask, request, jsonify    

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors

app = Flask(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/postmaster.readonly"]

def get_credentials():
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
    return creds

def get_domains_list(domains_resource, print_domains=False):
    domains = domains_resource.list().execute()
    domains_list = []
    if not domains:
        print("No domains found.")
    else:
        if print_domains:
            print("Domains:")
        for domain in domains["domains"]:
            name = domain["name"]
            create_time = domain["createTime"]
            permission = domain["permission"]
            domains_list.append(name)
            if print_domains:
                print(f"    domain.name: {name}")
                print(f"    domain.createTime: {create_time}")
                print(f"    domain.permission: {permission}")
    return domains_list

def get_domain_reputation_list(
    domains_resource,
    domain_name,
    start_day=9,
    end_day=16,
    start_month=3,
    end_month=3,
    start_year=2021,
    end_year=2021,
):
    domain = "domains/" + domain_name
    results = {}
    resource_found = True
    try:
        # fetch first page of results without using pageToken
        traffic_stats = (
            domains_resource.trafficStats()
            .list(
                parent=domain,
                startDate_day=start_day,
                startDate_month=start_month,
                startDate_year=start_year,
                endDate_day=end_day,
                endDate_month=end_month,
                endDate_year=end_year,
            )
            .execute()
        )
        print(f"Traffic stats found for {domain}")
    except Exception as e:
        print(f"No traffic stats found for {domain}: {e}")
        resource_found = False
    # keep fetching pages of results until you break from this loop
    while True and resource_found:
        for daily_stat in traffic_stats["trafficStats"]:
            date = daily_stat["name"].split("/")[-1]
            date_dashed = date[:4] + "-" + date[4:6] + "-" + date[6:]
            results[date_dashed] = daily_stat["domainReputation"]
        # if there is no next page, stop looping
        if "nextPageToken" not in traffic_stats:
            break
        # otherwise, get your next page stats ready
        traffic_stats = (
            domains_resource.trafficStats()
            .list(
                parent=domain,
                pageToken=traffic_stats["nextPageToken"],
                startDate_day=start_day,
                startDate_month=start_month,
                startDate_year=start_yeah,
                endDate_day=end_day,
                endDate_month=end_month,
                endDate_year=end_year,
            )
            .execute()
        )
    return results

@app.route('/print_domain_list/', methods=['GET'])
def print_domain_list():
    creds = get_credentials()
    service = build("gmailpostmastertools", "v1beta1", credentials=creds)       
    domains_resource = service.domains()
    reputations = get_domain_reputation_list(domains_resource, "boxed.com")
    print(reputations)

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
