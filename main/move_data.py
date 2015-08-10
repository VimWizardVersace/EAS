from subprocess import call, PIPE, check_output
from swiftclient import client

from threading import Thread
import time




#Move_data_to_local_cloud is used for testing, putting data on our cloud.
#
def MDTLC_helper(swift_client, clip, container):
    print clip
    with open(clip, 'rb') as f:
        swift_client.put_object(container, clip, contents=f, content_type="video")
    print "Done uploading %s" %clip

def Move_data_to_local_cloud(swift_client, ListOfFiles, container="videos"):
    swift_client.put_container(container)
    print "\"Videos\" container created"
    threads = []
    begin = time.time()
    for clip in ListOfFiles:
        threads.append(Thread(target=MDTLC_helper, args=(swift_client, clip, container)))
        threads[-1].start()
    for thread in threads:
        thread.join()
    print "Done uploading to LOCAL cloud..."

def upload_workload_split(swift_client, local_files, remote_files):
    with open("remote_workload.txt", 'w') as f:
        for clip in remote_files:
            f.write(clip+'\n')
        swift_client.put_object("Videos", "remote_workload.txt" , contents= f.read())

    with open("local_workload.txt", 'w') as f:
        for clip in local_files:
            f.write(clip+'\n')
        swift_client.put_object("Videos", "local_workload.txt" , contents= f.read())

# Move_data_from_local_cloud_OPENSTACK is the function we run on the local cloud 
# to move data from our cisco cloud to some remote cloud running openstack
# Note, we must be supplied with the appropriate authentication of the cloud to work
#
def Move_data_to_remote_cloud_OPENSTACK(ListOfFiles, swift_client, remote_swift_client):
    for f in ListOfFiles:
        f_tuple = swift_client.get_object("Videos", f)
        remote_swift_client.put_object("Videos", f, contents=f_tuple[1], content_type="Video")

def Retrieve_data_from_remote_cloud_OPENSTACK(swift_client, remote_swift_client):
    for data in remote_swift_client.get_container("completed")[1]:
        container_data.append('{0}'.format(data['name']))
    for f in container_data:
        with open(f, "rb") as xcode_bytes:
            swift_client.put_object("Completed", f, contents=xcode_bytes)

if __name__ == "__main__":
    ListOfFiles = check_output(["ls"]).split('\n')
    del ListOfFiles[-1]
    Move_data_to_local_cloud(ListOfFiles)