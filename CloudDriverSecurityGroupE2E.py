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
test_passed = True
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
	test_passed = False
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
		test_passed = False
	#end creation validation

#
# UPDATE
#
# update a new security group through clouddriver

sg_update = '[ { "upsertSecurityGroup": { "cloudProvider" : "azure", "appName" : "' + appName + '", "securityGroupName" : "' + appName + '-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "' + azure_creds + '", "region" : "westus", "vnet" : "none", "tags" : { "appName" : "testazure4", "stack" : "st1", "detail" : "d1"}, "securityRules" : [ { "name" : "rule1", "description" : "Allow FE Subnet", "access" : "Allow", "destinationAddressPrefix" : "*", "destinationPortRange" : "433", "direction" : "Inbound", "priority" : 100, "protocol" : "TCP", "sourceAddressPrefix" : "10.0.0.0/24", "sourcePortRange" : "*" }, { "name" : "rule2", "description" : "Block RDP", "access" : "Deny", "destinationAddressPrefix" : "*", "destinationPortRange" : "3389", "direction" : "Inbound", "priority" : 101, "protocol" : "TCP", "sourceAddressPrefix" : "Internet", "sourcePortRange" : "*" } ], "name" : "' + appName + '-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Update security group'
sys.stdout.flush()
r = requests.post(url, data = sg_update, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

authHeaders = TestUtilities.GetAzureAccessHeaders()

result = TestUtilities.CheckDeployment(deployment_endpoint, authHeaders, 3 * 60)

if (result):
	#validate update
	print ctime(), ' - Validate Deployment'
	sys.stdout.flush()
	r = requests.get(security_group_endpoint, headers=authHeaders)
	
	if (r.json()['properties']['securityRules'][1]['name'] == 'rule2'):
		print ctime(), ' - Security Group Updated'
		sys.stdout.flush()
	else:
		print ctime(), ' - Update Failed: ', r.json()['properties']['securityRules'][1]['name']
		sys.stdout.flush()
		test_passed = False
	#end update validation
else:
	test_passed = False

#
# UPDATE
#

sg_delete = '[ { "deleteSecurityGroup": { "cloudProvider" : "azure", "appName" : "' + appName + '", "securityGroupName" : "' + appName + '-st1-d1", "regions": ["westus"], "credentials": "' + azure_creds + '" }} ]'


#
# DELETE
#
#delete a securityGroup through clouddriver
url = clouddriver_host + '/ops'

print ctime(), ' - Delete security group'
sys.stdout.flush()
r = requests.post(url, data = sg_delete, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#validate delete
print ctime(), ' - Validate Delete'
sys.stdout.flush()
authHeaders = TestUtilities.GetAzureAccessHeaders()
r = requests.get(security_group_endpoint, headers=authHeaders)

timeout = 3 * 60
loopCounter = 0
while (r.text.find('error') == -1 and loopCounter <= timeout):
	sleep(5)
	loopCounter += 5
	r = requests.get(security_group_endpoint, headers=authHeaders)

if (r.json()['error']['code'] == 'ResourceNotFound' or r.json()['error']['code'] == 'NotFound'):
	print ctime(), ' - Securit Group Deleted'
else:
	print ctime(), ' - Deletion Failed: ', r.text
	test_passed = False
#end delete validation
#
# DELETE
#

if (test_passed):
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Test Failed'

sys.stdout.flush()
