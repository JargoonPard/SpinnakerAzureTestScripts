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

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/loadBalancers/' + appName + '-st1-d1?api-version=2016-03-30'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-' + resourceType + '-deployment?api-version=2015-11-01'

#
# UPDATE
#
#update a new loadbalancer through clouddriver
url = clouddriver_host + '/ops'

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
		result = False
	#end update validation
#
# UPDATE
#

if (result):
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Test Failed'

sys.stdout.flush()
