#!/usr/bin/env python
import adal
import requests
import os
import json
from time import sleep, ctime
import sys

clouddriver_host = 'http://localhost:7002'
azure_creds = os.getenv('AZURE_CREDENTIALS', 'azure-cred1')

test_passed = True

full_list = "[{u'sku': u'2012-R2-Datacenter', u'publisher': u'MicrosoftWindowsServer', u'account': u'" + azure_creds + "', u'version': u'4.0.20151214', u'offer': u'WindowsServer', u'region': None, u'uri': None, u'imageName': u'WindowsServer-2012-R2-Datacenter(Recommended)', u'ostype': None, u'isCustom': False}, {u'sku': u'14.04.3-LTS', u'publisher': u'Canonical', u'account': u'" + azure_creds + "', u'version': u'14.04.201602171', u'offer': u'UbuntuServer', u'region': None, u'uri': None, u'imageName': u'UbuntuServer-14.04.3-LTS(Recommended)', u'ostype': None, u'isCustom': False}, {u'sku': u'8', u'publisher': u'credativ', u'account': u'" + azure_creds + "', u'version': u'8.0.201602010', u'offer': u'Debian', u'region': None, u'uri': None, u'imageName': u'Debian-8(Recommended)', u'ostype': None, u'isCustom': False}, {u'sku': u'7.1', u'publisher': u'OpenLogic', u'account': u'" + azure_creds + "', u'version': u'7.1.20150731', u'offer': u'CentOS', u'region': None, u'uri': None, u'imageName': u'CentOS-7.1(Recommended)', u'ostype': None, u'isCustom': False}, {u'sku': u'42.1', u'publisher': u'SUSE', u'account': u'" + azure_creds + "', u'version': u'2016.01.14', u'offer': u'openSUSE-Leap', u'region': None, u'uri': None, u'imageName': u'openSUSE-Leap-42.1(Recommended)', u'ostype': None, u'isCustom': False}, {u'sku': u'12-SP1', u'publisher': u'SUSE', u'account': u'" + azure_creds + "', u'version': u'2015.12.15', u'offer': u'SLES', u'region': None, u'uri': None, u'imageName': u'SLES-12-SP1(Recommended)', u'ostype': None, u'isCustom': False}]"
#
# Find all default vm images
#
# retrieve the list of vm images specifed in the config.yml file
url = clouddriver_host + '/azure/images/find?configOnly=1&q=Recommended'

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


part_list = "[{u'sku': u'2012-R2-Datacenter', u'publisher': u'MicrosoftWindowsServer', u'account': u'" + azure_creds + "', u'version': u'4.0.20151214', u'offer': u'WindowsServer', u'region': None, u'uri': None, u'imageName': u'WindowsServer-2012-R2-Datacenter(Recommended)', u'ostype': None, u'isCustom': False}]"
#
# Find default vm images for a given prefix
#
# retrieve the list of all vm images specifed in the config.yml file that start with 'w'
url = clouddriver_host + '/azure/images/find?configOnly=1&q=windows'

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


