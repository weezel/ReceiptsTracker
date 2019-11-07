#!/usr/bin/env python3
import sys
sys.path.append("..")

import logging
import os
import unittest

import db.dbengine as dbengine


test_db_name = "test.db"

class DbEngTests(unittest.TestCase):
    def setUp(self):
        if os.path.exists(test_db_name):
            os.unlink(test_db_name)

    def test_receipts_mandatory_params(self):
        mandatory_params = ["filename",
                            "purchase_date",
                            "ocr_text",
                            "expiry_date"]
        mandatory_params_result = dbengine.got_mandatory_receipt_params( \
                mandatory_params)
        self.assertTrue(mandatory_params_result, "Missing mandatory params")

        vague_params = ["filename", "expiry_date", "non_existing"]
        vague_params_result = dbengine.got_mandatory_receipt_params( \
                vague_params)
        self.assertFalse(vague_params_result, "Missing mandatory params #2")

    def test_db_receipt_insert(self):
        dbeng = dbengine.DbEngine(logging, test_db_name)
        expected_last_row_id = 1
        r = {"filename": "deadbeef.jpg",
             "purchase_date": "2019-12-01",
             "ocr_text": "hiphei uuh aah nam nam",
             "expiry_date": "2_years"}
        last_row_id = dbeng.insert_receipt(r)
        self.assertEqual(expected_last_row_id, last_row_id,
                         "expected_last_row_id and last_row_id differ")

    def test_db_insert_and_get_tag(self):
        expected_count = 4
        dbeng = dbengine.DbEngine(logging, test_db_name)
        tags = ["3_months",
                "2016-06-06",
                "that_shop_name",
                "groceries"]
        rows_inserted = dbeng.insert_tags(tags)

        received = dbeng.get_tag_ids(tags)
        self.assertEqual(expected_count, len(received), "Tag IDs differ")

    def test_insert_receipt_tag_association(self):
        dbeng = dbengine.DbEngine(logging, test_db_name)

        tags = ["3_months",
                "2016-06-06",
                "that_shop_name",
                "groceries"]
        dbeng.insert_tags(tags)
        tag_ids = dbeng.get_tag_ids(tags)

        receipt = {"filename": "deadbeef.jpg",
                   "purchase_date": "2019-12-01",
                   "ocr_text": "hiphei uuh aah nam nam",
                   "expiry_date": "2_years"}
        receipt_id = dbeng.insert_receipt(receipt)
        self.assertGreater(receipt_id, 0, "Wrong receipt id")

        res = dbeng.insert_receipt_tags_association(receipt_id, tag_ids)

if __name__ == '__main__':
    unittest.main()
