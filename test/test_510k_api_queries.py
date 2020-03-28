#!/usr/bin/env python

"""
Contains unit tests for methods that query from the openFDA API
"""

import unittest
import os

import openpyxl

from src import fda_510k_api


class Test510kOpenFdaQueries(unittest.TestCase):

    @classmethod
    def setupClass(self):
        # Set the "USING_GUI" flag to False for testing
        fda_510k_api.USING_GUI = False


    def test_run_query_one_day(self):
        from_decision_date = "2019-12-08"
        to_decision_date = "2019-12-08"
        excel_file_path = "book.xlsx"

        # The return value contains many fields. This test checks that the relevant fields are correct, but not
        # all fields
        devices_info = fda_510k_api.run_query(to_decision_date, from_decision_date, excel_file_path)

        expected_applicant = "Etiometry, Inc."
        expected_decision_date = "2019-12-08"
        expected_device_name = "T3 Platform software"
        expected_k_number = "K190273"

        self.assertEqual(expected_applicant, devices_info[0][fda_510k_api.APPLICANT_KEY])
        self.assertEqual(expected_decision_date, devices_info[0][fda_510k_api.DECISION_DATE_KEY])
        self.assertEqual(expected_device_name, devices_info[0][fda_510k_api.DEVICE_NAME_KEY])
        self.assertEqual(expected_k_number, devices_info[0][fda_510k_api.K_NUMBER_KEY])

    def test_run_query_two_days(self):
        from_decision_date = "2019-12-07"
        to_decision_date = "2019-12-08"
        excel_file_path = "book.xlsx"

        # The return value contains many fields. This test checks that the relevant fields are correct, but not
        # all fields
        devices_info = fda_510k_api.run_query(to_decision_date, from_decision_date, excel_file_path)

        # There should be 2 records
        expected_num_devices = 2
        self.assertEqual(expected_num_devices, len(devices_info))

        # Verify the first record
        first_expected_applicant_ = "Etiometry, Inc."
        first_expected_decision_date = "2019-12-08"
        first_expected_device_name = "T3 Platform software"
        first_expected_k_number = "K190273"

        self.assertEqual(first_expected_applicant_, devices_info[0][fda_510k_api.APPLICANT_KEY])
        self.assertEqual(first_expected_decision_date, devices_info[0][fda_510k_api.DECISION_DATE_KEY])
        self.assertEqual(first_expected_device_name, devices_info[0][fda_510k_api.DEVICE_NAME_KEY])
        self.assertEqual(first_expected_k_number, devices_info[0][fda_510k_api.K_NUMBER_KEY])

        # Verify the second record
        second_expected_applicant_ = "OrthoGrid Systems Inc."
        second_expected_decision_date = "2019-12-07"
        second_expected_device_name = "PhantomMSK Trauma"
        second_expected_k_number = "K192279"

        self.assertEqual(second_expected_applicant_, devices_info[1][fda_510k_api.APPLICANT_KEY])
        self.assertEqual(second_expected_decision_date, devices_info[1][fda_510k_api.DECISION_DATE_KEY])
        self.assertEqual(second_expected_device_name, devices_info[1][fda_510k_api.DEVICE_NAME_KEY])
        self.assertEqual(second_expected_k_number, devices_info[1][fda_510k_api.K_NUMBER_KEY])

    def test_save_devices_info(self):
        from_decision_date = "2019-12-07"
        to_decision_date = "2019-12-08"
        excel_file_path = "test_workbook.xlsx"

        # Query for the devices info
        devices_info = fda_510k_api.run_query(to_decision_date, from_decision_date, excel_file_path)

        # Write this info to an excel file
        fda_510k_api.save_devices_info_to_excel_file(devices_info, excel_file_path)

        # Check that the info was written correctly
        # Open the workbook that was written to
        workbook = openpyxl.load_workbook(excel_file_path)

        # Get the worksheet that we saved data to
        worksheet = workbook[fda_510k_api.EXCEL_SHEET_NAME]

        # Get the rows of data
        excel_rows = [row for row in worksheet.values]

        # Verify the column headers
        expected_col_headers = tuple(devices_info[0].keys())
        self.assertEqual(expected_col_headers, excel_rows[0])

        # Verify the first row of data
        expected_first_row = tuple(devices_info[0].values())
        self.assertEqual(expected_first_row, excel_rows[1])

        # Verify the second row of data
        expected_second_row = tuple(devices_info[1].values())
        self.assertEqual(expected_second_row, excel_rows[2])

        # Close the workbook so we can safely delete it
        workbook.close()
        os.remove(excel_file_path)



if __name__ == '__main__':
    unittest.main()
