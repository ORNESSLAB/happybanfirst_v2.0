import logging
import re
import pandas as pd
import json
from pprint import pprint
from datetime import datetime
from ibanfirst_client.api_client import ApiClient
from ibanfirst_client.api.wallets_api import WalletsApi
from ibanfirst_client.api.payments_api import PaymentsApi
from ibanfirst_client.api.external_bank_account_api import ExternalBankAccountApi
from ibanfirst_client.api.financial_movements_api import FinancialMovementsApi
from ibanfirst_client.rest import ApiException
from orness.config import Config
from orness.auth import Authentication
from orness import error_exception
from orness import error_exception as errorExceptions


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Mapping():
    """_summary_

    Parameters
    ----------
    wallet_list : _type_
        _description_
    beneficiary : _type_
        _description_
    """
    def __init__(self, wallet_list, beneficiary):
        
        
        self.wallets = wallet_list
        self.beneficiary = beneficiary
        self.recip_iban = 'Unnamed: 3'
        self.send_iban = 'Unnamed: 1'
    
    def max_value(self):
        return max([float(i["amountValue"]) for i in self.wallets])
    
    def number_of_same_object_holder_name(self, holder_name:str, objet) -> int:
   
        """
        The number of object accounts with the same holder name

        Parameters
        ----------
        holder_name : str
            The holder name
        object : str, optional
            The object to search in, by default 'external_bank_accounts_info'

        Returns
        -------
        int
            The number of external bank accounts or wallet with the same holder name
        """
        if objet == "wallets_info":
            return len([i for i in self.wallets if i['holderName'] == holder_name])
        elif objet == "external_bank_accounts_info":
            return len([i for i in self.beneficiary if i['holderName'] == holder_name])
        else:
            return 0
        
    def number_object_with_same_iban(self, iban:str, objet='external_bank_accounts_info'):
        """_summary_

        Args:
            name (str): _description_
            objet (str, required): _description_. choice: 'external_bank_accounts_info' 'wallets_info'.

        Returns:
            _type_: _description_
        """
        if objet == "wallets_info":
            return len([i for i in self.wallets     if      i['holderIBAN'] == iban])
        elif objet == "external_bank_accounts_info":
            return len([i for i in self.beneficiary if      i['holderIBAN'] == iban])
        else:
            return 0

    def choose_the_wallet(self,data):
        
        ERROR = error_exception.NO_ERROR
        source_Id=[]
        if not data.get('Sender') and not data.get(self.send_iban):
            if len(self.wallets) == 1:
                source_Id = [(k['id'], k['amountCurrency'], k["amountValue"]) for k in self.wallets ]
            elif len(self.wallets) > 1:
                ERROR = error_exception.SENDER_IBAN_NOT_PROVIDED
            return source_Id, ERROR

        if data.get('Sender') and not data.get(self.send_iban): 
            if self.number_of_same_object_holder_name(data.get('Sender'), objet="wallets_info") > 1:
                ERROR = error_exception.TOO_MUCH_SENDER_IBAN_FOUND
            elif self.number_of_same_object_holder_name(data.get('Sender'), objet="wallets_info") == 1:
                source_Id = [(k['id'], k['amountCurrency'], k["amountValue"]) for k in self.wallets  if k['holderName'] == data.get('Sender')]
                if source_Id[0][2] and float(source_Id[0][2]) > float(data['Amount']):
                    source_Id = source_Id
                else:
                    ERROR = error_exception.NOT_ENOUGH_FUND
            else:
                ERROR = error_exception.SENDER_NOT_RETREIVED + 1
            return source_Id, ERROR

        if not data.get('Sender') and data.get(self.send_iban):
            if self.number_object_with_same_iban(data.get(self.send_iban), objet="wallets_info") > 1:
                ERROR = error_exception.SENDER_NOT_RETREIVED
            elif self.number_object_with_same_iban(data.get(self.send_iban), objet="wallets_info") == 1:
                source_Id = [(k['id'], k['amountCurrency'], k["amountValue"]) for k in self.wallets  if k['holderIBAN'] == data.get(self.send_iban)]
                if source_Id[0][2] and float(source_Id[0][2]) > float(data['Amount']):
                    source_Id = source_Id
                else:
                    ERROR = error_exception.NOT_ENOUGH_FUND 
            else:
                ERROR = error_exception.SENDER_NOT_RETREIVED + 2
            return source_Id, ERROR
        
        if data.get('Sender') and data.get(self.send_iban):
            matching_wallets = [k for k in self.wallets if k['holderIBAN'] == data.get(self.send_iban) and k['holderName'] == data.get('Sender')]
            if len(matching_wallets) == 1:
                wallet = matching_wallets[0]
                
                if wallet.get('amountValue') and float(wallet['amountValue']) > float(data.get("Amount")):
                    source_Id = [(wallet['id'], wallet['amountCurrency'], wallet["amountValue"])]
                else:
                    ERROR = error_exception.NOT_ENOUGH_FUND
            else:
                ERROR = error_exception.SENDER_NOT_RETREIVED + 3
            return source_Id, ERROR

    def choose_beneficiary(self,data):
        ERROR = error_exception.NO_ERROR
        benef = []
        if not data[self.recip_iban] and not data['Recipient']:
            ERROR = error_exception.BENEFICIARY_NAME_AND_IBAN_NOT_PROVIDED
            return benef, ERROR
        if data[self.recip_iban] and data['Recipient']:
            benef = [(k['id'], k['currency']) for k in self.beneficiary  if k['holderName'] == data['Recipient'] and k['holderIBAN'] == data[self.recip_iban]]
            if not benef:
                ERROR = error_exception.NO_BENEFICIARY_FOUND
            return benef, ERROR
        if data['Recipient'] and not data[self.recip_iban]:
            if self.number_of_same_object_holder_name(holder_name=data['Recipient'], objet='external_bank_accounts_info') == 1:
                benef = [(k['id'], k['currency']) for k in self.beneficiary  if k['holderName'] == data['Recipient']]
            else:
                ERROR = error_exception.TOO_MUCH_BENEFICIARY_IBAN
            return benef, ERROR

        if data[self.recip_iban] and not data['Recipient']:
            if self.number_object_with_same_iban(iban=data[self.recip_iban], objet="external_bank_accounts_info") == 1:
                benef = [(k['id'], k['currency']) for k in self.beneficiary  if k['holderIBAN'] == data[self.recip_iban]]

            else:
                ERROR = error_exception.TOO_MUCH_BENEFICIARY_IBAN
            return benef, ERROR
    

    
    def mapping_payment_submit_v2(self, data:dict) -> dict:
        payment_submit = {}
        #TODO: check the amount currency
        #TODO: check wallet holder name
        #TODO: check beneficiary holder name
        #TODO: return error value

        
        external_Id, BENEFICIARY_ERROR = self.choose_beneficiary(data)
        source_Id, SOURCE_ERROR = self.choose_the_wallet(data=data)
        logger.debug(f" Recipient ID: {external_Id} and Sender ID: {source_Id}")
        if not source_Id or not external_Id:
            return payment_submit, {"SOURCE_ERROR":SOURCE_ERROR, "BENEFICIARY_ERROR":BENEFICIARY_ERROR, "ERROR_CURRENCY": error_exception.NO_ERROR, "AMOUNT_ERROR": error_exception.NO_ERROR}
        if not data['Amount']:
            return payment_submit, {"SOURCE_ERROR":SOURCE_ERROR, "BENEFICIARY_ERROR":BENEFICIARY_ERROR, "AMOUNT_ERROR": error_exception.AMOUNT_NOT_PROVIDED, "ERROR_CURRENCY": error_exception.NO_ERROR}

        
        if external_Id[0][1] == data["Currency"] or not data["Currency"]:
            payment_submit['externalBankAccountId'] = external_Id[0][0]
            payment_submit['sourceWalletId'] = source_Id[0][0]
            date_execution = date_format(date=data['Execution date'])
            payment_submit['amount'] = {'value':data['Amount'], 'currency': external_Id[0][1]}
            payment_submit['desiredExecutionDate'] = date_execution 
            payment_submit['priorityPaymentOption'] = data['Priority'] if data['Priority'] else '24H' #data['priorite']
            payment_submit['feeCurrency'] = source_Id[0][1]
            if data['Fees option']:
                if data['Fees option'].upper() == "CLIENT":
                    payment_submit['feePaymentOption'] = 'OUR'
                if data['Fees option'].upper() == "recipient".upper():
                    payment_submit['feePaymentOption'] = 'BEN'
                if data['Fees option'].upper() == "share".upper():
                    payment_submit['feePaymentOption'] = 'SHARE'
            else:
                payment_submit['feePaymentOption'] = "OUR"
            payment_submit['tag'] = data['Description'] if data['Description'] else ''
            payment_submit['communication'] = data['Comment'] if data['Comment'] else ''
            return payment_submit, {"SOURCE_ERROR":SOURCE_ERROR, "BENEFICIARY_ERROR":BENEFICIARY_ERROR, "ERROR_CURRENCY": error_exception.NO_ERROR, "AMOUNT_ERROR": error_exception.NO_ERROR}
        else:
            return payment_submit, {"SOURCE_ERROR":SOURCE_ERROR, "BENEFICIARY_ERROR":BENEFICIARY_ERROR, "ERROR_CURRENCY": error_exception.CURRENCY_NOT_THE_SAME_BETWEEN_SENDER_AND_BEN, "AMOUNT_ERROR": error_exception.NO_ERROR}
        
    
class OrnessSDK:
    def __init__(self):
        self.config = Config()
        self.auth = None

    def login(self, username, password):
        self.auth = Authentication(username=username, password=password)
        
    
    def api_client(self):
        api_client = ApiClient(configuration=self.config)
        api_client.default_headers = self.auth.header()
        return api_client
    
  

    def get_wallets(self):
        try:
            api_client = self.api_client()
            wallets_api = WalletsApi(api_client)
            return wallets_api.wallets_get(_preload_content=False).json()['wallets']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

    def get_wallet_by_id(self, wallet_id):
        try:
            api_client = self.api_client()
            wallet_api = WalletsApi(api_client)
            return wallet_api.wallets_id_get(id=wallet_id, _preload_content=False).json()['wallet']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

    def get_payments_status(self, status):
        try:
            api_client = self.api_client()
            payments_api = PaymentsApi(api_client)
            return payments_api.payments_status_get(status=status, _preload_content=False).json()
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

    

    
    def payload(self, excel_data_filename:str):
        #if we want to ask the user to select the priority option
        """
        Process payment data from an Excel file and prepare a payload for payment operations.
    
        This function reads payment data from an Excel file, processes each entry to create 
        a payment submission, and retrieves the necessary fee and priority options for each 
        payment. It also handles errors encountered during processing.
    
        Parameters
        ----------
        excel_data_filename : str
            The path to the Excel file containing payment data to be processed.
    
        Returns
        -------
        dict
            A dictionary with two keys:
            - 'payment': A list of successfully processed payment submissions.
            - 'ERROR': A list of errors encountered, each associated with the line number 
              in the Excel file.
        """

        payload_returned = {"payment":[], "ERROR":[]}
        line = 0
        json_data_from_excel = read_data_from_file(excel_data_filename)
        for data in json_data_from_excel:
            if data['Sender'] == 'Name':
                line += 1
                continue
            payment_submit, ERRORS = Mapping(self.get_wallets_holder_info(), self.get_external_bank_account_info()).mapping_payment_submit_v2(data)
            if payment_submit:
                options= self.retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
                properties, OPT_ERROR  = get_payment_fee_and_priority(priority=payment_submit["priorityPaymentOption"], options=options)

                if OPT_ERROR:
                    payload_returned["ERROR"].append((OPT_ERROR, f"Line-{line}"))
                    continue
                payment_submit["feePaymentOption"] = properties['feePaymentOption']
                payment_submit["feeCurrency"] = properties['feeCurrency']
                payload_returned['payment'].append(payment_submit)
                payload_returned["ERROR"].append((ERRORS, f"Line-{line}"))
            else:
                payload_returned["ERROR"].append((ERRORS,f"Line-{line}"))

            line += 1
        return payload_returned
    
    def post_payment(self, excel_data_filename: str) -> list:

        """
        Read the excel file and for each line, call the payload function to construct the payment JSON body.
        If there is an error in the file, return the list of errors
        If there is no error, call the post payment API for each payment and return the list of response

        Parameters
        ----------
        excel_data_filename : str
            The path of the excel file containing the payments to be done

        Returns
        -------
        list
            A list of payments response
        list
            A list of errors
        """
        load_pay = self.payload(excel_data_filename)
        payment_sub = load_pay['payment']
        error = load_pay['ERROR']
        flag = 0
        post_payment_response = []

        for er in error:
            if er[0]['SOURCE_ERROR'] == er[0]['BENEFICIARY_ERROR'] == er[0]['ERROR_CURRENCY']:
                flag = 1
            else:
                logger.error(f"Error in the file: {er}")
                flag = 0
                return post_payment_response, error
        if flag == 1:
            for val in payment_sub:               
                if isinstance(val, dict):

                    try:
                        api_client = self.api_client()
                        payments_api = PaymentsApi(api_client)
                        post_payment_response.append(payments_api.payments_post(body=val, _preload_content=False).json())         
                    except ApiException as e:
                        logger.error(f"Error [postpay]: {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")   
        return post_payment_response, error
    
    def retreive_option_list(self, external_id:str, wallet_id:str):
        try:
            api_client = self.api_client()
            payments_api = PaymentsApi(api_client)
            if self.check_if_external_bank_account_exist(external_bank_account_id=external_id) and self.check_if_wallet_exist(wallet_id=wallet_id):
                return payments_api.payments_options_wallet_id_external_bank_account_id_get(external_bank_account_id=external_id, wallet_id=wallet_id, _preload_content=False).json()['paymentOption']['options']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
    
    def check_if_wallet_exist(self, wallet_id):
        return True if self.get_wallet_by_id(wallet_id=wallet_id) else False
    
    
    def check_if_external_bank_account_exist(self, external_bank_account_id):
        
        return True if self.get_external_bank_account_by_id(external_id=external_bank_account_id) else False
    

    def get_wallets_holder_info(self):
        list_of_wallet_by_id = [{"id": i['id'], 
                                 "amountValue": i["bookingAmount"]["value"], 
                                 'amountCurrency': i["bookingAmount"]["currency"]} for i in self.get_wallets()]
        list_of_wallet_info = [{'id': i['id'], 
                    'holderName': self.get_wallet_by_id(wallet_id=i['id'])['holder']['name'], 
                    'holderIBAN': self.get_wallet_by_id(wallet_id=i['id'])['accountNumber'], 
                    'holderBankBic': self.get_wallet_by_id(wallet_id=i['id'])['holderBank']['bic'], 
                    "amountValue": i["amountValue"], 'amountCurrency': i["amountCurrency"] } for i in list_of_wallet_by_id]


        return list_of_wallet_info  
    
    def get_external_bank_account_by_id(self, external_id):
        try:
            api_client = self.api_client()
        
            external_bank_account_api = ExternalBankAccountApi(api_client)
            return external_bank_account_api.external_bank_accounts_id_get(id=external_id, _preload_content=False).json()['account']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

        
    def get_external_bank_accounts(self):
        try:
            api_client = self.api_client()
            external_bank_account_api = ExternalBankAccountApi(api_client)
            return external_bank_account_api.external_bank_accounts_get(_preload_content=False).json()['accounts']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

    
    def get_external_bank_account_info(self):
        accounts = self.get_external_bank_accounts()
        list_info = [{'id': acc['id'], 
                      'holderName': acc['holder']['name'], 
                      'holderBankBic': acc['holderBank']['bic'], 
                      'holderIBAN': acc['accountNumber'], 
                      'currency': acc['currency']} for acc in accounts]
        return list_info
   
    def check_account_value(self,wallet_id: str, amount:float) -> bool:
        """
        Check if the wallet has enough money to make the payment.

        :param wallet_id: The id of the wallet
        :param amount: The amount of money to check
        :return: True if the wallet has enough money, False otherwise
        """
        
        return any(i['id'] == wallet_id and float(i['amountValue']) >= amount for i in self.get_wallets_holder_info())
    
    

def generate_api_with_default_header(conf):
    """
    Creates an ApiClient instance with a default header.

    This function initializes an ApiClient instance with configuration
    settings from the Config class. It then retrieves the header from the
    configuration and sets the 'X-WSSE' header for the ApiClient. Finally,
    it returns the configured ApiClient instance.

    :return: An ApiClient instance with the 'X-WSSE' header set.
    :rtype: ApiClient
    """

    API = ApiClient(configuration=conf)
    header = API.configuration.get_header()
    API.set_default_header('X-WSSE', header['X-WSSE'])
    return API

def read_data_from_file(filename):
    """
    Read the excel file and return the content in a json format.

    Parameters:
        filename (str): name of the excel file to read

    Returns:
        dict: the content of the excel file in json format
    """
    exc = pd.read_excel(filename).dropna(how='all')
    
    exc['Execution date'] = pd.to_datetime(exc['Execution date'], errors="coerce").dt.strftime('%Y-%m-%d')
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
    
    ERROR = errorExceptions.NO_ERROR
    option_returned = {}
    
    result = [option for option in options if option["priorityPaymentOption"] == priority.upper() and option['feePaymentOption'] == who_pays][0]
    if not options:
        logger.error(f"No priorities found between the two accounts")
        ERROR = errorExceptions.ERROR_NO_PRIORITY
    if not result:
        logger.error(f"Priority {priority} and fee payer {who_pays} not found in options: {options}")
        ERROR = errorExceptions.ERROR_PRIORITIES_FOUND_BUT_NOT_WHAT_ENTER
        
    else:
        option_returned = {
            "feePaymentOption": result["feePaymentOption"],
            "feeValue": result["feeCost"]["value"],
            "feeCurrency": result["feeCost"]['currency']
        }
    return option_returned, ERROR

def date_format(date):
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

if __name__ == "__main__":
    from pprint import pprint
    
    file = "new_payments_v2.xlsx"
    sdk = OrnessSDK()
    sdk.login(password="61JyoSK8GW6q395cXJTy0RtuhaFpIaxJCiMRESAVjEAO5kXJ+h0XsGGRD3gJu/pRrJyrr6C5u8voxAzleA/k6g==", username="mn11256")
    pprint(sdk.auth.header())
    pprint(sdk.auth.header())
    #pprint(sdk.post_payment(file))
    # pprint(sdk.get_payments_status('all'))
    #pprint(sdk.get_wallets_holder_info())
    pprint(type(sdk.get_external_bank_account_info()))
    #pprint(sdk.get_external_bank_account_by_id(""))
    #pprint(sdk.check_if_external_bank_account_exist("MTc3Njcy"))

    
    
