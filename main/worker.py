from client_create import create_swift_client
from flask import *
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
log = open('log.txt', 'r+')


@app.route('/')
def index():
    return redirect(url_for('jobs'))


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    global log
    if request.method == 'POST':
        log.write('Accessed POST method on /jobs')
        swift_files = '~/swift_list'
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], swift_files))
        log.write('Finished saving files on POST method on /jobs')
        fill_grabQ(swift_files)
        Thread(target=grab_thread)
        Thread(target=convert_thread)
        Thread(target=place_thread)
        log.write('Finished spawning threads on POST method on /jobs')
        return ''
    else:
        log.write('Accessed GET method on /jobs')
        return print_all_queues()


@app.route('/jobs/status')
def completed():
    global log
    log.write('Accessed /jobs/status')
    return str(grabQ.empty() and convertQ.empty() and placeQ.empty())


def grab_thread():
    global grabQ, convertQ, log

    log.write('GRAB THREAD: loading credentials')
    credentials = json.load(open('transburst.conf'))

    log.write('GRAB THREAD: spawning swift client')
    sw_client = create_swift_client(credentials)

    while True:
        log.write('GRAB THREAD: listening in grab queue')
        filename = grabQ.get()

        log.write('GRAB THREAD: grabbing ' + filename + ' from swift')
        grab(sw_client, filename)

        log.write('GRAB THREAD: putting ' + filename + ' in convert queue')
        convertQ.put(filename)


def convert_thread():
    global convertQ, placeQ, log

    while True:
        log.write('CONVERT THREAD: listening on convert queue')
        filename = convertQ.get()

        log.write('CONVERT THREAD: converting ' + filename)
        new_name = convert(filename)

        log.write('CONVERT THREAD: putting' + filename + ' in place queue')
        placeQ.put(new_name)


def place_thread():
    global placeQ, log

    log.write('PLACE THREAD: loading credentials')
    credentials = json.load(open('transburst.conf'))

    log.write('PLACE THREAD: spawning swift client')
    sw_client = create_swift_client(credentials)

    while True:
        log.write('PLACE THREAD: listening on place queue')
        filename = placeQ.get()

        log.write('PLACE THREAD: placing ' + filename + ' back in swift')
        place(sw_client, filename)


def fill_grabQ(swift_urls):
    global grabQ, log

    log.write('Filling grab queue')
    with open(swift_urls, 'r+') as swift_url_list:
        for line in swift_url_list.readlines():
            log.write('Adding ' + line.strip() + ' to grab queue')
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