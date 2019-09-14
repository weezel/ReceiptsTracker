import os
#import magic
from flask import Flask, request
from werkzeug.utils import secure_filename

UPLOAD_DIRECTORY = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff'])

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def is_allowed_file(filename):
    return '.' in filename \
            and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['POST'])
def upload_file():
    if request.method != "POST":
        return "Only POST allowed", 405

    if 'file' not in request.files \
              or request.files['file'] is None \
              or request.files['file'].filename == '':
        return "Missing parameter: 'file'\r\n", 422
    received_file = request.files['file']
    if received_file and is_allowed_file(received_file.filename):
        filename = secure_filename(received_file.filename)
        received_file.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filename))
        return "Upload OK\r\n", 200
    else:
        return "Extension type not allowed\r\n", 415

if __name__ == "__main__":
    app.debug = True
    app.run(host='127.0.0.1', port=5555)

