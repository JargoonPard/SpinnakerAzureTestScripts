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
azure_creds = os.environ['AZURE_CREDENTIALS']
if (azure_creds == ''):
 	azure_creds = 'azure-cred1'

token_response = adal.acquire_token_with_client_credentials(
	authority,
	client_id,
	client_secret
)

test_passed = True

full_list = "[{u'sku': u'012-R2-Datacenter', u'publisher': u'MicrosoftWindowsServer', u'account': None, u'version': u'4.0.20151214', u'offer': u'WindowsServer', u'region': None, u'imageName': u'WindowsServer-012-R2-Datacenter (Recommended)'}, {u'sku': u'14.04.3-DAILY-LTS', u'publisher': u'Canonical', u'account': None, u'version': u'14.04.201602010', u'offer': u'UbuntuServer', u'region': None, u'imageName': u'UbuntuServer-14.04.3-DAILY-LTS (Recommended)'}, {u'sku': u'8', u'publisher': u'credativ', u'account': None, u'version': u'8.0.201602010', u'offer': u'Debian', u'region': None, u'imageName': u'Debian-8 (Recommended)'}, {u'sku': u'7.1', u'publisher': u'OpenLogic', u'account': None, u'version': u'7.1.20150731', u'offer': u'CentOS', u'region': None, u'imageName': u'CentOS-7.1 (Recommended)'}, {u'sku': u'42.1', u'publisher': u'SUSE', u'account': None, u'version': u'2016.01.14', u'offer': u'openSUSE-Leap', u'region': None, u'imageName': u'openSUSE-Leap-42.1 (Recommended)'}, {u'sku': u'12-SP1', u'publisher': u'SUSE', u'account': None, u'version': u'2015.12.15', u'offer': u'SLES', u'region': None, u'imageName': u'SLES-12-SP1 (Recommended)'}]"
#
# Find all default vm images
#
# retrieve the list of vm images specifed in the config.yml file
url = clouddriver_host + '/azure/images/find'

print ctime(), ' - Validate virtual image list - full'
sys.stdout.flush()
r = requests.get(url, headers={'Content-Type': 'application/json'})

returned_list = "" + str(r.json())
if (returned_list == full_list):
	print ctime(), ' - Return full list passed'
	test_passed = True
	sys.stdout.flush()
else:
	print ctime(), ' - Return full list failed'
	print ctime(), 'Expected:'
	print full_list
	print ctime(), 'Returned:'
	print returned_list
	sys.stdout.flush()
	test_passed = False

#
# Find all default vm images
#


part_list = "[{u'sku': u'012-R2-Datacenter', u'publisher': u'MicrosoftWindowsServer', u'account': None, u'version': u'4.0.20151214', u'offer': u'WindowsServer', u'region': None, u'imageName': u'WindowsServer-012-R2-Datacenter (Recommended)'}]"
#
# Find default vm images for a given prefix
#
# retrieve the list of all vm images specifed in the config.yml file that start with 'w'
url = clouddriver_host + '/azure/images/find?q=w'

print ctime(), ' - Validate virtual image list - partial'
sys.stdout.flush()
r = requests.get(url, headers={'Content-Type': 'application/json'})

returned_list = "" + str(r.json())
if (returned_list == part_list):
	print ctime(), ' - Return partial list passed'
	test_passed = True
	sys.stdout.flush()
else:
	print ctime(), ' - Return partial list failed'
	print ctime(), 'Expected:'
	print part_list
	print ctime(), 'Returned:'
	print returned_list
	sys.stdout.flush()
	test_passed = False

#
# Find default vm images for a given prefix
#


if (test_passed):
	print('SUCCESS!!')
else:
	print('FAILED')


