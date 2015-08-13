import os

from converter import Converter


def find_matching_files(search_type, search_directory):
    """ Loop through all files in the search directory, find all the
    ones that match a given type, and return them in a list
    """
    to_convert = []
    to_check = os.listdir(search_directory)

    for f in to_check:
        attributes = f.split('.')
        if (len(attributes) >= 2 and
                    attributes[-1] == search_type):
            to_convert.append(f)

    return to_convert


def transcode(files, config, init_directory, final_directory):
    """ Transcode a list of given files """
    for name in files:
        attributes = name.split('.')
        form_type = config['format']
        new_name = attributes[0] + '.' + form_type

        initial = init_directory + name
        final = final_directory + new_name

        print 'Transcoding', name
        transcode_file(config, initial, final)
        print ''


def transcode_file(config, initial, final):
    """ Transcodes individual file """
    c = Converter()
    c_generator = c.convert(initial, final, config)

    percents = []
    p = 0
    for t in c_generator:
        if p not in percents and t > p:
            percents.append(p)
            p += 10
            print str(p) + '% done'


if __name__ == '__main__':
    file_type = 'mkv'

    init_directory = 'to_convert/'
    final_directory = 'converted/'

    # Dictionary of options which are passed onto FFmpeg
    config = {
        'format': 'mkv',
        'audio': {
            'codec': 'mp3'
        },
        'video': {
            'codec': 'h264',
            'width': 720,
            'height': 400,
            'fps': 24
        }
    }

    files = find_matching_files(file_type, init_directory)
    transcode(files, config, init_directory, final_directory)
