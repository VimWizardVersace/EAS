import time
import operator
import paramiko
from subprocess import call, PIPE, Popen, check_output

def find_time_until_deadline(deadline):
	#WARNING:  Time must be formatted the same as pattern
	#
	try:
		pattern = "%m/%d/%Y %H:%M:%S"
		epoch = int(time.mktime(time.strptime(deadline, pattern)))	
	except (ValueError):
		print "bruh give us a deadline in the form of MM/DD/YYYY HH:MM:SS"
	return epoch - time.time()

def partition_workload(deadline, bitrate, URL, AUTH):
	# use curl to connect to the object storage
	# to discover the sizes of the videos to xcode
	# 
	# note: authtoken may randomly change???

	stdout = check_output(["curl", URL+"?format=json", "-X", "GET", "-H" , "X-Auth-Token:"+AUTH])
	json_objs = stdout.split('{')
	json_objs = [token.split(' ') for token in json_objs]

	# get rid of garbage
	#
	del json_objs[0]
	
	# use a dictionary comprehension to assemble a size: filename map
	#
	file_size_dict = dict()
	try:
		file_size_dict = {token[7] : int(token[5].strip(",")) for token in json_objs}
	except IndexError:
		print "error (IndexError):  tried to ls on the local cloud to get file sizes.  things are formatted weird."

	# create some important time variables and counters
	#
	time_until_deadline = find_time_until_deadline(deadline)
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




