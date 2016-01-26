#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

authority = os.environ['AZURE_E2E_AUTHORITY']
client_id = os.environ['AZURE_E2E_CLIENT_ID']
client_secret = os.environ['AZURE_E2E_CLIENT_SECRET']
clouddriver_host = 'http://localhost:7002'

token_response = adal.acquire_token_with_client_credentials(
	'https://login.microsoftonline.com/b06e36c3-7474-4870-96c2-32e263b6344c',
	'3895ac6f-b20c-4055-bff8-71abdfd18bfd',
	'pYhDKB57D+boBm9kB3Up8L5WOaWfkdqQH7I0wm5mLCs='
)

access_token = token_response.get('accessToken')
headers = {"Authorization": 'Bearer ' + access_token}

load_balancer_endpoint = 'https://management.azure.com/subscriptions/0b44b9a8-ee7f-4020-a239-8b498e6fd0a2/resourceGroups/azure1-westus/providers/Microsoft.Network/loadBalancers/azure1-st1-d1?api-version=2015-05-01-preview'

print ctime(), ' - Validate Deployment'
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['name'] == 'azure1-st1-d1'):
	print ctime(), ' - LoadBalancer Created'
else:
	print ctime(), ' - Creation Failed'