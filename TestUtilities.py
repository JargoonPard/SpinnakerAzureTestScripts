# Utility methods for running python tests of clouddriver
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

#continuously check the deployment until it is complete
def CheckDeployment(deployment_endpoint, headers, timeout):
	print ctime(), ' - Waiting for deployment...'
	sys.stdout.flush()
	loopCounter = 0
	r = requests.get(deployment_endpoint, headers=headers)
	while (r.text.find('error') != -1 and loopCounter <= timeout):
		sleep(5)
		loopCounter += 5
		r = requests.get(deployment_endpoint, headers=headers)
	
	if (loopCounter > timeout):
		return False
		 
	provisioningState = 'none'
	
	print ctime(), ' - Checking deployment state'
	sys.stdout.flush()
	
	loopCounter = 0
	while (provisioningState != 'Succeeded' and loopCounter <= timeout):
		sleep(5)
		loopCounter += 5
		r = requests.get(deployment_endpoint, headers=headers)
		
		provisioningState = r.json()['properties']['provisioningState']
		print ctime(), ' - provisioningState: ', provisioningState
		sys.stdout.flush()
		
	if (loopCounter > timeout):
		print ctime(), ' - Check operation timed out'
		return False
	
	print ctime(), ' - Deployment complete'
	sys.stdout.flush()
	return True
#deployment complete

#get access token_response
def GetAzureAccessHeaders():
	authority = 'https://login.microsoftonline.com/' + os.environ['AZURE_TENANT_ID']
	client_id = os.environ['AZURE_CLIENT_ID']
	client_secret = os.environ['AZURE_APPKEY']

	token_response = adal.acquire_token_with_client_credentials(
		authority,
		client_id,
		client_secret
	)

	access_token = token_response.get('accessToken')
	headers = {"Authorization": 'Bearer ' + access_token}
	return headers