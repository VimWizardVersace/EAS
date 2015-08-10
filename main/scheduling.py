import time
import operator
import paramiko
import predictor
from subprocess import call, PIPE, Popen, check_output

def find_epoch_time_until_deadline(deadline):
    #WARNING:  Time must be formatted the same as pattern
    #
    try:
        pattern = "%m/%d/%Y %H:%M:%S"
        epoch = int(time.mktime(time.strptime(deadline, pattern)))  
        return epoch - time.time()
    except (ValueError):
        print "bruh give us a deadline in the form of MM/DD/YYYY HH:MM:SS"

def partition_workload(time_until_deadline, swiftclient, container_name):
    # use curl to connect to the object storage
    # to discover the sizes of the videos to xcode

    container_data = []
    for data in swiftclient.get_container(container_name)[1]:
        container_data.append('{0}\t{1}'.format(data['name'], data['bytes']))
    container_data = [token.split('\t') for token in container_data]

    # get_auth() returns the storage_url and auth_token associated with that account, this
    # would make it easy for joe's indexing thing to find and gain access to the files it
    # needs to look up
    #
    storage_url, auth_token = swiftclient.get_auth()
    storage_url = storage_url.encode('ascii')
    auth_token = auth_token.encode('ascii')

    # use a dictionary comprehension to assemble a filename:size map
    #
    file_list = []
    try:
        file_list = [token[0] for token in container_data]
    except IndexError:
        print "error (IndexError): container empty?"
    
    # where we store the videos. Internal lists seperated by what is possible to transcode in time on one VM
    #
    partitioned_video_list = []

    # given a time-until-completetion by joe's look up table, keep decrementing "time_until_deadline" by 
    # these times until it reaches zero, then, create a new list (representing a new vm), and repeat. 
    #
    tmp_t_u_d = time_until_deadline
    single_vm_capacity = []
    for video in file_list:
        prediction_time = predictor.predict(video)

        if (prediction_time > time_until_deadline):
            raise Exception("One of the files is too big to be transcoded by a VM in time.  Maybe cut it up into chunks and reupload it.")
        
        elif (tmp_t_u_d - prediction_time > 0):
            single_vm_capacity.append(video)
            tmp_t_u_d -= prediction_time
        
        else:
            tmp_t_u_d = time_until_deadline
            partitioned_video_list.append(single_vm_capacity)
            single_vm_capacity = []

    return partitioned_video_list




