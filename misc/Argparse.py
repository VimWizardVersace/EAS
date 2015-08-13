# movetocloud.py
#
import argparse
parser = argparse.ArgumentParser(description='Moves a specific number of files to the cloud')
#
# Add arguments
parser.add_argument('--filenames', dest='filenames',metavar='filenames', nargs='*', help='files to be moved to the cloud')
parser.add_argument('--cloud', dest='cloud', metavar='cloud', help='cloud name')
#
# Parse the args
args = parser.parse_args()

# filenames contains an array of the files input after --filenames

# set myArray to filenames
myArray = args.filenames

# set destcloud to cloud
destcloud = args.cloud
print 'cloud destination'
print destcloud

# Go through each element in the filenames array
for i in range(len(myArray)):
  # for each element in the array myArray[i],

  # print each argument
  print myArray[i]

  # add code here to move to the cloud -- assuming that function can be called from python and takes ONE at a time
  # by referencing myArray[i] and cloud

# add code here to move all videos to the cloud in a single call
# by referencing myArray and cloud

# Partition List

# Create VMs

# Transfer video

# Contact VMs

# Start Transcode

# Transfer back