#!/usr/bin/env python3

import datetime
import hashlib
import os
import os.path
import re

from dbutils import DBUtils
from models import Receipt

from flask import Flask, request
from werkzeug.utils import secure_filename

UPLOAD_DIRECTORY = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff'])

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = DBUtils()


def is_allowed_file(filename):
    return '.' in filename \
            and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_tags(request):
    if "tags" not in request.form.keys() or \
            request.form['tags'] == "":
        return "ERROR: Missing parameter: 'tags'\r\n", 422
    return re.sub("\s", " ", request.form['tags'])

def parse_purchase_date(tags):
    purchase_date_pat = re.compile(r"^[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}$")
    dates = list(filter(lambda i: re.search(purchase_date_pat, i), tags.split(" ")))
    if len(dates) > 0:
        dates.sort()
        return datetime.datetime.strptime(dates[0], "%Y-%m-%d")
    now = datetime.datetime.now()
    return datetime.datetime.strptime(now, "%Y-%m-%d")

@app.route('/', methods=['POST'])
def upload_file():
    if request.method != "POST":
        return "ERROR: Only POST allowed", 405

    if 'file' not in request.files \
              or request.files['file'] is None \
              or request.files['file'].filename == '':
        return "ERROR: Missing parameter: 'file'\r\n", 422

    received_file = request.files['file']
    if not received_file or not is_allowed_file(received_file.filename):
        return "Extension type not allowed\r\n", 415

    tags = parse_tags(request)

    # File hash and saving
    filename = secure_filename(received_file.filename)
    filename_hash = hashlib.sha256(received_file.stream.read()).hexdigest()
    ext = os.path.splitext(filename)[-1].strip(".")
    outfile = os.path.join(app.config['UPLOAD_DIRECTORY'], \
        f"{filename_hash}.{ext}")
    if os.path.exists(outfile):
        return "ERROR: File exists\r\n", 409
    received_file.save(outfile)

    # Get text from the receipt with OCR
    # TODO
    parsed_ocr = ""

    # Things related to tags, must be executed after tags parsing
    purchased = parse_purchase_date(tags)

    # Save to DB
    receipt = Receipt(filename=outfile, \
                      purchase_date=purchased, \
                      tags="|".join(tags.split(" ")), \
                      ocr_text=parsed_ocr)
    db.add(receipt)

    return "Upload OK\r\n", 200

if __name__ == "__main__":
    app.debug = True
    app.run(host='127.0.0.1', port=5555)

