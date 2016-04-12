#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys
import TestUtilities

subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
clouddriver_host = 'http://localhost:7002'
azure_creds = os.getenv('AZURE_CREDENTIALS', 'azure-cred1')
appName = 'pytest'
resourceType = 'securityGroup'
result = True

security_group_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/networkSecurityGroups/' + appName + '-st1-d1?api-version=2016-03-30'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-' + resourceType + '-deployment?api-version=2015-11-01'

url = clouddriver_host + '/ops'
sg_data = '[ { "upsertSecurityGroup": { "cloudProvider" : "azure", "appName" : "' + appName + '", "securityGroupName" : "' + appName + '-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "' + azure_creds + '", "region" : "westus", "vnet" : "none", "tags" : { "appName" : "testazure4", "stack" : "st1", "detail" : "d1"}, "securityRules" : [ { "name" : "rule1", "description" : "Allow FE Subnet", "access" : "Allow", "destinationAddressPrefix" : "*", "destinationPortRange" : "433", "direction" : "Inbound", "priority" : 100, "protocol" : "TCP", "sourceAddressPrefix" : "10.0.0.0/24", "sourcePortRange" : "*" } ], "name" : "' + appName + '-st1-d1", "user" : "[anonymous]" }} ]'

authHeaders = TestUtilities.GetAzureAccessHeaders()

print ctime(), ' - Check for existing security group'
sys.stdout.flush()
r = requests.get(security_group_endpoint, headers=authHeaders)

#the next line will fail if there is not 'error' as the first element.
#this should pass if the security group has not been created yet
if (not r.json()['error']):
	print ctime(), ' - Failed: security group ' + appName + '-st1-d1 aready created'
	result = False
else:
	#create a new securityGroup through clouddriver
	print ctime(), ' - Post new security group'
	sys.stdout.flush()
	r = requests.post(url, data = sg_data, headers={'Content-Type': 'application/json'})
	print ctime(), ' - result: ', (r.text)
	sys.stdout.flush()

	#continuously check the deployment until it is complete
	result = TestUtilities.CheckDeployment(deployment_endpoint, authHeaders, 3 * 60)
	
	#validate creation
	sleep(5)
	print ctime(), ' - Validate Create'
	sys.stdout.flush()
	r = requests.get(security_group_endpoint, headers=authHeaders)
	
	if (result and r.json()['name'] == '' + appName.lower() + '-st1-d1'):
		print ctime(), ' - Security Group Created'
		sys.stdout.flush()
	else:
		print ctime(), ' - Create Failed'
		sys.stdout.flush()
		result = False
	#end creation validation

if (result):
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Test Failed'

sys.stdout.flush()
