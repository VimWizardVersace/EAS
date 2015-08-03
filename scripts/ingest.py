import os


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
