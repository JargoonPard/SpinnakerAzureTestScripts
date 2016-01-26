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

load_balancer_endpoint = 'https://management.azure.com/subscriptions/0b44b9a8-ee7f-4020-a239-8b498e6fd0a2/resourceGroups/azure1-westus/providers/Microsoft.Network/loadBalancers/azure1-st1-d1?api-version=2015-05-01-preview'
deployment_endpoint = 'https://management.azure.com/subscriptions/0b44b9a8-ee7f-4020-a239-8b498e6fd0a2/resourceGroups/azure1-westus/providers/microsoft.resources/deployments/azure1-st1-d1-deployment?api-version=2015-11-01'

print ctime(), ' - Check for existing load balancer'
r = requests.get(load_balancer_endpoint, headers=headers)

json_output = r.json()

#the next line will fail if there is not 'error' as the first element.
#this should pass if the load balancer has not been created yet
json_output['error']

#create a new loadbalancer through clouddriver
url = clouddriver_host + '/ops'
lb_data = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "azure1", "loadBalancerName" : "azure1-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "azure-cred1", "region" : "West US", "vnet" : null, "probes" : [ { "probeName" : "healthcheck1", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck1", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "azure1-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Post new load balancer'
r = requests.post(url, data = lb_data, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)

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
#deployment complete

#validate creation
print ctime(), ' - Validate Deployment'
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['name'] == 'azure1-st1-d1'):
	print ctime(), ' - LoadBalancer Created'
else:
	print ctime(), ' - Creation Failed'
#end creation validation

#update the loadbalancer
lb_update = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "azure1", "loadBalancerName" : "azure1-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "azure-cred1", "region" : "West US", "vnet" : null, "probes" : [ { "probeName" : "healthcheck2", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck2", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "azure1-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Update load balancer'
r = requests.post(url, data = lb_data, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
#end update

#continuously check the deployment until it is complete
CheckDeployment()
#deployment complete

#validate the update
print ctime(), ' - Validate Deployment'
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['name'] == 'azure1-st1-d1'):
	print ctime(), ' - LoadBalancer Created'
else:
	print ctime(), ' - Creation Failed'
#end update validation

print('SUCCESS!!')