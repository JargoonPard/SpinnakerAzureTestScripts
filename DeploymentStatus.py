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

deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azure1-westus/providers/microsoft.resources/deployments/azure1-st1-d1-deployment?api-version=2015-11-01'

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
