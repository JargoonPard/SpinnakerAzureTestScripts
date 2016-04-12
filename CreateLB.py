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
	result = False
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
		result = False
	#end creation validation

if (result):
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Test Failed'

sys.stdout.flush()
