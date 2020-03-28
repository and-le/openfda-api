#!usr/bin/env python

"""Retrieves information on 510(k) medical devices from the FDA database and stores it in a Microsoft Excel file"""

import datetime
import tkinter  # For a simple GUI
import threading  # For threading queries

import openpyxl  # For writing to MS Excel
import requests  # For making HTTPS requests

# Base endpoint for API calls to 510(k) API
BASE_URL_510k = "https://api.fda.gov/device/510k.json"

# 510(k) Dictionary Keys
RESULTS_DICT_KEY = "results"  # "results" is a list of dictionaries

# 510(k) Query Params
SEARCH_QUERY_KEY = "search"  # specifies which fields to search
LIMIT_QUERY_KEY = "limit"  # specifies how many results to return
MAX_QUERY_SIZE = 99  # maximum number of results that a query can return

# 510(k) Query syntax characters
QUERY_FIELD_COLON = ":"
LOGICAL_OR_510k = "+"
LOGICAL_AND_510k = "AND"

# 510(k) "results" dictionary record attributes
ADDRESS_1__KEY = "address_1"
APPLICANT_KEY = "applicant"
CONTACT_KEY = "contact"
COUNTRY_CODE_KEY = "country_code"
STATE_KEY = "state"

DATE_RECEIVED_KEY = "date_received"
DECISION_CODE_KEY = "decision_code"
DECISION_DATE_KEY = "decision_date"

DEVICE_NAME_KEY = "device_name"
K_NUMBER_KEY = "k_number"

# Constants for Strings
EMPTY_STR = ""
EQUALS_STR = "="

# User input constants
DATE_FORMAT_UI = "YYYY-MM-DD"
DATE_STR_TO_DATE_TIME_FORMAT = "%Y-%m-%d"

# Excel files
EXCEL_FILE_FORMAT = ".xlsx"
EXCEL_SHEET_NAME = "510(k)"

# tkinter GUI
TO_DECISION_DATE_LBL_TEXT = "To Decision Date (" + DATE_FORMAT_UI + ")"
FROM_DECISION_DATE_LBL_TEXT = "From Decision Date (" + DATE_FORMAT_UI + ")"
EXCEL_FILE_LBL_TEXT = "Name of MS Excel file to save results in (must be a .xlsx file)"
RUN_QUERY_BTN_TEXT = "Get 510(k) medical device data"

QUERY_STATUS_LBL_TEXT = "Query status: "
QUERY_STATUS_RUNNING_TEXT = "Getting data ..."
QUERY_STATUS_FINISHED_TEXT = "Finished getting data. Check your current folder/directory for the Excel file"

INVALID_TO_DATE_MSG = "The 'to' date is invalid."
INVALID_FROM_DATE_MSG = "The 'from' date is invalid."
INVALID_DATE_RANGE_MSG = "The date range is invalid."
INVALID_EXCEL_FILE_PATH_MSG = "The MS Excel file path is invalid."

# tkinter event-handling
WM_DELETE_WINDOW_EVENT_STR = "WM_DELETE_WINDOW"

# Global variables for program execution
window = None
to_decision_date_ent = None
from_decision_date_ent = None
excel_file_ent = None
query_status_lbl = None
run_query_btn = None
USING_GUI = False


class SearchQueryBuilder510k:
    """
    Builder for the "search" key in the openFDA 510(k) API
    """

    def __init__(self):
        self.query_string = EMPTY_STR
        self.has_query_field = False

    def add_first_query_field(self, query_field_name, query_field_value):
        if not self.has_query_field:
            self.query_string = self.query_string + query_field_name + QUERY_FIELD_COLON + query_field_value
            self.has_query_field = True
        else:
            raise ValueError("Cannot add first query field because a query field already exists.")
        return self

    def add_query_field(self, query_field_name, query_field_value, logical_operator):
        if not self.has_query_field:
            raise ValueError("You must add a first query field.")
        else:
            if logical_operator == LOGICAL_AND_510k:
                self.query_string = self.query_string + LOGICAL_OR_510k + LOGICAL_AND_510k + LOGICAL_OR_510k + \
                                    query_field_name + QUERY_FIELD_COLON + query_field_value
            elif logical_operator == LOGICAL_OR_510k:
                self.query_string = self.query_string + LOGICAL_OR_510k + query_field_name + \
                                    QUERY_FIELD_COLON + query_field_value
            else:
                raise ValueError(f"Logical operator '{logical_operator}' is invalid.")
            return self

    def get_search_query_string(self):
        return self.query_string


def get_string_from_params(params):
    return "&".join("%s=%s" % (k, v) for k, v in params.items())


def get_previous_day_from_datetime(current_datetime):
    return current_datetime - datetime.timedelta(days=1)


def extract_device_records_from_response(response):
    # Get the list of records that matched the GET
    results = response.json()[RESULTS_DICT_KEY]

    # Add each record to our list of records
    records = []
    for result in results:
        record = {
            # Info about applicant, location
            ADDRESS_1__KEY: result[ADDRESS_1__KEY],
            APPLICANT_KEY: result[APPLICANT_KEY],
            CONTACT_KEY: result[CONTACT_KEY],
            COUNTRY_CODE_KEY: result[COUNTRY_CODE_KEY],
            STATE_KEY: result[STATE_KEY],

            # Info about approval process
            DATE_RECEIVED_KEY: result[DATE_RECEIVED_KEY],
            DECISION_DATE_KEY: result[DECISION_DATE_KEY],
            DECISION_CODE_KEY: result[DECISION_CODE_KEY],
            DECISION_DESCRIPTION_FIELD: result[DECISION_DESCRIPTION_FIELD],

            # Info about device
            DEVICE_NAME_KEY: result[DEVICE_NAME_KEY],
            K_NUMBER_KEY: result[K_NUMBER_KEY],
        }

        records.append(record)
    return records


def validate_date(a_date_str):
    # Try to parse the date string
    try:
        a_date = datetime.datetime.strptime(a_date_str, DATE_STR_TO_DATE_TIME_FORMAT)
        return True
    # If the format is incorrect, catch the ValueError and return False to indicate that the date is invalid
    except ValueError:
        return False


def validate_date_range(from_date_str, to_date_str):
    # Convert the from and to date strings to datetime objects
    from_date = datetime.datetime.strptime(from_date_str, DATE_STR_TO_DATE_TIME_FORMAT)
    to_date = datetime.datetime.strptime(to_date_str, DATE_STR_TO_DATE_TIME_FORMAT)

    # Calculate the difference in days between the to-date and from-date
    delta = to_date - from_date

    # If the time delta is >= 0, the date range is valid; otherwise, it is invalid
    return delta >= datetime.timedelta(0)


def validate_excel_file(excel_file_path):
    return excel_file_path.endswith(EXCEL_FILE_FORMAT)


def validate_input(from_decision_date_str, to_decision_date_str, excel_file_path):
    # Use the global query status label to let the user know which inputs they may have entered incorrectly
    global query_status_lbl

    # Validate the date formats on the dates
    if not validate_date(from_decision_date_str):
        update_query_status_lbl(INVALID_FROM_DATE_MSG)
        return False

    if not validate_date(to_decision_date_str):
        update_query_status_lbl(INVALID_TO_DATE_MSG)
        return False

    # Validate the date range of the to and from dates
    if not validate_date_range(from_decision_date_str, to_decision_date_str):
        update_query_status_lbl(INVALID_DATE_RANGE_MSG)
        return False

    # Validate the format of the Excel file: it must end with a .xlsx
    if not validate_excel_file(excel_file_path):
        update_query_status_lbl(INVALID_EXCEL_FILE_PATH_MSG)
        return False

    # At this point, all inputs have been validated as correct
    return True


def run_query(to_decision_date, from_decision_date, excel_file_path):
    # Store the device info in a list
    devices_info = []

    # Set the current date from which to make GET requests
    current_date = datetime.datetime.strptime(to_decision_date,
                                              DATE_STR_TO_DATE_TIME_FORMAT)  # Convert date str to datetime
    iso_formatted_date = datetime.date.isoformat(current_date)  # Intentionally passing datetime to date

    # Set the date to stop querying at
    stop_date = datetime.datetime.strptime(from_decision_date, DATE_STR_TO_DATE_TIME_FORMAT)

    # Query all dates in the range [stop_date, current_date]
    while not current_date == get_previous_day_from_datetime(stop_date):
        # Build the search query string
        query_builder = SearchQueryBuilder510k()
        search_query_str = query_builder.add_first_query_field(DECISION_DATE_KEY, iso_formatted_date) \
            .get_search_query_string()

        # Set the query params
        params = {
            "search": search_query_str,
            "limit": MAX_QUERY_SIZE,
        }

        # Re-construct the GET url
        # Convert the "params" to a string for the GET request
        # This is done because the requests module converts square brackets [] into percent encodings, which
        # the openFDA API does not understand.
        params_str = get_string_from_params(params)

        # Construct the GET url
        get_url = BASE_URL_510k + "?" + params_str

        # Make the GET request
        response = requests.get(get_url)

        # If the GET request was successful, extract the desired info from each device entry
        records = []
        if response.status_code == 200:
            records = extract_device_records_from_response(response)

            # Add the devices to our list
            devices_info.extend(records)

        # Go back one calendar day by re-assigning the current date
        current_date = get_previous_day_from_datetime(current_date)
        iso_formatted_date = datetime.date.isoformat(current_date)

    # If we're using the GUI, then this method will have been started as a thread. As a result, we need to call the
    # method below to start the next thread to save data to the workbook
    if USING_GUI:
        handle_run_query(devices_info, excel_file_path)

    return devices_info


def save_devices_info_to_excel_file(devices_info, excel_file):
    global run_query_btn

    # Create an Excel workbook and worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.create_sheet(EXCEL_SHEET_NAME)

    # Write the column labels to the worksheet
    col_headers = list(devices_info[0].keys())
    worksheet.append(col_headers)

    # Write the device records to each row in the worksheet
    for info in devices_info:
        worksheet.append(list(info.values()))

    workbook.save(excel_file)

    # If using the GUI, then update the GUI:
    if USING_GUI:
        # Notify the user that the workbook is available
        update_query_status_lbl(QUERY_STATUS_FINISHED_TEXT)

        # Enable the query button again
        run_query_btn.config(state=tkinter.ACTIVE)


def handle_left_mouse_button_click():
    global to_decision_date_ent
    global from_decision_date_ent
    global excel_file_ent
    global run_query_btn

    # Get the start date, end date, and excel file that the user provided
    to_decision_date_str = to_decision_date_ent.get()
    from_decision_date_str = from_decision_date_ent.get()
    excel_file_path = excel_file_ent.get()

    # Validate the user's input
    valid_input = validate_input(from_decision_date_str, to_decision_date_str, excel_file_path)
    if not valid_input:
        return

    # Disable the button until the query is finished
    run_query_btn.config(state=tkinter.DISABLED)

    # Create a separate thread to run the query
    run_query_thread = threading.Thread(target=run_query, args=(to_decision_date_str, from_decision_date_str,
                                                                excel_file_path))
    # Make this thread a daemon so that it is killed automatically when the main thread exits
    run_query_thread.daemon = True

    # Update the query status label
    update_query_status_lbl(QUERY_STATUS_RUNNING_TEXT)

    # Run the thread
    run_query_thread.start()


def handle_run_query(devices_info, excel_file_path):
    # Create a thread to save the device info
    save_devices_info_thread = threading.Thread(target=save_devices_info_to_excel_file,
                                                args=(devices_info, excel_file_path))
    # Make this thread a daemon so that it is killed automatically when the main thread exits
    save_devices_info_thread.daemon = True

    save_devices_info_thread.start()


def handle_window_close():
    global window
    window.quit()
    window.destroy()


def update_query_status_lbl(lbl_text):
    global query_status_lbl

    # Only try to update the GUI if we are using it. The flag may be false in a unit test, for example.
    if USING_GUI:
        new_text = QUERY_STATUS_LBL_TEXT + lbl_text
        query_status_lbl.configure(text=new_text)


def main():
    # Set the USING_GUI flag
    global USING_GUI
    USING_GUI = True

    # Use the global start and end decision date Entry objects so that they can be accessed in the event handler
    global to_decision_date_ent
    global from_decision_date_ent
    global excel_file_ent
    global query_status_lbl
    global run_query_btn

    # Use the global window
    global window

    # Create a window
    window = tkinter.Tk()

    # Bind the event-handler to the window close
    window.protocol(WM_DELETE_WINDOW_EVENT_STR, handle_window_close)

    # Create a label for the from decision date, and add it to the window
    from_decision_date_lbl = tkinter.Label(text=FROM_DECISION_DATE_LBL_TEXT)
    from_decision_date_lbl.pack()

    # Create a text box entry for the from decision date, and add it to the window
    from_decision_date_ent = tkinter.Entry()
    from_decision_date_ent.pack()

    # Similar to above, but for the to decision date
    to_decision_date_lbl = tkinter.Label(text=TO_DECISION_DATE_LBL_TEXT)
    to_decision_date_lbl.pack()

    to_decision_date_ent = tkinter.Entry()
    to_decision_date_ent.pack()

    # Similar to above: create a label for the Excel file path and an entry, and add them to the window
    excel_file_path_lbl = tkinter.Label(text=EXCEL_FILE_LBL_TEXT)
    excel_file_path_lbl.pack()

    excel_file_ent = tkinter.Entry()
    excel_file_ent.pack()

    # Create a button that the user can click to run the query and make it listen for mouse clicks
    run_query_btn = tkinter.Button(text=RUN_QUERY_BTN_TEXT, command=handle_left_mouse_button_click)

    # Add the button to the window
    run_query_btn.pack()

    # Add a label to indicate the progress of the query
    query_status_lbl = tkinter.Label(text=QUERY_STATUS_LBL_TEXT)
    query_status_lbl.pack()

    # Run the window
    window.mainloop()


if __name__ == "__main__":
    main()
