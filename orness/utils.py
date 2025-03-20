
from datetime import datetime
import json
import logging
import pandas as pd
from orness import error_exception

"""
This module contains utility functions that are used in the ORNESS application.
"""



logger = logging.getLogger(__name__)

def date_format(date) -> str:
    """
    Format the input date to a string in the format 'YYYY-MM-DD'.

    Parameters:
        date (str or datetime): The input date to be formatted.

    Returns:
        str: The formatted date in the format 'YYYY-MM-DD'.
    """

    # Check if date is empty
    if not date:
        return datetime.now().strftime('%Y-%m-%d')
    
    # If the date is a string, try to convert it to a datetime object
    if isinstance(date, str):
        try:
            # Parse the string to a datetime object
            input_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            # Handle invalid string date format
            logger.error("Invalid date format. Please use YYYY-MM-DD.")
            return ""
    
    # If the date is already a datetime object (e.g., from pandas Excel import)
    elif isinstance(date, pd.Timestamp) or isinstance(date, datetime):
        input_date = date
    else:
        return "Invalid input date type."

    # Compare the input date with the current date
    if input_date > datetime.now():
        return input_date.strftime('%Y-%m-%d')  # Return future date as is
    else:
        return datetime.now().strftime('%Y-%m-%d')  # Return today's date
    


def read_data_from_file(filename):
    """
    Read the excel file and return the content in a json format.

    Parameters:
        filename (str): name of the excel file to read

    Returns:
        dict: the content of the excel file in json format
    """
    exc = pd.read_excel(filename).dropna(how='all')
    exc['Execution date'] = pd.to_datetime(exc['Execution date'],
                                           errors="coerce").dt.strftime('%Y-%m-%d')
    myjson = json.loads(exc.to_json(orient='records')) #convert str to dict
    return myjson

def get_payment_fee_and_priority(options: list, priority: str ="48H", who_pays:str = "OUR") -> dict:
    """
    Retrieve fee and priority options from a list of payment options.

    This function takes a list of payment options, a priority, and a fee payer as parameters.
    It then filters the list of options to find the one that matches the given parameters,
    and returns a dictionary containing the fee and priority options. If no matching option
    is found, it returns an error code.

    Parameters
    ----------
    options : list
        A list of payment options.
    priority : str, optional
        The priority of the payment (default is '48H').
    who_pays : str, optional
        The fee payer (default is 'OUR').

    Returns
    -------
    dict
        A dictionary containing the fee and priority options
    ERROR
        An error code (default is NO_ERROR)
    """
    
    error = error_exception.NO_ERROR
    option_returned = {}
    
    result = [option for option in options if option["priorityPaymentOption"] == priority.upper() and option['feePaymentOption'] == who_pays][0]
    if not options:
        logger.error("No priorities found between the two accounts")
        error = error_exception.ERROR_NO_PRIORITY
    if not result:
        logger.error(f"Priority {priority} and fee payer {who_pays} not found in options: {options}")
        error = error_exception.ERROR_PRIORITIES_FOUND_BUT_NOT_WHAT_ENTER
        
    else:
        option_returned = {
            "feePaymentOption": result["feePaymentOption"],
            "feeValue": result["feeCost"]["value"],
            "feeCurrency": result["feeCost"]['currency']
        }
    return option_returned, error