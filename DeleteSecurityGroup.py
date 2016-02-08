#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

test_passed = True

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

security_group_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azuresg1-westus/providers/Microsoft.Network/networkSecurityGroups/azuresg1-st1-d1?api-version=2015-05-01-preview'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azuresg1-westus/providers/microsoft.resources/deployments/azuresg1-st1-d1-deployment?api-version=2015-11-01'

#
# DELETE
#
#delete a securityGroup through clouddriver
url = clouddriver_host + '/ops'

sg_delete = '[ { "deleteSecurityGroup": { "cloudProvider" : "azure", "appName" : "azuresg1", "securityGroupName" : "azuresg1-st1-d1", "regions": ["westus"], "credentials": "' + azure_creds + '" }} ]'

print ctime(), ' - Delete security group'
sys.stdout.flush()
r = requests.post(url, data = sg_delete, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#validate delete
sleep(10)
print ctime(), ' - Validate Delete'
sys.stdout.flush()
r = requests.get(security_group_endpoint, headers=headers)

if (not r.json()['error']):
	print ctime(), ' - Deletion Failed: ', r.text
	test_passed = False
else:
	sys.stdout.flush()
	print ctime(), ' - securityGroup Deleted'
	sys.stdout.flush()

#end delete validation
#
# DELETE
#

if (test_passed):
	print('SUCCESS!!')
else:
	print('FAILED')

