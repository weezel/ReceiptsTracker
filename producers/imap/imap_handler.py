#!/usr/bin/env python3

import configparser
import email
import hashlib
import imaplib
import logging
import os
import pytz
import requests
import sys

import dateutil.parser
from typing import Generator


received_tz = pytz.timezone("CET")
local_tz = pytz.timezone("Europe/Helsinki")

class CredsException(): pass

import re
pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')
def parse_uid(data):
    match = pattern_uid.match(data)
    return match.group('uid')

class ImapHandler(object):
    def __init__(self, **kwargs):
        '''
        Constructor.
        :param login_name (str): IMAP login name
        :param password (str): IMAP password
        :param server_address (str): IMAP server address
        :parem folder (str): IMAP folder to fetch messages
        '''
        self.login_name = kwargs['login_name']
        self.password = kwargs['password']
        self.server_address = kwargs['server_address']
        self.folder = kwargs['folder']
        self.imap = imaplib.IMAP4_SSL(self.server_address)

    def __enter__(self):
        self.imap.login(self.login_name, self.password)
        return self

    def __exit__(self, type, value, traceback):
        self.imap.close()
        self.imap.logout()

    def get_count(self) -> int:
        self.imap.select(self.folder)
        status, data = self.imap.search(None, 'ALL')
        return sum(1 for num in data[0].split())

    def delete_message(self, msg_id, subject) -> None:
        self.imap.select(self.folder)
        logging.info(f"Deleting message ID {msg_id} with subject {subject}")
        self.imap.store(msg_id, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def move_message(self, msg_id: str, dest_folder: str) -> None:
        result = self.imap.uid('COPY', msg_id, dest_folder)

        if result[0] == 'OK':
            mov, data = self.imap.uid('STORE', msg_id, '+FLAGS', '(\Deleted)')
            self.imap.expunge()

    def sha256_checksum(self, data: str) -> str:
        return hashlib.sha256(data).hexdigest()

    def yield_messages(self) -> Generator[dict, None, None]:
        self.imap.select(mailbox=self.folder, readonly=False)
        all_status, all_data = self.imap.search(None, 'ALL')
        logging.info(f"Total messages available: {len(all_data)}")
        for num in reversed(all_data[0].split()):
            status, data = self.imap.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            subject = email.header.decode_header(msg["Subject"])
            from_field = msg["From"]
            parsed_date = dateutil.parser.parse(msg["Date"])
            arrival_time = parsed_date.replace(tzinfo=received_tz) \
                                      .astimezone(tz=local_tz)
            cleaned_subj = filter(lambda x: x is not None, subject[0])
            cleaned_subj = " ".join(cleaned_subj).rstrip("\n")
            # cleaned_subj will be sent as tags, hence mark sender (from)
            # XXX cleaned_subj.append(f"from_

            msgid_resp, msg_id = self.imap.fetch(num, "(UID)")
            msg_uid = parse_uid(msg_id[0].decode())

            for part in msg.walk():
                content_type = part.get_content_type()
                if not content_type.startswith("image/"):
                    continue

                orig_fname = part.get_filename()

                msg_payload = part.get_payload(decode=True)
                fout_name = self.sha256_checksum(msg_payload)
                fout_ext = "." + orig_fname.rsplit(".", 1)[1].lower()

                logmsg = f"Retrieving ID {int(num)} {fout_name}{fout_ext} " \
                         + f"[{len(msg_payload)} bytes] with subject: " \
                         + f"{cleaned_subj}"
                logging.info(logmsg)

                yield {"fname": fout_name + fout_ext,
                       "msg_uid": msg_uid,
                       "arrival_time": arrival_time,
                       "tags": cleaned_subj,
                       "payload": msg_payload}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"ERROR: {sys.argv[0]}: Missing configuration filename. Must be absolute path")
        sys.exit(1)

    os.chdir(os.path.dirname(sys.argv[1]))

    must_have_sections = ('IMAP', 'Messages', 'Receipts_api',)
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    if not all(i in config.sections() for i in must_have_sections):
        print("ERROR: {}: Parsing config file failed. Must have sections: {}"
              .format(sys.argv[0], " ".join(must_have_sections)))
        sys.exit(1)

    login_name = config['IMAP']['login_name']
    password = config['IMAP']['password']
    server_address = config['IMAP']['server_address']
    folder = config['IMAP']['folder']
    receipt_api_host = config['Receipts_api']['server_address']

    logging.basicConfig(filename="imap_handler.log",
                datefmt="%Y-%m-%d %H:%M:%S",
                format="%(asctime)s.%(msecs)03d: %(levelname)s %(message)s",
                level=logging.INFO)

    with ImapHandler(login_name=login_name,
                     password=password,
                     server_address=server_address,
                     folder=folder) as imap_handler:
        for msg in imap_handler.yield_messages():
            logmsg = f"msgid_{int(msg['msg_uid'])}: Sending {msg['fname']} with tags '{msg['tags']}' to {receipt_api_host}"
            logging.info(logmsg)
            ret = requests.post(receipt_api_host,
                                files={'tags': (None, msg['tags']),
                                       'file': (msg['fname'], msg['payload'])})
            if ret.ok:
                logging.info(f"msgid_{int(msg['msg_uid'])}: Moving message to receipts/archived")
                imap_handler.move_message(msg["msg_uid"], "receipts/archived")
                logging.info(f"msgid_{int(msg['msg_uid'])}: Message archived")
                logging.info(f"msgid_{int(msg['msg_uid'])}: Completed")
            else:
                logging.info(f"msgid_{int(msg['msg_uid'])}: [{ret.status_code}] {ret.content}")

