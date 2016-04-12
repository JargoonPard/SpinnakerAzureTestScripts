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

server_group_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/networkSecurityGroups/' + appName + '-st1-d1?api-version=2016-03-30'
sg_destroy = '[ { "destroyServerGroup": { "cloudProvider" : "azure", "appName" : "' + appName + '", "serverGroupName" : "' + appName + '-st1-d1-v000", "regions": ["westus"], "credentials": "' + azure_creds + '" }} ]'


#
# DESTROY
#
# destroy a Server Group through clouddriver
url = clouddriver_host + '/ops'

print ctime(), ' - Destroy server group'
sys.stdout.flush()
r = requests.post(url, data = sg_destroy, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#validate delete
print ctime(), ' - Validate Delete'
sys.stdout.flush()
authHeaders = TestUtilities.GetAzureAccessHeaders()
r = requests.get(server_group_endpoint, headers=authHeaders)

timeout = 10 * 60
loopCounter = 0
while (r.text.find('error') == -1 and loopCounter <= timeout):
	sleep(5)
	loopCounter += 5
	r = requests.get(server_group_endpoint, headers=authHeaders)

if (loopCounter > timeout):
	print ctime(), ' - Check operation timed out'

if (r.json()['error']['code'] == 'ResourceNotFound' or r.json()['error']['code'] == 'NotFound'):
	print ctime(), ' - Server Group Destroyed'
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Destroy Failed: ', r.text
	print ctime(), ' - Test Failed'
#end delete validation
#
# DESTROY
#
sys.stdout.flush()

