#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

#You need to provide your own credentials as environment variables.
authority = 'https://login.microsoftonline.com/' + os.environ['AZURE_TENANT_ID']
client_id = os.environ['AZURE_CLIENT_ID']
client_secret = os.environ['AZURE_APPKEY']
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
clouddriver_host = 'http://localhost:7002'
azure_creds = os.environ['AZURE_CREDENTIALS']
if (azure_creds == ''):
 	azure_creds = 'azure-cred1'

token_response = adal.acquire_token_with_client_credentials(
	authority,
	client_id,
	client_secret
)

access_token = token_response.get('accessToken')
headers = {"Authorization": 'Bearer ' + access_token}

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azure1-westus/providers/Microsoft.Network/loadBalancers/azure1-st1-d1?api-version=2015-05-01-preview'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azure1-westus/providers/microsoft.resources/deployments/azure1-st1-d1-deployment?api-version=2015-11-01'

#
# DELETE
#
#delete a loadbalancer through clouddriver
url = clouddriver_host + '/ops'

lb_delete = '[ { "deleteLoadBalancer": { "cloudProvider" : "azure", "providerType" : "azure", "appName" : "azure1", "loadBalancerName" : "azure1-st1-d1", "regions": [{"westus"}], "credentials": "' + azure_creds + '" }} ]'

print ctime(), ' - Delete load balancer'
sys.stdout.flush()
r = requests.post(url, data = lb_delete, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#validate delete
print ctime(), ' - Validate Delete'
sys.stdout.flush()
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['error']):
	print ctime(), ' - LoadBalancer Deleted'
	sys.stdout.flush()
else:
	print ctime(), ' - Deletion Failed: ', r.text
	sys.stdout.flush()
#end delete validation
#
# DELETE
#
