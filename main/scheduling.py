import time
import operator
import paramiko
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

def partition_workload(time_until_deadline, bitrate, swiftclient, container_name):
	# use curl to connect to the object storage
	# to discover the sizes of the videos to xcode
	# 
	# note: authtoken may randomly change???

	container_data = []
	for data in swiftclient.get_container(container_name)[1]:
		container_data.append('{0}\t{1}'.format(data['name'], data['bytes']))
	container_data = [token.split('\t') for token in container_data]
	print container_data

	# use a dictionary comprehension to assemble a size: filename map
	#
	file_size_dict = dict()
	try:
		file_size_dict = {token[0] : (int(token[1])/1024) for token in container_data}
	except IndexError:
		print "error (IndexError):  tried to ls on the local cloud to get file sizes.  things are formatted weird."

	# create some important time variables and counters
	#
	total_possible_xcodable_content = time_until_deadline*bitrate
	total_xcodable = 0
	
	# where we store the videos in either local or external
	#
	video_names_local = []
	video_names_outsourced = []

	# given the bitrate, find how much xcoding is possible on local machine
	#
	for video in file_size_dict:
		if (total_xcodable + file_size_dict[video] < total_possible_xcodable_content):
			video_names_local.append(video)
			total_xcodable += file_size_dict[video]
		else:
			video_names_outsourced.append(video)

	return (video_names_local, video_names_outsourced)

#main is used for testing
#
if __name__ == "__main__":
	# This file takes in urls in the form of a list
	# URL[0] = IP of VM
	# URL[1] = port #
	# URL[2] = username for VM
	# URL[3] = password for VM
	# This is neccesary to ssh into it and find their file sizes

	test_url = "http://10.131.69.121:8080/v1/AUTH_1eacdf40e54e4d72b1b1096e82d3bbe3/videos"
	test_auth = "255d997d9321454fa3e2d454dc641cb1"
	test_deadline = '07/15/2015 16:10:09'
	test_bitrate = 1024 * 0
	partition_workload(test_deadline, test_bitrate, test_url, test_auth)
	#stdout = check_output(["curl", test_url+"?format=json", "-X", "GET", "-H" , "X-Auth-Token:"+test_auth])
	#print stdout




