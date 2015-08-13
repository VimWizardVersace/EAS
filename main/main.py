# main.py

from time import sleep
import json

from ingest import ingest
import worker_node_init
import client_create
import upload_image
import scheduling
import move_data

test_deadline = "08/12/2015 20:00:00"

remote_credentials = {"OS_AUTH_URL": "https://us-internal-1.cloud.cisco.com:5000/v2.0",
                       "OS_USERNAME": 'rumadera',
                       "OS_PASSWORD": '1ightriseR!',
                       "OS_TENANT_NAME": 'BXBInternBox' ,
                       "OS_REGION_NAME": 'us-internal-1'}

if __name__ == "__main__":
    credentials = json.load(open('transburst.json'))
    print "Logging in to "+credentials["OS_AUTH_URL"]+" as "+credentials["OS_USERNAME"]+"..."

    ingest(credentials)

    ksclient = client_create.create_keystone_client(credentials)
    glclient = client_create.create_glance_client(ksclient)
    swclient = client_create.create_swift_client(credentials)
    nvclient = client_create.create_nova_client(credentials)
    remote_ksclient, remote_glclient, remote_nvclient, remote_swclient = None, None, None, None

    local_only = True
    test_deadline = credentials["DEADLINE"]

    ##### IMPORTANT STUFF: #####

    #####################################################
    # FUNCTIONS THAT ARE COMMENTED OUT ARE NOT COMPLETE #
    #####################################################

    """For testing purposes, move a couple of test videos to our local cloud before doing anything"""
   #move_data.Move_data_to_local_cloud(swclient, list_of_test_files, container="Videos")

    """Determine what can be done in the alloted time"""
    time_remaining = scheduling.find_epoch_time_until_deadline(test_deadline)
    schedule = scheduling.partition_workload(time_remaining, swclient, "videos")
    print "Predicted number of instances needed: ",len(schedule)

    images = []

    """Check if our image is already on the cloud, if it isn't, upload it"""
    image = upload_image.find_image(glclient)
    if image == None:
        upload_image.upload(glclient, ksclient, images)
    else:
        images.append(image)

    """Start up image on our local cloud"""
    flavor = worker_node_init.find_flavor(nvclient, RAM=4096, vCPUS=2)
    local_servers = worker_node_init.spawn(nvclient, images[0], "Local Transburt Server Group", "local", [], flavor)
    
    """Determine if a remote cloud is needed"""
    remote_workload = []
    if (len(local_servers) < len(schedule)):
    # if we can't fit all the workload on the local cloud, send the remaining workload to the remote cloud 
        local_only = False
        remote_workload = schedule[len(local_servers):]

    print "Predicted number of instances needed on local cloud: ", len(local_servers)
    print "Predicted number of instances needed on remote cloud: ", len(remote_workload)

    remote_servers = []
    if (not local_only):
        """Given a deadline, workload, and a collection of data, determine
         which cloud to outsource to"""
        # remote_credentials = find_optimal_cloud(deadline, work_load_outsourced)        

        print "Logging in to "+remote_credentials["OS_AUTH_URL"]+" as "+remote_credentials["OS_USERNAME"]+"..."

        """(ASSUMING THE OPTIMAL CLOUD RUNS OPENSTACK) Given credentials, 
        spawn a new client keystone client so that we may have permission to move files around"""

        remote_ksclient = client_create.create_keystone_client(remote_credentials)
        remote_glclient = client_create.create_glance_client(remote_ksclient)
        remote_nvclient = client_create.create_nova_client(remote_credentials)
        remote_swclient = client_create.create_swift_client(remote_credentials)

        print "Moving data to remote cloud..."
        """Using that cloud's api, move the video files to that cloud"""
        move_data.Move_data_to_remote_cloud_OPENSTACK(swclient, remote_swclient, remote_workload)


        """Check if our image exists on the remote cloud, if not, upload it"""
        image = upload_image.find_image(glclient)
        if image == None:
            upload_image.upload(glclient, ksclient, images)
        else:
            print "Image found on remote cloud!"
            images.append(image)


        """Start up the image on our remote cloud"""
        remote_servers = worker_node_init.spawn(remote_nvclient, images[1], "Remote Transburst Server Group", 'remote', len(remote_workload))

        """Wait for a signal from the workers saying that they are done"""
        while not scheduling.transcode_job_complete(nvclient, remote_servers,
                                                    'remote'):
            sleep(5)

        """Once the job is complete, kill the servers"""
        #worker_node_init.kill_servers(remote_servers)
        
        """Retrieve data from remote cloud"""
        move_data.retrieve_data_from_remote_cloud_OPENSTACK(swclient, remote_swclient)

    print "Waiting for response from worker nodes..."
    while not scheduling.transcode_job_complete(nvclient, local_servers,
                                                'local'):
        sleep(5)

    print "JOB COMPLETE!"
    #worker_node_init.kill_servers(local_servers)

