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
resourceType = 'loadBalancer'
result = True
test_passed = True

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/loadBalancers/' + appName + '-st1-d1?api-version=2016-03-30'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-' + resourceType + '-deployment?api-version=2015-11-01'

url = clouddriver_host + '/ops'
lb_data = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "' + appName + '", "loadBalancerName" : "' + appName + '-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "' + azure_creds + '", "region" : "westus", "vnet" : null, "probes" : [ { "probeName" : "healthcheck1", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck1", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "' + appName + '-st1-d1", "user" : "[anonymous]" }} ]'

authHeaders = TestUtilities.GetAzureAccessHeaders()

print ctime(), ' - Check for existing load balancer'
sys.stdout.flush()
r = requests.get(load_balancer_endpoint, headers=authHeaders)

#the next line will fail if there is not 'error' as the first element.
#this should pass if the security group has not been created yet
if (r.text.find('error') == -1):
	print ctime(), ' - Failed: load balancer ' + appName + '-st1-d1 aready created'
	test_passed = False
else:
	#create a new loadbalancer through clouddriver
	print ctime(), ' - Post new load balancer'
	r = requests.post(url, data = lb_data, headers={'Content-Type': 'application/json'})
	print(r.text)
	
	result = TestUtilities.CheckDeployment(deployment_endpoint, authHeaders, 3 * 60)
	
	#validate creation
	sleep(5)
	print ctime(), ' - Validate Create'
	sys.stdout.flush()
	r = requests.get(load_balancer_endpoint, headers=authHeaders)
	
	if (result and r.json()['name'] == '' + appName.lower() + '-st1-d1'):
		print ctime(), ' - LoadBalancer Created'
		sys.stdout.flush()
	else:
		print ctime(), ' - Create Failed'
		sys.stdout.flush()
		test_passed = False
	#end creation validation

#
# UPDATE
#
# update a new loadbalancer through clouddriver

lb_update = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "' + appName + '", "loadBalancerName" : "' + appName + '-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "' + azure_creds + '", "region" : "westus", "vnet" : null, "probes" : [ { "probeName" : "healthcheck2", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck2", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "azure1-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Update load balancer'
r = requests.post(url, data = lb_update, headers={'Content-Type': 'application/json'})
print(r.text)

authHeaders = TestUtilities.GetAzureAccessHeaders()

result = TestUtilities.CheckDeployment(deployment_endpoint, authHeaders, 3 * 60)

if (result):
	#validate update
	print ctime(), ' - Validate Deployment'
	sys.stdout.flush()
	r = requests.get(load_balancer_endpoint, headers=authHeaders)
	
	if (r.json()['properties']['probes'][0]['name'] == 'healthcheck2'):
		print ctime(), ' - LoadBalancer Updated'
		sys.stdout.flush()
	else:
		print ctime(), ' - Update Failed: ', r.json()['properties']['probes'][0]['name']
		sys.stdout.flush()
		test_passed = False
	#end update validation
else:
	test_passed = False
#
# UPDATE
#


#
# DELETE
#
# delete a loadbalancer through clouddriver
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
else:
	print ctime(), ' - Deletion Failed: ', r.text
	print ctime(), ' - Test Failed'
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
