import time
import operator
import paramiko
import predictor
import urllib2
from subprocess import call, PIPE, Popen, check_output

def find_epoch_time_until_deadline(deadline):
    #WARNING:  Time must be formatted the same as pattern
    #
    try:
        pattern = "%m/%d/%Y %H:%M:%S"
        epoch = int(time.mktime(time.strptime(deadline, pattern)))  
        if (epoch < time.time()):
            raise Exception("Negative deadline")
        return epoch - time.time()
    except (ValueError):
        print "bruh give us a deadline in the form of MM/DD/YYYY HH:MM:SS"
    except Exception as e:
        print e

def partition_workload(time_until_deadline, swiftclient, container_name):
    container_data = []
    for data in swiftclient.get_container(container_name)[1]:
        container_data.append('{0}\t{1}'.format(data['name'], data['bytes']))
    container_data = [token.split('\t') for token in container_data]

    # use a list comprehension to create a list of all the filenames
    file_list = []
    try:
        file_list = [token[0] for token in container_data]
    except IndexError:
        print "error (IndexError): container empty?"
    
    print file_list
    # where we store the partitioned list of videos.
    # Internal lists seperate what is possible to transcode in time on one VM
    partitioned_video_list = []

    # given a time-until-completetion by joe's look up table, we keep decrementing "time_until_deadline" by 
    # these times until it reaches zero, then, create a new list (representing a new vm), and repeat. 
    tmp_t_u_d = time_until_deadline
    print "time left: ", time_until_deadline
    single_vm_capacity = []
    for video in file_list:
        single_vm_capacity.append(video)
        prediction_time = predictor.predict(video)
        if (prediction_time > time_until_deadline):
            print "WARNING:  One of the files is too big to be transcoded by a VM in time.  Maybe cut it up into chunks and reupload it."
            partitioned_video_list.append(single_vm_capacity)
            single_vm_capacity = []
            tmp_t_u_d -= prediction_time
            continue

        if (tmp_t_u_d - prediction_time > 0):
            tmp_t_u_d -= prediction_time
            if (video == file_list[-1]):
                partitioned_video_list.append(single_vm_capacity)
        
        else:
            tmp_t_u_d = time_until_deadline
            partitioned_video_list.append(single_vm_capacity)
            single_vm_capacity = []

    print partitioned_video_list
    return partitioned_video_list


def transcode_job_complete(nova_client, server_list):
    for server in server_list:
        ip_address = nova_client.servers.ips(server)['private'][0]['addr'].encode('ascii')
        url = "http://" + ip_address + ':5000/jobs/status'
        website = urllib2.urlopen(url)
        if "False" == website.read().strip():
            return False
    return True



