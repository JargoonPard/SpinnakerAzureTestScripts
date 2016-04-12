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

load_balancer_endpoint = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourceGroups/' + appName + '-westus/providers/Microsoft.Network/loadBalancers/' + appName + '-st1-d1?api-version=2016-03-30'

print ctime(), ' - Validate Deployment'
authHeaders = TestUtilities.GetAzureAccessHeaders()
r = requests.get(load_balancer_endpoint, headers=authHeaders)

if (r.json()['name'] == 'pytest-st1-d1'):
	print ctime(), ' - LoadBalancer Created'
	print ctime(), ' - Test Passed'
else:
	print ctime(), ' - Creation Failed'
	print ctime(), ' - Test Failed'

sys.stdout.flush()
