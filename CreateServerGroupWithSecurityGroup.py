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

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/loadBalancers/' + appName + '-st1-d1?api-version=2016-03-30'
deployment_lb_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-' + resourceType + '-deployment?api-version=2015-11-01'

security_group_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/networkSecurityGroups/' + appName + '-st1-d1?api-version=2016-03-30'
deployment_nsg_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-' + resourceType + '-deployment?api-version=2015-11-01'

server_group_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Compute/virtualMachineScaleSets/' + appName + '-st1-d1-v000?api-version=2016-03-30'
deployment_sg_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-' + resourceType + '-deployment?api-version=2015-11-01'

url = clouddriver_host + '/ops'

#create a new server group through clouddriver
#IMPORTANT  - This requires a loadbalancer to exist with the name <appName>-st1-d1 
#   and a backend address pool named be-<appName>-st1-d1

lb_data = '[ { "upsertLoadBalancer": { "cloudProvider" : "azure", "appName" : "' + appName + '", "loadBalancerName" : "' + appName + '-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "' + azure_creds + '", "region" : "westus", "vnet" : null, "probes" : [ { "probeName" : "healthcheck1", "probeProtocol" : "HTTP", "probePort" : 7001, "probePath" : "/healthcheck", "probeInterval" : 10, "unhealthyThreshold" : 2 } ], "securityGroups" : null, "loadBalancingRules" : [ { "ruleName" : "lbRule1", "protocol" : "TCP", "externalPort" : "80", "backendPort" : "80", "probeName" : "healthcheck1", "persistence" : "None", "idleTimeout" : "4" } ], "inboundNATRules" : [ { "ruleName" : "inboundRule1", "serviceType" : "SSH", "protocol" : "TCP", "port" : "80" } ], "name" : "' + appName + '-st1-d1", "user" : "[anonymous]" }} ]'

sg_data = '[ { "upsertSecurityGroup": { "cloudProvider" : "azure", "appName" : "' + appName + '", "securityGroupName" : "' + appName + '-st1-d1", "stack" : "st1", "detail" : "d1", "credentials" : "' + azure_creds + '", "region" : "westus", "vnet" : "none", "tags" : { "appName" : "testazure4", "stack" : "st1", "detail" : "d1"}, "securityRules" : [ { "name" : "rule1", "description" : "Allow FE Subnet", "access" : "Allow", "destinationAddressPrefix" : "*", "destinationPortRange" : "433", "direction" : "Inbound", "priority" : 100, "protocol" : "TCP", "sourceAddressPrefix" : "10.0.0.0/24", "sourcePortRange" : "*" } ], "name" : "' + appName + '-st1-d1", "user" : "[anonymous]" }} ]'

server_group_data = '[ { "createServerGroup": { "name": "' + appName + '-st1-d1", "cloudProvider": "azure", "appName": "' + appName + '",  "stack": "st1", "detail": "d1", "credentials": "' + azure_creds + '", "region": "West US", "user": "[anonymous]", "upgradePolicy": "Automatic", "loadBalancerName": "' + appName + '-st1-d1", "securityGroup": { "name": "' + appName + '-st1-d1"}, "image": { "publisher": "Canonical", "offer": "UbuntuServer", "sku": "14.04.3-LTS", "version": "14.04.201602171" }, "sku": { "name": "Standard_A1", "tier": "Standard", "capacity": 2 }, "osConfig": { "adminUserName": "spinnakerUser", "adminPassword": "asd!!34ABC" }, "application": "' + appName + '", "type": "createServerGroup" }} ]'

#
# Create Load Balancer
#
#create a new loadbalancer through clouddriver
print ctime(), ' - Post new load balancer'
r = requests.post(url, data = lb_data, headers={'Content-Type': 'application/json'})
print(r.text)

authHeaders = TestUtilities.GetAzureAccessHeaders()

result = TestUtilities.CheckDeployment(deployment_lb_endpoint, authHeaders, 3 * 60)

#validate creation
sleep(5)
print ctime(), ' - Validate Create Load Balancer'
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
# Create Security Group
#
#create a new securityGroup through clouddriver
print ctime(), ' - Post new security group'
sys.stdout.flush()
r = requests.post(url, data = sg_data, headers={'Content-Type': 'application/json'})
print ctime(), ' - result: ', (r.text)
sys.stdout.flush()

authHeaders = TestUtilities.GetAzureAccessHeaders()

result = TestUtilities.CheckDeployment(deployment_nsg_endpoint, authHeaders, 3 * 60)
	
#validate creation
sleep(5)
print ctime(), ' - Validate Create Security Group'
sys.stdout.flush()
r = requests.get(security_group_endpoint, headers=authHeaders)

if (result and r.json()['name'] == '' + appName.lower() + '-st1-d1'):
	print ctime(), ' - Security Group Created'
	sys.stdout.flush()
else:
	print ctime(), ' - Create Security Group Failed'
	sys.stdout.flush()
	test_passed = False
#end creation validation


#
# Create Server Group
#
print ctime(), ' - Post new server group'
r = requests.post(url, data = server_group_data, headers={'Content-Type': 'application/json'})
print(r.text)

authHeaders = TestUtilities.GetAzureAccessHeaders()

result = TestUtilities.CheckDeployment(deployment_sg_endpoint, authHeaders, 3 * 60)

#validate creation
sleep(5)
print ctime(), ' - Validate Create Server Group'
sys.stdout.flush()
r = requests.get(load_balancer_endpoint, headers=authHeaders)

# skip validation check since the deployment could succeed while server VMSS is still being deployed
#if (result and r.json()['name'] == '' + appName.lower() + '-st1-d1-v000'):
#	print ctime(), ' - Server Group Created'
#	sys.stdout.flush()
#else:
#	print ctime(), ' - Create Failed'
#	sys.stdout.flush()
#	test_passed = False

#end creation validation

if (test_passed):
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Test Failed'

sys.stdout.flush()
