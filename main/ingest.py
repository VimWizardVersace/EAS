import subprocess
import json
import os

from converter import Converter

from client_create import create_swift_client


def find_num_frames(frame_type, filename):
    """Find and return the number of frames of a given type
    Valid frame_types are 'I', 'P', and 'B'.
    """
    return 250
    print 'Finding number of', frame_type, 'frames for', filename
    command = ('ffprobe -loglevel quiet -show_frames ' + filename + ' | ' +
               'grep pict_type=' + frame_type + ' | wc -l')
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return int(process.stdout.read())


def ingest(credentials, directory='.'):
    print 'Beginning ingest'
    for filename in os.listdir(directory):
        if filename.endswith('.mp4') or filename.endswith('.mkv'):
            ingest_file(filename, credentials)
    print 'Finished ingesting'


def ingest_file(filename, credentials):
    print 'Ingesting file', filename
    index = generate_index(filename)
    write_index(filename, index)
    swift_move(filename, credentials)


def generate_index(filename):
    print 'Generating index for file', filename
    c = Converter()
    info = c.probe(filename)
    index = dict()

    index['i frames'] = find_num_frames('I', filename)
    index['b frames'] = find_num_frames('B', filename)
    index['p frames'] = find_num_frames('P', filename)
    index['duration'] = info.format.duration
    index['width'] = info.video.video_width
    index['height'] = info.video.video_height
    index['format'] = info.format.format
    index['fps'] = info.video.video_fps
    index['v codec'] = info.video.codec
    index['a codec'] = info.audio.codec

    return index


def swift_move(filename, credentials, container='videos', content_type='video'):
    print 'Moving', filename, 'to swift'
    swift = create_swift_client(credentials)
    swift.put_container(container)
    with open(filename, 'rb') as f:
        swift.put_object(container, filename, contents=f,
                         content_type=content_type)


def read_index(index_filename='index.json'):
    return json.load(open(index_filename))


def write_index(filename, index, index_filename='index.json'):
    print 'Writing index for', filename
    try:
        with open(index_filename, 'r') as index_file:
            total_index = json.load(index_file)
        total_index[filename] = index
        with open(index_filename, 'w+') as index_file:
            json.dump(total_index, index_file, sort_keys=True, indent=4)

    except IOError:
        total_index = dict()
        total_index[filename] = index
        with open(index_filename, 'w+') as index_file:
            json.dump(total_index, index_file, sort_keys=True, indent=4)


if __name__ == '__main__':
    credentials = dict()
    ingest(credentials)
