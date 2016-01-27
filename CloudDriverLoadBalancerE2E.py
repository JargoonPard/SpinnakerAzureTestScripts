#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

test_passed = True

authority = os.environ['AZURE_E2E_AUTHORITY']
client_id = os.environ['AZURE_E2E_CLIENT_ID']
client_secret = os.environ['AZURE_E2E_CLIENT_SECRET']
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
clouddriver_host = 'http://localhost:7002'

token_response = adal.acquire_token_with_client_credentials(
	authority,
	client_id,
	client_secret
)

access_token = token_response.get('accessToken')
headers = {"Authorization": 'Bearer ' + access_token}

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azure1-westus/providers/Microsoft.Network/loadBalancers/azure1-st1-d1?api-version=2015-05-01-preview'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/azure1-westus/providers/microsoft.resources/deployments/azure1-st1-d1-deployment?api-version=2015-11-01'

print ctime(), ' - Check for existing load balancer'
sys.stdout.flush()
r = requests.get(load_balancer_endpoint, headers=headers)

#the next line will fail if there is not 'error' as the first element.
#this should pass if the load balancer has not been created yet
if (!r.json()['error']):
	test_passed = False

#create a new loadbalancer through clouddriver
url = clouddriver_host + '/ops'
lb_data = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "azure1", "loadBalancerName" : "azure1-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "azure-cred1", "region" : "West US", "vnet" : null, "probes" : [ { "probeName" : "healthcheck1", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck1", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "azure1-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Post new load balancer'
sys.stdout.flush()
r = requests.post(url, data = lb_data, headers={'Content-Type': 'application/json'})
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
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['name'] == 'azure1-st1-d1'):
	print ctime(), ' - LoadBalancer Created'
	sys.stdout.flush()
else:
	print ctime(), ' - Create Failed'
	sys.stdout.flush()
	test_passed = False
#end creation validation

#update the loadbalancer
url = clouddriver_host + '/ops'

lb_update = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "azure1", "loadBalancerName" : "azure1-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "azure-cred1", "region" : "West US", "vnet" : null, "probes" : [ { "probeName" : "healthcheck2", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck2", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "azure1-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Update load balancer'
sys.stdout.flush()
r = requests.post(url, data = lb_update, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()
#end update

#continuously check the deployment until it is complete
CheckDeployment()
#deployment complete

#validate the update
print ctime(), ' - Validate Deployment'
sys.stdout.flush()
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['properties']['probes'][0]['name'] == 'healthcheck2'):
	print ctime(), ' - LoadBalancer Created'
	sys.stdout.flush()
else:
	print ctime(), ' - Creation Failed: ', r.json()['properties']['probes'][0]['name']
	sys.stdout.flush()
	test_passed = False
#end update validation


#
# DELETE
#
#delete a loadbalancer through clouddriver
url = clouddriver_host + '/azure/ops'

lb_delete = '[ { "deleteLoadBalancer": { "cloudProvider" : "azure", "providerType" : "azure", "appName" : "azure1", "loadBalancerName" : "azure1-st1-d1", "region": "West US", "credentials": "azure-cred1" }} ]'

print ctime(), ' - Delete load balancer'
sys.stdout.flush()
r = requests.post(url, data = lb_delete, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#validate delete
print ctime(), ' - Validate Delete'
sys.stdout.flush()
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['error']):
	print ctime(), ' - LoadBalancer Deleted'
	sys.stdout.flush()
else:
	print ctime(), ' - Deletion Failed: ', r.text
	test_passed = False
	sys.stdout.flush()
#end delete validation
#
# DELETE
#

if (test_passed):
	print('SUCCESS!!')
else:
	print('FAILED')