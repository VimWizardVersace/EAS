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
    print time.time() - begin
    print "Done uploading to LOCAL cloud..."

# Move_data_from_local_cloud_OPENSTACK is the function we run on the local cloud 
# to move data from our cisco cloud to some remote cloud running openstack
# Note, we must be supplied with the appropriate authentication of the cloud to work
#
def Move_data_to_remote_cloud_OPENSTACK(ListOfFiles, swift_client, remote_swift_client):
    "give me a moment"

if __name__ == "__main__":
    ListOfFiles = check_output(["ls"]).split('\n')
    del ListOfFiles[-1]
    Move_data_to_local_cloud(ListOfFiles)