from flask import Flask, request
from threading import Thread
from converter import ffmpeg
import json
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '~/tmp'


@app.route("/config", methods=['POST'])
def config():
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'file_list'))
    Thread(target=process)
    return ''


def read_config(config_file='config.json'):
    with open(config_file) as json_config:
        return json.load(json_config)


def grab_file(filename):
    """ Download file from swift """
    pass


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

    for c in c_gen:
        pass
    return t


def process():
    file_list = open('file_list', 'r+')
    config = read_config()
    for filename in file_list:
        grab_file(filename)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)