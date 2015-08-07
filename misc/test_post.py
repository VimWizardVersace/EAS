import requests
import json

url = 'http://0.0.0.0:5000/config'
filename = '/home/joe/Dropbox/pycharm/EAS/main/config.json'

files = {'file': open(filename, 'rb')}

r = requests.post(url, files=files)
print r.text
