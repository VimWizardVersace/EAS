# main.py
from threading import Thread

import transburst_utils
import client_create
import upload_image
import worker_node_init
import scheduling
import move_data

test_deadline = "07/24/2015 12:40:00"

list_of_test_files = ['/Users/rumadera/projects/EAS/scripts/vids/1.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/3.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/5.mp4.mkv']

test_remote_credentials = {"OS_AUTH_URL": "https://us-internal-1.cloud.cisco.com:5000/v2.0",
                           "OS_USERNAME": 'rumadera',
                           "OS_PASSWORD": ,
                           "OS_TENANT_NAME": 'BXBInternBox' ,
                           "OS_REGION_NAME": 'us-internal-1'}

if __name__ == "__main__":
    file_pointer = open("transburst.conf", 'r')
    credentials = transburst_utils.parse_config_file(file_pointer)
    print "Logging in to "+credentials["OS_AUTH_URL"]+" as "+credentials["OS_USERNAME"]+"..."

    ksclient = client_create.create_keystone_client(credentials)
    glclient = client_create.create_glance_client(ksclient)
    swclient = client_create.create_swift_client(credentials)
    nvclient = client_create.create_nova_client(credentials)
    remote_ksclient, remote_glclient, remote_nvclient, remote_swclient = None, None, None, None

    local_only = False

    ##### IMPORTANT STUFF: #####

    #####################################################
    # FUNCTIONS THAT ARE COMMENTED OUT ARE NOT COMPLETE #
    #####################################################

    """For testing purposes, move a couple of test videos to our local cloud before doing anything"""
    move_data.Move_data_to_local_cloud(swclient, list_of_test_files, container="Videos")

    """Determine what can be done in the alloted time"""
    time_remaining = scheduling.find_epoch_time_until_deadline(test_deadline)
    schedule = scheduling.partition_workload(time_remaining, test_conversion_rate, swclient, "Videos")

    """Start up image on our local cloud"""
    images = []
    remote_workload = []
    upload_image.upload(glclient, ksclient, images)
    local_servers = worker_node_init.spawn(nvclient, images[0].id.encode('ascii'), "Local Transburt Server Group", "local", schedule)
    
    """Determine if a remote cloud is needed"""
    if (len(local_servers) == len(schedule)):
        local_only = True

    # if we can't fit all the workload on the local cloud, send the remaining workload to the remote cloud 
    else:
        remote_workload = schedule[len(local_servers):]

    remote_servers = []
    if (not local_only):
         """Given a deadline, workload, and a collection of data, determine which cloud to outsource to"""
        # remote_credentials = find_optimal_cloud(deadline, work_load_outsourced)
        remote_credentials = test_remote_credentials

        """(ASSUMING THE OPTIMAL CLOUD RUNS OPENSTACK) Given credentials, 
        spawn a new client keystone client so that we may have permission to move files around"""

        remote_ksclient = client_create.create_keystone_client(remote_credentials)
        remote_glclient = client_create.create_glance_client(remote_ksclient)
        remote_nvclient = client_create.create_nova_client(remote_credentials)
        remote_swclient = client_create.create_swift_client(remote_credentials)

        """Using that cloud's api, move the video files to that cloud"""
        move_data.Move_data_to_remote_cloud_OPENSTACK(swclient, remote_swclient, remote_workload)


        """Start up the image on our local cloud"""
        upload_image.upload(remote_glclient, remote_ksclient, images)
        remote_servers = worker_node_init.spawn(remote_nvclient, images[1].id.encode('ascii'), "Remote Transburst Server Group", 'remote', len(remote_workload))


        """Retrieve data from remote cloud"""
        move_data.Get_data_from_remote_cloud(swclient, remote_swclient, container="Videos")

    while (not worker_node_init.transcode_job_complete()):
        continue

    move_data.retrieve_data_from_remote_cloud_OPENSTACK(swclient, remote_swclient)

    worker_node_init.kill_servers(local_servers)
    worker_node_init.kill_servers(remote_servers)

