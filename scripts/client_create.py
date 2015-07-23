# A collection of functions that spawn openstack clients
import keystoneclient.v2_0.client as ksclient
from keystoneclient import session
from keystoneclient.auth.identity import v2

import glanceclient.v2.client as glclient

from novaclient import client

from swiftclient import Connection

def create_keystone_client(credentials):
	keystone = ksclient.Client(auth_url=credentials["OS_AUTH_URL"],
	                           username=credentials["OS_USERNAME"],
	                           password=credentials["OS_PASSWORD"],
	                           tenant_name=credentials["OS_TENANT_NAME"],
	                           region_name=credentials["OS_REGION_NAME"])
	try:
		return keystone
	except:
		print "KEYSTONE AUTHENTICATION FAILURE.  Check config file."

def create_nova_client(credentials):
	auth = v2.password(	auth_url=credentials["OS_AUTH_URL"],
						username=credentials["OS_USERNAME"],
	                    password=credentials["OS_PASSWORD"],
	                    tenant_name=credentials["OS_TENANT_NAME"])

	sess = session.Session(auth=auth)
	nova = client.Client("2", session=sess)
	return nova

def create_swift_client(credentials):
	swift = Connection(user=credentials["OS_USERNAME"],
						key=credentials["OS_PASSWORD"],
						authurl=credentials["OS_AUTH_URL"],
						tenant_name=credentials["OS_TENANT_NAME"],
						auth_version="2.0")
	return swift

def create_glance_client(keystone_client):
	glance_endpoint = keystone_client.service_catalog.url_for(service_type='image')
	glance = glclient.Client(endpoint=glance_endpoint, token=keystone_client.auth_token)
	return glance