#!/usr/bin/env python3
import sys
sys.path.append("..")

import datetime
import unittest

from dateutil.relativedelta import relativedelta

import receipts_api


class ReceiptsApiParsers(unittest.TestCase):
    def test_parse_tags(self):
        tagsString = "2019-01-12 receipt test aaargfh blragh asdf"
        tagsList = tagsString.split(" ")
        tagsList.sort()
        parsed = receipts_api.parse_tags(tagsString)
        self.assertListEqual(parsed, tagsList)

    def test_parse_expiry_date(self):
        test_day = "1_day"
        test_days = "10_days"
        test_month = "1_month"
        test_months = "10_months"
        test_year = "1_years"
        test_years = "25_years"
        some_date = datetime.datetime(2000, 6, 1, 8, 0)

        print(f"\nStart date: {some_date}")

        # Test "days" expiration
        self.assertEqual(receipts_api.parse_expiry_date( \
                             some_date,  [test_day, "a", "b"]), \
                         some_date + relativedelta(days=1), \
                         "Expiring after one day failed")
        days = datetime.datetime(2000, 6, 11, 8, 0)
        print(f"After 10 days: {days}")
        self.assertEqual(receipts_api.parse_expiry_date( \
                             some_date,  [test_days, "a", "b"]), \
                         days, \
                         "Expiring after 10 days failed")

        # Test "months" expiration
        self.assertEqual(receipts_api.parse_expiry_date( \
                             some_date,  [test_month, "a", "b"]), \
                         some_date + relativedelta(months=1), \
                         "Expiring after one month failed")
        months = datetime.datetime(2001, 4, 1, 8, 0)
        print(f"After 10 months: {months}")
        self.assertEqual(receipts_api.parse_expiry_date( \
                             some_date,  [test_months, "a", "b"]), \
                         months, \
                         "Expiring after 10 months failed")

        # Test "years" expiration
        self.assertEqual(receipts_api.parse_expiry_date( \
                             some_date,  [test_year, "a", "b"]), \
                         some_date + relativedelta(years=1), \
                         "Expiring after one month failed")
        years = datetime.datetime(2025, 6, 1, 8, 0)
        print(f"After 25 years: {years}")
        self.assertEqual(receipts_api.parse_expiry_date( \
                             some_date,  [test_years, "a", "b"]), \
                         years, \
                         "Expiring after 25 years failed")

if __name__ == '__main__':
    unittest.main()
