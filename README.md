As of right now, input is taken via transburst.conf.

It grabs video files from a container called "videos" on the object storage associated with your keystone credentials, sends them to a remote cloud with a set of remote credentials (which are currently fixed), and transfer them back into a new container called "completed".

REQUIREMENTS:

At least 11GB of storage available in your local cloud object storage for image storage
Python 2.7, and the following modules:
  Flask
  sklearn
  python-video-converter
  numpy
  youtube-dl
  python-swiftclient
  python-novaclient
  python-keystoneclient
  python-glancelclient
