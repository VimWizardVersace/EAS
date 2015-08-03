from converter import Converter
import subprocess
import json
import os


def find_num_frames(pict_type, filename):
    """Find and return the number of frames of a given type
    Valid pict_type's are 'I', 'P', and 'B'.
    """
    command = ('ffprobe -loglevel quiet -show_frames ' + filename + ' | ' +
               'grep pict_type=' + pict_type + ' | wc -l')
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return int(process.stdout.read())


def ingest(path):
    if os.path.isdir(path):
        ingest_directory(path)

    elif os.path.isfile(path):
        ingest_file(path)

    else:
        raise IOError('Location not valid file or folder')


def ingest_directory(directory):
    for filename in os.listdir(directory):
        if not filename.endswith('.py'):
            ingest_file(filename)


def ingest_file(filename):
    info = Converter.probe(filename)
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