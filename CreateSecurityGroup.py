#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

test_passed = True
appName = 'azureTesting'

authority = 'https://login.microsoftonline.com/' + os.environ['AZURE_TENANT_ID']
client_id = os.environ['AZURE_CLIENT_ID']
client_secret = os.environ['AZURE_APPKEY']
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
clouddriver_host = 'http://localhost:7002'
azure_creds = os.getenv('AZURE_CREDENTIALS', 'azure-cred1')

token_response = adal.acquire_token_with_client_credentials(
	authority,
	client_id,
	client_secret
)

access_token = token_response.get('accessToken')
headers = {"Authorization": 'Bearer ' + access_token}

security_group_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/networkSecurityGroups/' + appName + '-st1-d1?api-version=2015-05-01-preview'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-deployment?api-version=2015-11-01'

print ctime(), ' - Check for existing security group'
sys.stdout.flush()
r = requests.get(security_group_endpoint, headers=headers)

#the next line will fail if there is not 'error' as the first element.
#this should pass if the security group has not been created yet
if (not r.json()['error']):
	test_passed = False

#create a new securityGroup through clouddriver
url = clouddriver_host + '/ops'
sg_data = '[ { "upsertSecurityGroup": { "cloudProvider" : "azure", "appName" : "' + appName + '", "securityGroupName" : "' + appName + '-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "' + azure_creds + '", "region" : "westus", "vnet" : "none", "tags" : { "appName" : "testazure4", "stack" : "st1", "detail" : "d1"}, "securityRules" : [ { "name" : "rule1", "description" : "Allow FE Subnet", "access" : "Allow", "destinationAddressPrefix" : "*", "destinationPortRange" : "433", "direction" : "Inbound", "priority" : 100, "protocol" : "TCP", "sourceAddressPrefix" : "10.0.0.0/24", "sourcePortRange" : "*" } ], "name" : "' + appName + '-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Post new security group'
sys.stdout.flush()
r = requests.post(url, data = sg_data, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#continuously check the deployment until it is complete
def CheckDeployment():
	print ctime(), ' - Waiting for deployment...'
	sys.stdout.flush()
	r = requests.get(deployment_endpoint, headers=headers)
	while (r.text.find('error') != -1):
		sleep(10)
		r = requests.get(deployment_endpoint, headers=headers)
	
	provisioningState = 'none'
	
	print ctime(), ' - Checking deployment state'
	sys.stdout.flush()
	
	while (provisioningState != 'Succeeded'):
		sleep(10)
		r = requests.get(deployment_endpoint, headers=headers)
		provisioningState = r.json()['properties']['provisioningState']
		print ctime(), ' - provisioningState: ', provisioningState
		sys.stdout.flush()
		
	print ctime(), ' - Deployment complete'
	sys.stdout.flush()
#deployment complete

CheckDeployment()

#validate creation
print ctime(), ' - Validate Create'
sys.stdout.flush()
r = requests.get(security_group_endpoint, headers=headers)

if (r.json()['name'] == '' + appName + '-st1-d1'):
	print ctime(), ' - securityGroup Created'
	sys.stdout.flush()
else:
	print ctime(), ' - Create Failed'
	sys.stdout.flush()
	test_passed = False
#end creation validation

if (test_passed):
	print('SUCCESS!!')
else:
	print('FAILED')

