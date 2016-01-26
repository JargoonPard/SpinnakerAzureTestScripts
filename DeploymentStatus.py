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

deployment_endpoint = 'https://management.azure.com/subscriptions/0b44b9a8-ee7f-4020-a239-8b498e6fd0a2/resourceGroups/azure1-westus/providers/microsoft.resources/deployments/azure1-st1-d1-deployment?api-version=2015-11-01'

#continuously check the deployment until it is complete
def CheckDeployment():
	print ctime(), ' - Waiting for deployment...'
	r = requests.get(deployment_endpoint, headers=headers)
	while (r.text.find('error') != -1):
		sleep(10)
		r = requests.get(deployment_endpoint, headers=headers)
	
	provisioningState = 'none'
	
	print ctime(), ' - Checking deployment state'
	while (provisioningState != 'Succeeded'):
		sleep(10)
		r = requests.get(deployment_endpoint, headers=headers)
		provisioningState = r.json()['properties']['provisioningState']
		print ctime(), ' - provisioningState: ', provisioningState
		
	print ctime(), ' - Deployment complete'
	
CheckDeployment()

print('SUCCESS!!')