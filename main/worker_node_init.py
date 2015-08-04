# This file contains functions that automate the process for uploading, starting, and creating worker nodes
# in glance.  Dependencies include python glance-client, our proprietary state of the art virtual machine image 
# (courtesy of joe), and python nova.  

from subprocess import call, Popen, PIPE
from novaclient import client
from keystoneclient import session
from keystoneclient.auth.identity import v2
from glanceclient import Client
# after the image is uploaded, you will need to boot it with nova
# first create a nova servergroup
# load the image into the server
#
def activate_image(nova_client, ImageID, ServerName="myserver", Flavor=4, userdata=None):
    print "Booting server..."
    server = nova_client.servers.create(ServerName, ImageID, Flavor)
    nova_client.servers.start(server.id.enconde('ascii'))


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

