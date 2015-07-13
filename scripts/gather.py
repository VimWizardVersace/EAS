from __future__ import unicode_literals
from converter import Converter, ffmpeg
import youtube_dl
import subprocess
import random
import glob
import time
import csv
import os


#######################################################################
def get_data(file_name):
    """ Read data from file and return it in a list """
    data_file = open(file_name)

    data = []
    for line in data_file.readlines():
        data.append(line)
    return data
#######################################################################


#######################################################################
def random_config(options):
    """ From a list of possible options, create and return a dictionary
    which is a random configuration for ffmpeg
    """
    codec = random.choice(options[0]).rstrip()
    fps = random.choice(options[1]).rstrip()
    bitrate = random.choice(options[2]).rstrip()
    size = random.choice(options[3]).rstrip()

    width = int(size.split('x')[0])
    height = int(size.split('x')[1])

    config = {
        'format': 'm3u8',
        'audio': {'codec': 'libvo_aacenc'},
        'video': {
            'codec': 'h264',
            'size': size,
            'fps': fps,
            'bitrate': bitrate
        }
    }
    return config
#######################################################################


#######################################################################
def get_random_video(url_list):
    """ Continuously tries to download a youtube video from a list of
    random possible videos until one is finally found, then this is
    renamed to 'video.mp4'
    """
    ydl_opts = {}
    ydl = youtube_dl.YoutubeDL(ydl_opts)

    while True:
        try:
            ydl.download([url])
            files = os.listdir('.')
            for f in files:
                if f.endswith('.mkv'):
                    os.remove(f)
                    raise TypeError
                if f.endswith('.mp4'):
                    os.rename(f, 'video.mp4')
                    return
        except:
            url = random.choice(url_list)
#######################################################################


#######################################################################
def find_num_frames(pict_type):
    """Find and return the number of frames of a given type
    Valid pict_type's are 'I', 'P', and 'B'.
    """
    command = ('ffprobe -loglevel quiet -show_frames video.mp4 | ' +
               'grep pict_type=' + pict_type + ' | wc -l')
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return int(process.stdout.read())
#######################################################################


#######################################################################
def convert(file_name, config):
    """ Using python-vide-converter as an ffmpeg wrapper, convert a
        given file to match the given config.
    """

    # Create the new name based off the new format (found in the config
    # dictionary)
    name_parts = file_name.split('.')
    form_type = config['format']
    new_name = name_parts[0] + '.' + form_type

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
    c_gen = ffmpeg.FFMpeg().convert(file_name, new_name, new_config)

    print 'Beginning transcode'

    # Transcodes the file, keeping track of how many seconds it takes
    t0 = time.time()
    for c in c_gen:
        pass
    t = time.time() - t0
    print 'Finished transcode in', t, 'seconds'
    return t
#######################################################################


# BEGIN MAIN #
#######################################################################
# Create the default name used throughout the program structure. Done
# to avoid issues with modules not conforming to unicode, which many
# youtubes use
default_name = 'video'
default_type = 'mp4'
file_name = default_name + '.' + default_type

# Read in the predefined data from the text files
urls = get_data('url_list.txt')
fpss = get_data('fps_list.txt')
sizes = get_data('size_list.txt')
codecs = get_data('codec_list.txt')
bitrates = get_data('bitrate_list.txt')

options = [codecs, fpss, bitrates, sizes]

# Create CSV file for data and write data types to top of file
conversion_data = open('conversions.csv', 'w+', 0)
writer = csv.writer(conversion_data, delimiter=str(','),
                    quoting=csv.QUOTE_MINIMAL)
first_line = ['Input Container Format', 'Video Duration', 'Input FPS',
              'Input Video Codec', 'Input Resolution', 'Input Audio Codec',
              'Input # i-frames', 'Input # b-frames', 'Input # p-frames',
              'Output Container Format', 'Output FPS', 'Output Video Codec',
              'Output Resolution', 'Output Audio Codec', 'Transcode Time']
writer.writerow(first_line)

# Infinitely loop to continuously generate data until stopped manually
c = Converter()
while True:
    config = random_config(options)
    get_random_video(urls)
    elapsed_time = convert(file_name, config)

    files = os.listdir('.')
    for f in files:
        # Different information is needed for the mp4 and m3u8 files
        # so they are handled separately
        if f.endswith('.mp4'):
            i_frames = find_num_frames('I')
            b_frames = find_num_frames('B')
            p_frames = find_num_frames('P')
            info = c.probe(f)
            size = (str(info.video.video_width) + 'x' +
                    str(info.video.video_height))
            original = [info.format.format, info.format.duration,
                        info.video.video_fps, info.video.codec, size,
                        info.audio.codec, i_frames, b_frames, p_frames]

        if f.endswith('.m3u8'):
            info = c.probe(f)
            size = (str(info.video.video_width) + 'x' +
                    str(info.video.video_height))
            output = [info.format.format, info.video.video_fps,
                      info.video.codec, size, info.audio.codec]

    # Cleanup video files to save disk space
    for f in files:
        if f.endswith('.mp4') or f.endswith('.ts') or f.endswith('.m3u8'):
            os.remove(f)

    writer.writerow(original + output + [elapsed_time])
#######################################################################
