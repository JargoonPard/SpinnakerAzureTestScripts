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

#
# UPDATE
#
#update a new loadbalancer through clouddriver
url = clouddriver_host + '/ops'

lb_update = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "azure1", "loadBalancerName" : "azure1-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "azure-cred1", "region" : "West US", "vnet" : null, "probes" : [ { "probeName" : "healthcheck2", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck2", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "azure1-st1-d1", "user" : "[anonymous]" }} ]'

print ctime(), ' - Update load balancer'
sys.stdout.flush()
r = requests.post(url, data = lb_update, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

#continuously check the deployment until it is complete
print ctime(), ' - Checking deployment state'
sys.stdout.flush()
provisioningState = 'none'

while (provisioningState != 'Succeeded'):
	sleep(10)
	r = requests.get(deployment_endpoint, headers=headers)
	provisioningState = r.json()['properties']['provisioningState']
	print ctime(), ' - provisioningState: ', provisioningState
	sys.stdout.flush()
	
print ctime(), ' - Deployment complete'
sys.stdout.flush()
#deployment complete

#validate update
print ctime(), ' - Validate Deployment'
sys.stdout.flush()
r = requests.get(load_balancer_endpoint, headers=headers)

if (r.json()['properties']['probes'][0]['name'] == 'healthcheck2'):
	print ctime(), ' - LoadBalancer Created'
	sys.stdout.flush()
else:
	print ctime(), ' - Creation Failed: ', r.json()['properties']['probes'][0]['name']
	sys.stdout.flush()
#end update validation
#
# UPDATE
#

print('SUCCESS!!')