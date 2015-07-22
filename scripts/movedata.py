from subprocess import call, PIPE, check_output
from swiftclient import client

#Move_data_to_local_cloud is used for testing, putting data on our cloud.
#
def Move_data_to_local_cloud(ListOfFiles):
	for clip in ListOfFiles:
		subprocess.call(["Swift upload videos "+clip])

# Move_data_from_local_cloud_OPENSTACK is the function we run on the local cloud 
# to move data from our cisco cloud to some remote cloud running openstack
# Note, we must be supplied with the appropriate authentication of the cloud to work
#
def Move_data_to_remote_cloud_OPENSTACK(ListOfFiles, OS_AUTH_URL, OS_USERNAME, OS_PASSWORD):
	for clip in ListOfFiles:
		subprocess.call(["Swift --os_auth_url %s --os_username %s --os_password %s upload videos %s" %(OS_AUTH_URL, OS_USERNAME, OS_PASSWORD, clip)])

if __name__ == "__main__":
	ListOfFiles = check_output(["ls"]).split('\n')
	del ListOfFiles[-1]
	Move_data_to_local_cloud(ListOfFiles)