#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

authority = 'https://login.microsoftonline.com/' + os.environ['AZURE_TENANT_ID']
client_id = os.environ['AZURE_CLIENT_ID']
client_secret = os.environ['AZURE_APPKEY']
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
clouddriver_host = 'http://localhost:7002'
azure_creds = os.getenv('AZURE_CREDENTIALS', 'azure-cred1')
appName = 'azure1'

token_response = adal.acquire_token_with_client_credentials(
	authority,
	client_id,
	client_secret
)

access_token = token_response.get('accessToken')
headers = {"Authorization": 'Bearer ' + access_token}

scale_set_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '_westus/providers/Microsoft.Network/loadBalancers/' + appName + '-st1-d1?api-version=2015-05-01-preview'

#create a new server group through clouddriver
url = clouddriver_host + '/ops'
server_group_data = '[ { "upsertServerGroup": { "name": ' + appName + '"-st1-d1", "cloudProvider": "azure", "appName": "' + appName + '",  "stack": "st1", "detail": "d1", "credentials": "' + azure_creds + '", "region": "West US", "user": "[anonymous]", "upgradePolicy": "Automatic", "loadBalancerName": "' + appName + '-st1-d1", "image": { "publisher": "Canonical", "offer": "UbuntuServer", "sku": "14.04.3-DAILY-LTS", "version": "14.04.201602010" }, "sku": { "name": "Standard_A1", "tier": "Standard", "capacity": 2 }, "osConfig": { "adminUserName": "spinnakerUser", "adminPassword": "asd!!34ABC" }, "application": "' + appName + '" }} ]'

print ctime(), ' - Post new server group'
r = requests.post(url, data = lb_data, headers={'Content-Type': 'application/json'})
print(r.text)
