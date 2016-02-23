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
appName = 'azure1'

scale_set_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '_westus/providers/Microsoft.Network/loadBalancers/' + appName + '-st1-d1?api-version=2015-05-01-preview'
deployment_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/microsoft.resources/deployments/' + appName + '-st1-d1-deployment?api-version=2015-11-01'

#create a new server group through clouddriver
#IMPORTANT  - This requires a loadbalancer to exist with the name <appName>-st1-d1 
#   and a backend address pool named be-<appName>-st1-d1
url = clouddriver_host + '/ops'
server_group_data = '[ { "createServerGroup": { "name": "' + appName + '-st1-d1", "cloudProvider": "azure", "appName": "' + appName + '",  "stack": "st1", "detail": "d1", "credentials": "' + azure_creds + '", "region": "West US", "user": "[anonymous]", "upgradePolicy": "Automatic", "loadBalancerName": "' + appName + '-st1-d1", "image": { "publisher": "Canonical", "offer": "UbuntuServer", "sku": "14.04.3-DAILY-LTS", "version": "14.04.201602010" }, "sku": { "name": "Standard_A1", "tier": "Standard", "capacity": 2 }, "osConfig": { "adminUserName": "spinnakerUser", "adminPassword": "asd!!34ABC" }, "application": "' + appName + '", "type": "createServerGroup" }} ]'

print ctime(), ' - Post new server group'
r = requests.post(url, data = server_group_data, headers={'Content-Type': 'application/json'})
print(r.text)

authHeaders = TestUtilities.GetAzureAccessHeaders()
TestUtilities.CheckDeployment(deployment_endpoint, authHeaders)