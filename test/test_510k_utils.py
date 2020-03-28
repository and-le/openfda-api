#!/usr/bin/env python

"""
Unit tests for various utility functions in the openFDA 510(k) API script
"""

import unittest
import datetime

from src import fda_510k_api


class Test510kUtils(unittest.TestCase):
    def test_get_string_from_params(self):
        # Set params dict
        params = {
            "key_1" : "val_1",
            "key_2" : "val_2",
        }

        expected = "key_1=val_1&key_2=val_2"

        self.assertEqual(expected, fda_510k_api.get_string_from_params(params))

    def test_get_previous_day_from_date(self):
        # Create a datetime
        year = 2020
        month = 10
        day_of_month = 20
        current_date = datetime.datetime(year, month, day_of_month)

        # Expected date is the previous day
        expected_date = datetime.datetime(year, month, day_of_month - 1)

        self.assertEqual(expected_date, fda_510k_api.get_previous_day_from_datetime(current_date))


    def test_validate_date_valid(self):
        # Create a valid date; validator should return true
        valid_date_str = "2020-04-10"
        self.assertTrue(fda_510k_api.validate_date(valid_date_str))


    def test_validate_date_invalid(self):
        # Create an invalid date; validator should return False
        invalid_date_str = "2020/04/10"
        self.assertFalse(fda_510k_api.validate_date(invalid_date_str))


    def test_validate_date_range_valid(self):
        # Test a valid date range
        valid_from_date_str = "2020-04-10"
        valid_to_date_str = "2020-05-10"
        self.assertTrue(fda_510k_api.validate_date_range(valid_from_date_str, valid_to_date_str))

    def test_validate_date_range_invalid(self):
        # Test an invalid date range
        invalid_from_date_str = "2020-04-10"
        invalid_to_date_str = "2020-04-09"
        self.assertFalse(fda_510k_api.validate_date_range(invalid_from_date_str, invalid_to_date_str))

    def test_validate_date_range_same_day(self):
        # Test a date range that starts and ends on the same day
        date_str = "2020-03-20"
        self.assertTrue(fda_510k_api.validate_date_range(date_str, date_str))


    def test_validate_excel_file_valid(self):
        # Test a valid excel file
        valid_excel_file_path = "valid.xlsx"
        self.assertTrue(fda_510k_api.validate_excel_file(valid_excel_file_path))

    def test_validate_excel_file_invalid(self):
        # Test an invalid excel file
        invalid_excel_file_path = "valid.xls"  # Missing the last x
        self.assertFalse(fda_510k_api.validate_excel_file(invalid_excel_file_path))

    def test_validate_input_invalid_to_date_str(self):
        invalid_to_date_str = ""
        valid_from_date_str = "2020-03-01"
        valid_excel_file_path = "valid.xlsx"
        self.assertFalse(fda_510k_api.validate_input(invalid_to_date_str, valid_from_date_str, valid_excel_file_path))

    def test_validate_input_invalid_from_date_str(self):
        invalid_from_date_str = ""
        valid_to_date_str = "2020-03-01"
        valid_excel_file_path = "valid.xlsx"
        self.assertFalse(fda_510k_api.validate_input(valid_to_date_str, invalid_from_date_str, valid_excel_file_path))

    def test_validate_input_invalid_date_range(self):
        from_date_str = "2020-04-05"
        to_date_str = "2020-03-01"
        valid_excel_file_path = "valid.xlsx"
        self.assertFalse(fda_510k_api.validate_input(from_date_str, to_date_str, valid_excel_file_path))


    def test_validate_input_invalid_excel_file(self):
        from_date_str = "2020-04-05"
        to_date_str = "2020-05-01"
        invalid_excel_file_path = "invalid.xl"
        self.assertFalse(fda_510k_api.validate_input(from_date_str, to_date_str, invalid_excel_file_path))


    def test_validate_input_valid(self):
        from_date_str = "2020-04-05"
        to_date_str = "2020-05-01"
        valid_excel_file_path = "valid.xlsx"
        self.assertTrue(fda_510k_api.validate_input(from_date_str, to_date_str, valid_excel_file_path))


if __name__ == '__main__':
    unittest.main()
