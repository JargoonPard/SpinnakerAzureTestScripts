#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

authority = 'https://login.microsoftonline.com/' + os.environ['AZURE_TENANT_ID']
client_id = os.environ['AZURE_CLIENT_ID']
client_secret = os.environ['AZURE_APPKEY']
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
clouddriver_host = 'http://localhost:7002'

token_response = adal.acquire_token_with_client_credentials(
	authority,
	client_id,
	client_secret
)

access_token = token_response.get('accessToken')
headers = {"Authorization": 'Bearer ' + access_token}

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azure1-westus/providers/Microsoft.Network/loadBalancers/azure1-st1-d1?api-version=2015-05-01-preview'

print ctime(), ' - Validate Deployment'
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['name'] == 'azure1-st1-d1'):
	print ctime(), ' - LoadBalancer Created'
else:
	print ctime(), ' - Creation Failed'
