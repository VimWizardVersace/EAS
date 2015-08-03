import subprocess
import os


def find_num_frames(pict_type):
    """Find and return the number of frames of a given type
    Valid pict_type's are 'I', 'P', and 'B'.
    """
    command = ('ffprobe -loglevel quiet -show_frames video.mp4 | ' +
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
