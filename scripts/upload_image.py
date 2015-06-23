from os import environ as env
import keystoneclient.v2_0.client as ksclient
import glanceclient.v2.client as glclient

OS_AUTH_URL = 'https://us-internal-1.cloud.cisco.com:5000/v2.0'
OS_TENANT_ID = '0bcdc2b0a4274578a95b780f954b69cf'
OS_TENANT_NAME = 'BXBInternBox'
OS_USERNAME = 'josephor'
OS_PASSWORD = '46exeGLS16RN'

keystone = ksclient.Client(auth_url=OS_AUTH_URL,
                           username=OS_USERNAME,
                           password=OS_PASSWORD,
                           tenant_name=OS_TENANT_NAME)

glance_endpoint = keystone.service_catalog.url_for(service_type='image')
glance = glclient.Client(glance_endpoint, token=keystone.auth_token)

