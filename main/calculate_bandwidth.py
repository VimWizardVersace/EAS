# NOTE:  Pretty much everything in this file is useless except for the iperf_test function

import paramiko
import time
import scp
import os
from subprocess import Popen, PIPE
# five bandwidth measuring tests
# one uses a command line interface of speedtest.net to find the upload/download
#    speed of the vm
#
# one sends packets (pings) from one cloud to another to estimate their upload/download
#    speeds
#
# one sends a file via SCP and times how long it takes to complete the transfer
#
# one sends a file via cURL and times how long it takes to complete the transfer
#
# the final test, and the on we will use in production, is the iperf test.


# ssh into the vm and run a speedtest command
# returns a string in form of MB/s
def speedtest_bandwidth(ssh):
	(stdin, stdout, stderr) = ssh.exec_command(
									"speedtest-cli --simple")

	bandwidth_data = stdout.read().split('\n')
	bandwidth_data = [token.split(": ") for token in bandwidth_data]
	try:
		download_speed = bandwidth_data[1][1]
		upload_speed = bandwidth_data[2][1]
	except IndexError:
		print "uh oh, speedtest-cli isn't installed on the server"

	return download_speed, upload_speed

# ping the vm and do a bunch of arithematic to find the bandwidth in kb/second
# pretty inaccurate
def ping_bandwidth(ssh, target_ip):

	(stdin, stdout, stderr) = ssh.exec_command(
								"echo \"from subprocess import Popen, PIPE, STDOUT\nproc = Popen(['sudo','ping','-f','-c','833', '-s' ,'1464','"+
									target_ip+
									"'],stdin=PIPE, stdout=PIPE, stderr=PIPE)\nproc.stdin.write('pass')\nprint proc.stdout.read()\"> ping.py")

	print "pinging",target_ip,"a bunch of times to find avg send time..."

	(stdin, stdout, stderr) = ssh.exec_command(
								"python ping.py")

	bandwidth_data = stdout.read().split('\n')
	print bandwidth_data[-3]
	avg_time = float(bandwidth_data[-3].split('/')[4])
	
	return (24.0/1024)/(avg_time/1000)

# send a test file of your choosing, and find the average send time
# over that period
#
# if target_ip is specified, it will scp from the ssh to the target_ip
def send_test_file(ssh, video_file, target_ip=None, directory=""):
	# paramiko's scp client allows you to send files to a server
	# 
	if target_ip is None:
		scp_client = scp.SCPClient(ssh.get_transport())
	
		# begin and end allow time keeping to track how long the scp took. 
		begin = time.time()
		scp_client.put(video_file, directory+"ayy_lmao.mp4")
		end = time.time()

		total_time = end - begin
		video_size_MB = float(os.path.getsize(video_file)/1048576)
		return (video_size_MB)/total_time

	else:
		begin = time.time()
		(stdin, stdout, stderr) = ssh.exec_command("scp -P 3022 "+directory+"ayy_lmao.mp4"+" "+"user2@"+target_ip+":~"+directory+"ayy_lmao.mp4")
		end = time.time()
		print stdout.read()
		total_time = end - begin
		video_size_MB = float(os.path.getsize(video_file)/1048576)
		return (video_size_MB)/total_time


def swift_test(public_url, sample_file, auth_token, file_size):
	begin = time.time()
	(stdin, stdout, stderr) = ssh.exec_command(
		"curl -i"
		+public_url
		+sample_file
		+" -X PUT -H \"Content-Length: 1\" -H \"Content-Type: video/mp4; charset=UTF-8\" -H \"X-Auth-Token: "
		+auth_token+"\""
		)

		
	total_time = begin - time.time()

	return file_size/float(total_time)

# the simplest one is the most effective
def iperf_test(url):
	# automatically connects to port 5001 for testing,
	# so be sure to have both iperf and port 5001 running on the other computer
	(stdout, stderr) = Popen(['iperf','-c',url,'-f', 'M'],
						stdout=PIPE).communicate()

	# parsing stdout for upload speed in Mbytes
	test_transfer_results = stdout.strip().split('\n')[-1]
	upload_speed = test_transfer_results.split('MBytes')[1].strip()
	return upload_speed


# main is used for testing
#
if __name__ == "__main__":
	#client = paramiko.SSHClient()
	#client.load_system_host_keys()
	#client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	#URL = ["10.131.77.199", 3024, "user", "pass"]
	#try:
	#	client.connect(URL[0], URL[1], username=URL[2], password=URL[3])
	#except:
#		print "invalid url"

	print "TEST 1: SPEEDTEST-CLI"
	#(dl, ul) = speedtest_bandwidth(client) 
	#print dl, ul

	print
	print "TEST 2: PING"
	#bandwidth = ping_bandwidth(client, "google.com")
	#print "%.2f Mbits/s" %bandwidth

	print 
	print "TEST 3: SEND TEST FILE"
	#print "%2.f Mbits/s" %send_test_file(client, "0.mp4", target_ip="10.131.77.199", directory="Videos/")
	
	print
	print "TEST 4: SWIFT-API"

	print
	print "TEST 5: IPERF"
	url = "10.131.69.121"
	bandwidth = iperf_test(url)
	print bandwidth, "Mbytes/sec"

