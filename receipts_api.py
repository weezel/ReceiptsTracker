#!/usr/bin/env python3

import datetime
import hashlib
from itertools import dropwhile
import os
import os.path
import re

from dateutil.relativedelta import relativedelta
from flask import Flask, request
from werkzeug.utils import secure_filename

from dbutils import DBUtils
from models import Receipt, Tag


UPLOAD_DIRECTORY = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff'])

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = DBUtils()


def is_allowed_file(filename):
    return '.' in filename \
            and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_tags(tags):
    normalized = re.sub("\s", " ", tags)
    splitted = normalized.split(" ")
    dups_removed = list(set(splitted))
    dups_removed.sort()
    return dups_removed

def parse_purchase_date(tags):
    purchase_date_pat = re.compile(r"^[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}$")
    dates = list(filter(lambda i: re.search(purchase_date_pat, i), tags))

    # Remove purchase date(s) from tags
    [tags.remove(d) for d in dates if d in tags]

    if len(dates) > 0:
        dates.sort()
        return datetime.datetime.strptime(dates[0], "%Y-%m-%d")
    now = datetime.datetime.now()
    return datetime.datetime.strptime(now, "%Y-%m-%d")

def parse_expiry_date(start_date, tags):
    """
    Parse expiry date from tags starting from start_date.
    """
    exp_pat = re.compile(r"^[0-9]+_(day|month|year)s?$")
    exp = list(filter(lambda i: re.search(exp_pat, i), tags))

    # Remove expiration date(s) from tags
    [tags.remove(e) for e in exp if e in tags]

    if len(exp) > 0:
        exp.sort()
        expiration = exp[0]

        number_val = int(re.search(r"^[0-9]+", expiration).group())

        if re.search("days?$", expiration):
            return start_date  + relativedelta(days=number_val)
        elif re.search("months?$", expiration):
            return start_date  + relativedelta(months=number_val)
        elif re.search("years?$", expiration):
            return start_date  + relativedelta(years=number_val)
    return None

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

    if "tags" not in request.form.keys() or \
            request.form['tags'] == "":
        return "ERROR: Missing parameter: 'tags'\r\n", 422
    tags = parse_tags(request.form['tags'])

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
    purchase_date = parse_purchase_date(tags)
    expiry_date = parse_expiry_date(purchase_date, tags)

    # Save to DB
    receipt = Receipt(filename=outfile, \
                      purchase_date=purchase_date, \
                      expiry_date=expiry_date, \
                      ocr_text=parsed_ocr)
    tag_rows = [Tag(tag=i) for i in tags]
    db.add(receipt, tag_rows)

    return "Upload OK\r\n", 200

if __name__ == "__main__":
    app.debug = True
    app.run(host='127.0.0.1', port=5555)

