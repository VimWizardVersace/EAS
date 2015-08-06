from flask import Flask, request
import os


def init():
    global app
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = '/home/joe/tmp/'
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route("/config", methods=['POST'])
def config():
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    return ''

init()