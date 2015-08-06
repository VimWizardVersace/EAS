from flask import Flask, request
from threading import Thread
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '~/tmp'


@app.route("/config", methods=['POST'])
def config():
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'file_list'))
    Thread(target=process)
    return ''

def grab_file(filename):
    """ Download file from swift """
    pass





def process():
    file_list = open('file_list', 'r+')
    for filename in file_list:
        grab_file(filename)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)