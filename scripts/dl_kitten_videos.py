# download every video about kittens on youtube
# also find the highest quality of video and audio seperately and merges them
# be sure to have beautifulsoup and ffmpeg installed or the script will h8 u
#
#
# main is at line 69
# -ruru

import os
import sys
import time
import urllib2
import re
from subprocess import Popen, PIPE, call
# they named their constructor after the module smh
from BeautifulSoup import BeautifulSoup

def SearchVideosByKeywords(search_term, isUrl):
	# check if "search_term" is a search_term or a url
	#	
	url = ""
	if isUrl:
		url = search_term
	else:
		url = "https://www.youtube.com/results?search_query="+search_term

	# take the site and load it as a beautiful soup object for crawling.
	#
	website = urllib2.urlopen(url)
	soup = BeautifulSoup(website.read())
	links = soup.findAll('a')

	# collect all urls that lead to videos.
	# note all youtube videos are delimited by:
	# "/watch?v="
	#
	list_of_urls = []
	for url in links:
		soupstring = str(url)
		if "/watch?v=" in soupstring:
			index = soupstring.index("/watch?v=")
			if ('https://www.youtube.com/watch?v='+(soupstring[index+9:index+20]) not in list_of_urls):
				list_of_urls.append('https://www.youtube.com/watch?v='+(soupstring[index+9:index+20]))
	return list_of_urls

def findbestquality(stdout):
	stdout = stdout.split('\n')
	stdout = stdout[5:-1]

	formatcodeVid = ''
	formatcodeAud = ''

	# quality versions are identified by format codes
	# best audio and videos are split
	# this is used to combine the best audio and video files
	#
	for line in stdout:
		if 'DASH audio' in line:
			line = line.split(' ')
			formatcodeAud = line[0]

		if 'DASH video' in line:
			line = line.split(' ')
			formatcodeVid = line[0]
	
	return (formatcodeVid, formatcodeAud)


if __name__ == "__main__":

	# let's start our crawl by looking for videos of kittens
	#	
	list_of_urls = SearchVideosByKeywords("kittens", False)

	# some comprehensive variables to keep you updated
	#
	numvids = 0
	totalbytes = 0
	
	for url in list_of_urls:
		# iteratively come up with new file names.
		# 0.mp4, 1.mp4, 2.mp4...
		#
		dest = str(numvids)+'.mp4'
		
		# assemble the two bashcalls
		# the first bashcall is a subprocess used to identify the highest
		# quality of video and audio available. the second bashcall is
		# to download and merge the audio and video files.
		#
		(stdout, stderr) = Popen(['youtube-dl','-F',url],
							 stdout=PIPE).communicate()

		# find the best audio and video files.
		#
		(formatCodeVid, formatCodeAud) = findbestquality(stdout)

		# download and merge the audio and video files
		# shell needs to be true to download files and rename files
		#
		call(['youtube-dl '+'-f '+formatCodeVid+'+'
						+formatCodeAud+' '+url
						+' -o '+dest], shell=True)

		# iterate numvids and total memory stored thus far
		# for record keeping
		#
		numvids += 1
		if (os.path.isfile(dest)):
			totalbytes += float(os.path.getsize(dest))
		elif (os.path.isfile(dest.split('.')[0]+'.mkv')):
			totalbytes += float(os.path.getsize(dest.split('.')[0]+'.mkv'))
		else:
			print "Can't find your file, not counting it lol"
		
		print 
		print "TOTAL MB downloaded: %.2f MB" %(totalbytes/1048576.0)
		print "TOTAL # of vids downloaded: ",numvids 
		print

		# check if the current url is the last url in the list
		# if so, generate a new list of videos from the related section
		#
		if numvids is len(list_of_urls)-1:
			list_of_urls.extend(SearchVideosByKeywords(url,True))

