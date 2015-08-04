# This file contains functions that automate the process for uploading, starting, and creating worker nodes
# in glance.  Dependencies include python glance-client, our proprietary state of the art virtual machine image 
# (courtesy of joe), and python nova.  

from subprocess import call, Popen, PIPE
from novaclient import client
from novaclient import exceptions
from keystoneclient import session
from keystoneclient.auth.identity import v2
from glanceclient import Client
from time import sleep
from threading import Thread

# after the image is uploaded, you will need to boot it with nova
#
def activate_image(nova_client, ImageID, ServerName, Flavor):
    server = nova_client.servers.create(ServerName, ImageID, Flavor)
    return server


# keep starting servers until we run out of room
#
def spawn(nova_client, ImageID, ServerName, loc, max_num_servers):
    server_list = []
    while True:
        try:
            server = activate_image(nova_client, ImageID, "Transburst Server Group", 3)
            sleep(5)
            server.diagnostics()
        except exceptions.Forbidden:
            print "Local cloud core quota reached"
            break 
        except exceptions.ClientException:
            print "Local cloud resource quota reached"
            server.delete()
            break
        server_list.append(server)
        print "booted %s server #%i" %(len(server_list), loc)
        if (len(server_list) == max_num_servers):
            break
    return server_list





# main is used for testing
#
if __name__ == "__main__":

    auth = v2.Password(auth_url="http://10.0.2.15:35357/v2.0", username="admin", password="light", tenant_name="admin")

    sess = session.Session(auth=auth)

    nova_client = client.Client("2.26.0", session=sess)

    # NOTE: try the swift auth token
    # can be found via command "swift stat -v"
    glance_client = Client('1', endpoint="http://10.131.69.112:9292", token="8520212cd1a34b39b0e9d8d475144abb")

    image = upload_new_image(glance_client, "gather.raw", True)
    activate_image(nova_client, image.id, "test server", 2)

