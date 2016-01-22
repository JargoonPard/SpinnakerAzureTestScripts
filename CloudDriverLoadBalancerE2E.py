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

load_balancer_endpoint = 'https://management.azure.com/subscriptions/0b44b9a8-ee7f-4020-a239-8b498e6fd0a2/resourceGroups/azure1_westus/providers/Microsoft.Network/loadBalancers/azureMASM-st1-d11?api-version=2015-05-01-preview'
deployment_endpoint = 'https://management.azure.com/subscriptions/0b44b9a8-ee7f-4020-a239-8b498e6fd0a2/resourceGroups/azure1_westus/providers/microsoft.resources/deployments/azureMASM-st1-d11_deployment?api-version=2015-05-01-preview'

print 'Check for existing load balancer at: ', ctime()
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
print(r.text)

#Hopefully 2 minutes is enough time for Azure to provision the loadbalancer
#Could replace this with a test of the deployment status to make it more robust.
print('sleeping for 120 seconds then check for new load balancer')
print 'start sleep at: ', ctime()
sleep(120)
print 'end sleep at: ', ctime()
r = requests.get(load_balancer_endpoint, headers=headers)
print ctime(), ' - finished checking deployment'

print(r.text)

print('SUCCESS!!')