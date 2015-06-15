import time
import operator
import paramiko

def find_time_until_deadline(deadline):
	#WARNING:  Time must be formatted the same as pattern
	#
	try:
		pattern = "%m/%d/%Y %H:%M:%S"
		epoch = int(time.mktime(time.strptime(deadline, pattern)))	
	except (ValueError):
		print "bruh give us a deadline in the form of MM/DD/YYYY HH:MM:SS"
	return epoch - time.time()

def PartitionURLlist(deadline, bitrate, URL):
	# spawn an ssh client to connect to local cloud
	# to discover the sizes of the videos to xcode
	#	
	client = paramiko.SSHClient()
	client.load_system_host_keys()
	try:
		client.connect(URL[0], URL[1], URL[2], URL[3])
	except:
		print "invalid url"
	print "connection to local cloud successful"

	# travel to the appropriate directory and store file names + info
	# 
	(stdin, stdout, stderr) = client.exec_command('du -a ~/Videos')
	filenames = stdout.read().split('\n')
	filenames = [token.split('\t') for token in filenames]
	client.close()	
	
	# delete the "total" footer and strip empty list
	#
	del filenames[-1]
	del filenames[-1]

	# use a dictionary comprehension to assemble a size: filename map
	#
	try:
		file_size_dict = {token[1]: int(token[0]) for token in filenames}
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

	test_url = ['10.131.77.64', 3022, 'user', 'pass']
	test_deadline = '06/15/2015 16:10:09'
	test_bitrate = 1024 * 0.5
	PartitionURLlist(test_deadline, test_bitrate, test_url)
