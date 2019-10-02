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

def parse_purchase_date(request):
    # Parse purchase_date
    if "pur_date" in request.form.keys():
        purchase_date = request.form['pur_date']
    elif "purchase_date" in request.form.keys():
        purchase_date = request.form['purchase_date']
    else:
        purchase_date = datetime.datetime.now()

    if not isinstance(purchase_date, type(datetime.datetime.now())):
        purchase_date = purchase_date.replace(".", "-")
        return datetime.datetime.strptime(purchase_date, "%Y-%m-%d")
        #year, month, day = purchase_date.split("-")
        #purchase_date = datetime.datetime.strftime(f"{year}.{month}.{day}", "%Y-%m-%d", )

def parse_tags(request):
    if "tags" not in request.form.keys() or \
            request.form['tags'] == "":
        return "ERROR: Missing parameter: 'tags'\r\n", 422
    return re.sub("\s", " ", request.form['tags'])

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

    purchased = parse_purchase_date(request)

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

