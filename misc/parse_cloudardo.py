from BeautifulSoup import BeautifulSoup
import urllib2
from time import sleep

# this is a one-time-use script used to find the base price of up to 400 different clouds catalogged by
# http://cloud-computing.softwareinsider.com/ 
#
# only rerun this script if you anticipate cloud prices changing 
#
# get_all_cloud_hourly_rates is the bulk of the work.  softwareinsider.com is kind enough to index their clouds in
# their url in order, so it loops through http://cloud-computing.softwareinsider.com/l/1, 
# http://cloud-computing.softwareinsider.com/l/2 ... http://cloud-computing.softwareinsider.com/l/400 getting every single
# cloud's price plan.  
#
# parse_page_for_hourly_rate is the function that actually parses each individual page
#
#


#this function is misc and was used mostly for testing
def get_cloud_hourly_rates(URL, bot_hdr):
	req = urllib2.Request(URL, headers=bot_hdr)

	try:
		website = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
    		print e.fp.read()

	soup = BeautifulSoup(website.read())
	cloud_price_dict = dict()
	raw_txt = soup.getText().split(",")
	last_found_cloud = ""
	flag = False
	for index, word in enumerate(raw_txt):
		if "[\"\"]" in word:
			last_found_cloud =  raw_txt[index-4]
			flag = True
		if "per hour" in word and flag:
			cost_index = word.index("per hour") - 6
			cloud_price_dict[last_found_cloud.encode("ascii")] = word[cost_index:cost_index+5].encode("ascii")
			flag = False

	for key in cloud_price_dict:
		print key, cloud_price_dict[key] 

def get_one_cloud_hourly_rate(bot_hdr, website):
	soup = BeautifulSoup(website.read())

	# using beautiful soup to extract the raw text from the web page, see if the cloud we're looking at is 
	# IaaS.  if not, exit.  else, do parsing voodoo to extract the base plan price and the name of the cloud
	#
	raw_txt = soup.getText()
	if raw_txt.find("Infrastructure as a Service") == -1 or raw_txt.find("Plan Price") == -1:
		return -1, -1
	cloud_name = website.geturl().split("/")[-1]
	cloud_hourly_rate = raw_txt.split("Plan Price")[1].split(" ")[0]
	cloud_hourly_rate = float(cloud_hourly_rate.encode("ascii").strip("$"))
	return cloud_name, cloud_hourly_rate

def get_all_cloud_hourly_rates(bot_hdr):
	cloud_price_dict = dict()
	for i in range(337, 400):
		print "http://cloud-computing.softwareinsider.com/l/"+str(i)
		req = urllib2.Request("http://cloud-computing.softwareinsider.com/l/"+str(i), headers=bot_hdr)
		try:
			website = urllib2.urlopen(req)
		except:
			# 404/no cloud stored in this page
			sleep(40)
			continue
		
		(name, rate) = get_one_cloud_hourly_rate(bot_hdr, website)
		# check if IaaS
		if name == -1:
			sleep(40)
			continue
	
		print (name, rate)
		sleep(30)

if __name__ == "__main__":
	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}
	cloud_dict = get_all_cloud_hourly_rates(bot_hdr=hdr)


