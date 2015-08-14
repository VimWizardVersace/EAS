from threading import Thread
from Queue import Queue
import datetime
import tarfile
import time
import os
from flask import *
from converter import ffmpeg
from client_create import create_swift_client

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/interns/eas/main'

grabQ = Queue()
convertQ = Queue()
placeQ = Queue()
num_total = 0
num_processed = 0


@app.route('/')
def index():
    return redirect(url_for('jobs'))


@app.route('/boot', methods=['GET'])
def booted():
    return 'True'


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'POST':
        print'Accessed POST method on /jobs'
        swift_files = 'swift_list'
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], swift_files))
        print 'Finished saving workload'
        fill_grabQ(swift_files)

        print 'Spawning grab thread'
        Thread(target=grab_thread).start()

        print 'Spawning convert thread'
        Thread(target=convert_thread).start()

        print 'Spawning place thread'
        Thread(target=place_thread).start()
        return ''
    else:
        print 'Accessed GET method on /jobs'
        return print_all_queues()


@app.route('/jobs/status')
def completed():
    global num_processed, num_total
    print 'Accessed /jobs/status'
    print 'Jobs remaining: ' + str(num_total - num_processed)
    return str(num_processed == num_total)


def return_time():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')


def grab_thread():
    global grabQ, convertQ

    print 'GRAB THREAD: Loading credentials'
    credentials = json.load(open('transburst.json'))

    print 'GRAB THREAD: Spawning swift client'
    sw_client = create_swift_client(credentials)

    while True:
        print 'GRAB THREAD: Listening in grab queue...'
        filename = grabQ.get()

        print 'GRAB THREAD: Grabbing ' + filename + ' from swift'
        grab(sw_client, filename)

        print 'GRAB THREAD: Putting ' + filename + ' in convert queue'
        convertQ.put(filename)


def convert_thread():
    global convertQ, placeQ

    while True:
        print 'CONVERT THREAD: Listening on convert queue'
        filename = convertQ.get()

        print 'CONVERT THREAD: Converting ' + filename
        new_name = convert(filename)

        print 'CONVERT THREAD: Putting ' + new_name + ' in place queue'
        placeQ.put(new_name)


def place_thread():
    global placeQ, num_processed, num_total

    print 'PLACE THREAD: Loading credentials'
    credentials = json.load(open('transburst.json'))

    print 'PLACE THREAD: Spawning swift client'
    sw_client = create_swift_client(credentials)

    while True:
        print 'PLACE THREAD: Listening on place queue'
        filename = placeQ.get()

        print 'PLACE THREAD: Placing ' + filename + ' back in swift'
        place(sw_client, filename)
        num_processed += 1


def fill_grabQ(swift_urls):
    global grabQ, num_total

    print 'Filling grab queue...'
    with open(swift_urls, 'r+') as swift_url_list:
        for line in swift_url_list.readlines():
            print 'Adding ' + line.strip() + ' to grab queue'
            grabQ.put(line.strip())
    num_total = grabQ.qsize()


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
    vid_tuple = sw_client.get_object('videos', filename)

    # finally, write a file to the local directory with the same name as the
    # file we are retrieving
    with open(filename, 'wb') as new_vid:
        new_vid.write(vid_tuple[1])


def place(sw_client, filename, container='completed', content_type='video'):
    sw_client.put_container(container)
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

    f = ffmpeg.FFMpeg()

    # Creates the generator used to convert the file
    c_gen = f.convert(filename, new_name, new_config, timeout=0)

    for c in c_gen:
        pass

    os.remove(filename)
    return tar(base)


def tar(base):
    print 'Writing tar archive as ' + base + '.tar'
    archive = tarfile.open(base + '.tar', 'w')
    for filename in os.listdir('.'):
        if base in filename:
            print 'Adding ' + filename + ' to ' + base + '.tar'
            archive.add(filename)
    archive.close()
    return base + '.tar'


def print_all_queues():
    global grabQ, convertQ, placeQ
    grab_list = list(grabQ.queue)
    convert_list = list(convertQ.queue)
    place_list = list(placeQ.queue)

    return str(grab_list) + str(convert_list) + str(place_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
