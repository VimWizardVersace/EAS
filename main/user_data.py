# this is a script that will run on the remote server immediately on start up
# the purpose of this script is to retrieve the video files from the local object-store

from swift import Connection

swclient = Connection(user="admin",
                      key="light",
                      authurl="http://10.131.69.112:35357/v2.0",
                      tenant_name="admin",
                      auth_version="2.0")

# the files which will be exported to the remote cloud would be stored in remote_workload.txt
file_tuple = swclient.get_object("Videos", "remote_workload.txt")
with open("remote_workload.txt", 'w') as remote_workload:
    remote_workload.write(file_tuple[1])


fp = open("remote_workload.txt", 'r')
list_of_files_to_transcode = fp.read().split('\n')

# using swclient, actually get the objects
for clip in list_of_files_to_transcode:
    swclient.get_object("Videos", clip)