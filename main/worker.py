from transburst_utils import parse_config_file
from client_create import create_swift_client
from flask import Flask, request
from threading import Thread
from converter import ffmpeg
from Queue import Queue
import tarfile
import json
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '~/tmp'

grabQ = Queue()
convertQ = Queue()
placeQ = Queue()


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'POST':
        swift_files = '~/swift_list'
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], swift_files))

        fill_grabQ(swift_files)
        Thread(target=grab_thread)
        Thread(target=convert_thread)
        Thread(target=place_thread)
        return ''
    else:
        return print_all_queues()


@app.route('/jobs/status')
def completed():
    return str(grabQ.empty() and convertQ.empty() and placeQ.empty())


def grab_thread():
    global grabQ, convertQ

    credentials = parse_config_file('transburst.conf')
    sw_client = create_swift_client(credentials)

    while True:
        filename = grabQ.get()
        grab(sw_client, filename)
        convertQ.put(filename)


def convert_thread():
    global convertQ, placeQ

    while True:
        filename = convertQ.get()
        new_name = convert(filename)
        placeQ.put(new_name)


def place_thread():
    global placeQ

    credentials = parse_config_file('transburst.conf')
    sw_client = create_swift_client(credentials)

    while True:
        filename = placeQ.get()
        place(sw_client, filename)


def fill_grabQ(swift_urls):
    global grabQ
    with open(swift_urls, 'r+') as swift_url_list:
        for line in swift_url_list.readlines():
            grabQ.put(line.strip())


def read_config(config_file='config.json'):
    with open(config_file) as json_config:
        return json.load(json_config)


def grab(sw_client, filename):
    """
    In order to interact with swift storage, we need credentials
    # and we need to create an actual client with the swiftclient API
    # this assumes several things:
    # 1) the remote credentials have been posted to the worker VM
    # 2) client_create.py and transburst_utils.py are in the current directory
    """

    # reminder: sw_client.get_object returns a tuple in the form of:
    # (filename, file content)
    vid_tuple = sw_client.get_object("Videos", filename)

    # finally, write a file to the local directory with the same name as the
    # file we are retrieving
    with open(filename, 'wb') as new_vid:
        new_vid.write(vid_tuple[1])


def place(sw_client, filename, container='completed', content_type='video'):
    with open(filename, 'rb') as f:
        sw_client.put_object(container, filename, contents=f,
                             content_type=content_type)
    os.remove(filename)


def convert(filename, config=None):
    """
    Using python-vide-converter as an ffmpeg wrapper, convert a
    given file to match the given config.
    """

    if not config:
        config = read_config()

    # Create the new name based off the new format (found in the config
    # dictionary)
    name_parts = filename.split('.')
    base = name_parts[0]
    form_type = config['format']
    new_name = base + '.' + form_type

    # Although a dictionary is easiest to work with for entering
    # options from a human-readable point of view, the low-level ffmpeg
    # wrapper takes in a list of manual ffmpeg options. Those are
    # established here
    new_config = ['-codec:a', config['audio']['codec'],
                  '-codec:v', config['video']['codec']]

    if 'fps' in config['video']:
        new_config += ['-r', config['video']['fps']]
    if 'bitrate' in config['video']:
        new_config += ['-b:v', config['video']['bitrate']]
    if 'size' in config['video']:
        new_config += ['-s', config['video']['size']]

    # Creates the generator used to convert the file
    c_gen = ffmpeg.FFMpeg().convert(filename, new_name, new_config)

    for c in c_gen:
        pass

    os.remove(filename)
    return tar(base)


def tar(base):
    archive = tarfile.open(base + '.tar', 'w')
    for filename in os.listdir('.'):
        if base in filename:
            archive.add(filename)
            os.remove(filename)
    return base + '.tar'


def print_all_queues():
    global grabQ, convertQ, placeQ
    grab_list = list(grabQ.queue)
    convert_list = list(convertQ.queue)
    place_list = list(placeQ.queue)

    return str(grab_list) + str(convert_list) + str(place_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)