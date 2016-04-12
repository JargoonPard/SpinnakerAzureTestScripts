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

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/loadBalancers/' + appName + '-st1-d1?api-version=2016-03-30'

#
# DELETE
#
#delete a loadbalancer through clouddriver
url = clouddriver_host + '/ops'
lb_delete = '[ { "deleteLoadBalancer": { "cloudProvider" : "azure", "providerType" : "azure", "appName" : "' + appName + '", "loadBalancerName" : "' + appName + '-st1-d1", "regions": ["westus"], "credentials": "' + azure_creds + '" }} ]'

print ctime(), ' - Delete load balancer'
sys.stdout.flush()
r = requests.post(url, data = lb_delete, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#validate delete
print ctime(), ' - Validate Delete'
sys.stdout.flush()
authHeaders = TestUtilities.GetAzureAccessHeaders()
r = requests.get(load_balancer_endpoint, headers=authHeaders)

timeout = 3 * 60
loopCounter = 0
while (r.text.find('error') == -1 and loopCounter <= timeout):
	sleep(5)
	loopCounter += 5
	r = requests.get(load_balancer_endpoint, headers=authHeaders)

if (r.json()['error']['code'] == 'ResourceNotFound' or r.json()['error']['code'] == 'NotFound'):
	print ctime(), ' - LoadBalancer Deleted'
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Deletion Failed: ', r.text
	print ctime(), ' - Test Failed'
#end delete validation
#
# DELETE
#
sys.stdout.flush()

