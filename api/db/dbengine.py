#!/usr/bin/env python3

import os.path
import sqlite3
import threading
from typing import List

TagList = List[str]
TagResults = List[int]
db_name = "receipts.db"
schema_file = "resources/schema.sql"

schema_script = """
CREATE TABLE receipt (
        id INTEGER PRIMARY KEY,
        filename VARCHAR NOT NULL,
        purchase_date DATE,
        expiry_date DATE,
        ocr_text VARCHAR,
        UNIQUE (filename)
);
CREATE TABLE tag (
        id INTEGER PRIMARY KEY,
        tag VARCHAR,
        UNIQUE (tag)
);
CREATE TABLE receipt_tag_association (
        id INTEGER PRIMARY KEY,
        receipt_id INTEGER,
        tag_id INTEGER,
        FOREIGN KEY(receipt_id) REFERENCES receipt (id),
        FOREIGN KEY(tag_id) REFERENCES tag (id)
);"""


def got_mandatory_receipt_params(params: list) -> None:
    must_params = ["filename", "purchase_date", "expiry_date", "ocr_text"]
    must_params.sort()

    params.sort()

    if all(k1 == k2 for k1, k2 in zip(must_params, params)):
        return True
    return False

class DbEngine(object):
    def __init__(self, logger, db_path:str=db_name):
        self.conn = None
        self.cur = None
        self.db_path = db_path
        self.lock = threading.Lock()
        self.logger = logger

        if not os.path.exists(self.db_path):
            self.__init_connection()
            self.__init_schema()
        else:
            self.__init_connection()

    def __del__(self):
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def __init_schema(self):
        schemas = ""
        #with open(schema_file, "r") as f:
        #    schemas = f.read()
        with self.lock:
            res = self.cur.executescript(schema_script)
            self.conn.commit()

    def __init_connection(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def insert_receipt(self, receipt: dict) -> int:
        inserted_row_id = -1
        receipt_keys = [k for k in receipt.keys()]
        if got_mandatory_receipt_params(receipt_keys):
            cols = ", ".join(receipt.keys())
            placeholders = ":" + ", :".join(receipt.keys())
            insert_q = f"INSERT OR IGNORE INTO receipt({cols}) " \
                               + f"VALUES ({placeholders});"
            with self.lock:
                self.cur.execute(insert_q, receipt)
                self.conn.commit()
                inserted_row_id = self.cur.lastrowid
        else:
            self.logger.info(f"Won't insert {receipt} due missing mandatory parameters")
        return inserted_row_id

    def insert_tags(self, tags: list) -> int:
        rows_inserted = 0
        insert_q = f"INSERT OR IGNORE INTO tag (tag) VALUES (?);"
        # Generate row factor format and remove duplicates
        row_tags = [(i,) for i in set(tags)]
        with self.lock:
            self.cur.executemany(insert_q, row_tags)
            self.conn.commit()
            rows_inserted = self.cur.rowcount
        return rows_inserted

    def get_tag_ids(self, tags: TagList) -> TagResults:
        uniq_tags = [t for t in set(tags)]
        qmarks = "{}".format(", ".join("?" * len(tags)))
        q = f"SELECT id FROM tag WHERE tag in ({qmarks});"
        result = self.cur.execute(q, uniq_tags)
        return [i["id"] for i in result.fetchall()]

    def insert_receipt_tags_association(self, receipt_id: int, tags: TagList):
        tag_ids = self.get_tag_ids(tags)
        rows = [(receipt_id, tag_id) for tag_id in tag_ids]

        insert_q = "INSERT OR IGNORE INTO receipt_tag_association " \
                       + "(receipt_id, tag_id) VALUES (?, ?);"
        with self.lock:
            self.cur.executemany(insert_q, rows)
            self.conn.commit()

