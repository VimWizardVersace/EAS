# main.py
from threading import Thread
from Queue import Queue

import client_create
import upload_image
import worker_node_init
import scheduling
import movedata

test_conversion_rate = 100

test_deadline = "07/30/2015 12:40:00"

list_of_test_files = ['/Users/rumadera/projects/EAS/scripts/vids/1.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/2.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/3.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/5.mp4.mkv']

test_remote_credentials = {"OS_AUTH_URL": 'https://us-internal-1.cloud.cisco.com:5000/v2.0',
                           "OS_USERNAME": 'rumadera',
                           "OS_PASSWORD": "1ightriseR!",
                           "OS_TENANT_NAME": 'BXBInternBox'  ,
                           "OS_REGION_NAME":'us-internal-1'}

def parse_config_file(fp):
    file_data = fp.read().split('\n')
    required_credentials = ["STORAGE_URL",
                            "DEADLINE",
                            "OS_AUTH_URL",
                            "OS_USERNAME",
                            "OS_PASSWORD",
                            "OS_TENANT_NAME",
                            "OS_REGION_NAME"]

    usr_credentials = dict()

    try: 
        for line in file_data:
            line = line.split("=")
            if line[0] not in required_credentials:
                raise Exception("Malformed config file: %s is not a variable" %line[0] )
            else:
                required_credentials.remove(line[0])
                usr_credentials[line[0]] = line[1]

        if len(required_credentials) > 0:
            raise Exception("Credentials missing from config file: ", required_credentials)
    except Exception as e:
        print e.args
    except IndexError:
        print "Malformed config file: Each credential must be in the form VARIABLE=VALUE"
    
    else:
        return usr_credentials


if __name__ == "__main__":
    file_pointer = open("transburst.conf", 'r')
    credentials = parse_config_file(file_pointer)
    print "Logging in to "+credentials["OS_AUTH_URL"]+" as "+credentials["OS_USERNAME"]+"..."

    local_only = False

    ksclient = client_create.create_keystone_client(credentials)
    glclient = client_create.create_glance_client(ksclient)
    swclient = client_create.create_swift_client(credentials)
    nvclient = client_create.create_nova_client(credentials)

    ##### IMPORTANT STUFF: #####

    #####################################################

    # FUNCTIONS THAT ARE COMMENTED OUT ARE NOT COMPLETE #

    #####################################################

    """For testing purposes, move a couple of test videos to our local cloud before doing anything"""
    movedata.Move_data_to_local_cloud(swclient, list_of_test_files, container="Videos")

    """Find transcode rate of local cloud"""
    # xcode_rate = find_xcode_rate()

    """Determine what can be done in the alloted time"""
    time_remaining = scheduling.find_epoch_time_until_deadline(test_deadline)
    work_load_to_outsource = scheduling.partition_workload(time_remaining, test_conversion_rate, swclient, "Videos")
    #if len(work_load_to_outsource) == 0:
        #local_only = True

    """Given a deadline, workload, and a collection of data, determine which cloud to outsource to"""
    # remote_credentials = find_optimal_cloud(deadline, work_load_to_outsource)
    remote_credentials = None if local_only else test_remote_credentials

    """(ASSUMING THE OPTIMAL CLOUD RUNS OPENSTACK) Given credentials, 
        spawn a new client keystone client so that we may have permission to move files around"""

    remote_ksclient = client_create.create_keystone_client(remote_credentials)
    remote_glclient = client_create.create_glance_client(remote_ksclient)
    remote_nvclient = client_create.create_nova_client(remote_credentials)
    remote_swclient = client_create.create_swift_client(remote_credentials)

    """Using that cloud's api, move the video files to that cloud"""
    # remote_thread = Thread(target=movedata.Move_data_to_remote_cloud_OPENSTACK, args=(swcleint, remote_swclient, work_load_to_outsource))
    # remote_thread.start()
    # move_data.Move_data_to_remote_cloud_OPENSTACK(swclient, remote_swclient, work_load_to_outsource)


    """Initialize remote and local image objects"""
    remote_image, local_image = None, None


    """Upload image on our local cloud"""
    local_thread = Thread(target=upload_image.upload, args=(glclient, ksclient, local_image))
    local_thread.start()

    """Upload image on the remote cloud"""
    #remote_thread.join()
    remote_thread = Thread(target=upload_image.upload, args=(remote_glclient, remote_ksclient, remote_image))
    remote_thread.start()
    

    """Start server using image on local and remote cloud"""
    local_thread.join()
    local_thread = Thread(target=worker_node_init.activate_image, args=(nvclient, local_image.id, "Transburst Server Group", 0))
    local_thread.start()

    remote_thread.join()
    remote_thread = Thread(target=worker_node_init.activate_image, args=(remote_nvclient, remote_image.id, "Remote Transburt Server Group", 0))
    remote_thread.start()

    """Begin transcoding work on local cloud"""
    # ???

    """Begin transcoding work on remote cloud"""
    #???

    """Retrieve data from remote cloud"""
    #???

