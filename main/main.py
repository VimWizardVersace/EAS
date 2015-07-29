# main.py
from threading import Thread
from Queue import Queue

import client_create
import upload_image
import worker_node_init
import scheduling
import movedata

test_conversion_rate = 100

test_deadline = "07/24/2015 12:40:00"

list_of_test_files = ['/Users/rumadera/projects/EAS/scripts/vids/1.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/2.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/3.mp4',
                      '/Users/rumadera/projects/EAS/scripts/vids/5.mp4.mkv']

test_remote_credentials = {"OS_AUTH_URL": "https://us-internal-1.cloud.cisco.com:5000/v2.0",
                           "OS_USERNAME": 'rumadera',
                           "OS_PASSWORD": '1ightriseR!',
                           "OS_TENANT_NAME": 'BXBInternBox' ,
                           "OS_REGION_NAME": 'RegionOne'}

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

    ksclient = client_create.create_keystone_client(credentials)
    glclient = client_create.create_glance_client(ksclient)
    swclient = client_create.create_swift_client(credentials)
    nvclient = client_create.create_nova_client(credentials)

    local_only = False

    ##### IMPORTANT STUFF: #####

    #####################################################

    # FUNCTIONS THAT ARE COMMENTED OUT ARE NOT COMPLETE #

    #####################################################

    """For testing purposes, move a couple of test videos to our local cloud before doing anything"""
    movedata.Move_data_to_local_cloud(swclient, list_of_test_files, container="Videos")

    """Find transcode rate of local cloud"""
    #xcode_rate = find_xcode_rate()

    """Determine what can be done in the alloted time"""
    time_remaining = scheduling.find_epoch_time_until_deadline(test_deadline)
    work_load_to_outsource = scheduling.partition_workload(time_remaining, test_conversion_rate, swclient, "Videos")

    """Given a deadline, workload, and a collection of data, determine which cloud to outsource to"""
    # remote_credentials = find_optimal_cloud(deadline, work_load_to_outsource)
    remote_credentials = test_remote_credentials

    """(ASSUMING THE OPTIMAL CLOUD RUNS OPENSTACK) Given credentials, 
        spawn a new client keystone client so that we may have permission to move files around"""

    remote_ksclient = client_create.create_keystone_client(remote_credentials)
    remote_glclient = client_create.create_glance_client(remote_ksclient)
    remote_nvclient = client_create.create_nova_client(remote_credentials)
    remote_swclient = client_create.create_swift_client(remote_credentials)

    """Using that cloud's api, move the video files to that cloud"""
    # move_data.Move_data_to_remote_cloud_OPENSTACK(swclient, remote_swclient, work_load_to_outsource)

    images = []

    """Start up the image on our local cloud"""
    local_thread = Thread(target=upload_image.upload, args=(glclient, ksclient, images))
    local_thread.start()

    remote_thread = Thread(target=upload_image.upload, args=(remote_glclient, remote_ksclient, images))
    remote_thread.start()


    local_thread.join()
    worker_node_init.activate_image(nvclient, images[0].id, "Transburst Server Group", Flavor=0 , Userdata=None)

    remote_thread.join()
    worker_node_init.activate_image(remote_nvclient, images[1].id, "Remote Transburt Server Group", Flavor=0, Userdata="remote_script.py")
    """Begin transcoding work on local cloud"""
    #???

    """Start up the image on the remote cloud"""

    """Begin transcoding work on remote cloud"""
    #???

    """Retrieve data from remote cloud"""
    #???

