#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import logging
import os
import os.path
import re

from dateutil.relativedelta import relativedelta
from flask import Flask, request
from werkzeug.utils import secure_filename

import db.dbengine as dbengine

UPLOAD_DIRECTORY = "uploads"
ALLOWED_EXTENSIONS = set(['gif', 'jpg', 'jpeg', 'png', 'tiff'])

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

dbeng = dbengine.DbEngine(logging)


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
    return datetime.datetime.now().strftime("%Y-%m-%d")

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
    file_binary = received_file.stream.read()
    filename_hash = hashlib.sha256(file_binary).hexdigest()
    ext = os.path.splitext(filename)[-1].strip(".")
    outfile = os.path.join(app.config['UPLOAD_DIRECTORY'], \
        f"{filename_hash}.{ext}")
    if os.path.exists(outfile):
        return "ERROR: File exists\r\n", 409
    with open(outfile, "wb") as f:
        f.write(file_binary)

    # Get text from the receipt with OCR
    # TODO
    parsed_ocr = ""

    # Things related to tags, must be executed after tags parsing
    purchase_date = parse_purchase_date(tags)
    expiry_date = parse_expiry_date(purchase_date, tags)

    # Save to DB
    receipt = {"filename": outfile, \
               "purchase_date": purchase_date, \
               "expiry_date": expiry_date, \
               "ocr_text": parsed_ocr}
    receipt_id = dbeng.insert_receipt(receipt)
    if receipt_id == -1:
        logging.error(f"Returned receipt ID was wrong: {receipt_id}")
        return "ERROR: terror\n", 503 # XXX
    dbeng.insert_tags(tags)
    dbeng.insert_receipt_tags_association(receipt_id, tags)

    return "Upload OK\r\n", 200

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-d", help="Debug mode", action="store_true")
    args = argparser.parse_args()

    if args.d:
        app.debug = True
        logger = logging.basicConfig(
             datefmt="%Y-%m-%d %H:%M:%S", \
             format="%(asctime)s.%(msecs)03d: %(levelname)s %(message)s", \
             level=logging.INFO)
    else:
        logger = logging.basicConfig(filename="receiptsapi.log", \
             datefmt="%Y-%m-%d %H:%M:%S", \
             format="%(asctime)s.%(msecs)03d: %(levelname)s %(message)s", \
             level=logging.INFO)

    app.run(host='127.0.0.1', port=5555)

