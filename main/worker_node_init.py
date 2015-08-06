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
from request import post

# after the image is uploaded, you will need to boot it with nova
#
def activate_image(nova_client, ImageID, ServerName, Flavor):
    server = nova_client.servers.create(ServerName, ImageID, Flavor)
    return server

# once you get a server object, that information is constant.  
# in order to get the most up to date information on a nova server, you
# must ask for it again.  this is used primarily for finding the status
# of a machine (active, error, building...)
#
def update_status(nova_client, server):
    server = nova_client.servers.get(server.id)
    return server

def post_workload(nova_client, server, workload):
    ip_address = nova_client.servers.ips(server)
    files_to_download = {'file': open(workload, 'rb')}
    r = request.post(ip_address, files=files_to_download)
    pass

# keep spamming servers until we run out of room
#
def spawn(nova_client, ImageID, ServerName, loc, schedule):
    server_list = []
    print "Spawning transburst servers..."
    while True:
        try:    
            # make a unique workload file for each individual VM from the schedule list.
            workload = schedule[len(server_list)]
            f = open("workload.txt",'w')
            for video in workload:
                f.write(video+'\n')

            # files argument takes a dictionary where keys are destination path and value is the contents of the file
            # on the server, we can create a file called "workload.txt"
            # and put that vm's workload in that file.
            server = activate_image(nova_client, ImageID, "Transburst Server Group", 3)

            # using the rest api, send the workload to the vm.
            post_workload(nova_client, server, "workload.txt")
            
            # keep checking to make sure the server has been booted.
            # if an error state is reached, fall back.
            while (not is_done_booting(server)):
                server = update_status(nova_client, server)
                if (server.status == "ERROR"):
                    server.delete()
                    return server_list
                continue

        except exceptions.Forbidden:
            print "Your credentials don't give you access to building servers."
            break

        except exceptions.RateLimit:
            print "Rate limit reached"
            print "3..."
            sleep(1)
            print "2..."
            sleep(1)
            print"1..."
            sleep(1)
            continue

        except (exceptions.ClientException, exceptions.OverLimit) as e:
            print "Local cloud resource quota reached"
            break

        # it's probably a good idea to keep these servers stored somewhere easily accessible    
        server_list.append(server)
        print "booted %s server #%i" %(loc, len(server_list))
  
        # check to see if we booted enough vms
        if (len(server_list) == len(schedule)):
            break

    return server_list

# checks the server status to see if it's still building  
#
def is_done_booting(server):
    if (server.status == "BUILD"):
        return False
    else:
        return True

# clean up time
#
def kill_servers(server_list):
    for server in server_list:
        server.delete()


# given the resources you have available and the resources a single vm consumes,
# calculate how many vms you can fit on your cloud.
#
def find_local_max_number_of_vms(nova_client, tenant_name, flavor):
    flavor = nova_client.flavors.get(flavor)
    ram_per_vm = flavor.ram
    cores_per_vm = flavor.vpus 

    quota = nova_client.quotas.get(tenant_name)
    max_ram = quota.ram
    max_cores = quota.cores
    max_servers = quota.server_groups

    num_vms = min(max_ram/ram_per_vm, max_cores/cores_per_vm, max_servers)
    return num_vms

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

