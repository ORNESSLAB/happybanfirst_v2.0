import logging
import re
import pandas as pd
import json
from pprint import pprint
from datetime import datetime
from orness import utils
from ibanfirst_client.api.auth_api import AuthApi
from ibanfirst_client.api_client import ApiClient
from ibanfirst_client.api.wallets_api import WalletsApi
from ibanfirst_client.api.payments_api import PaymentsApi
from ibanfirst_client.api.external_bank_account_api import ExternalBankAccountApi
from ibanfirst_client.api.financial_movements_api import FinancialMovementsApi
from ibanfirst_client.rest import ApiException
from orness.config import Config
from orness.auth import Authentication
from orness import error_exception
from orness.mapping import Mapping
import re




logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


    
class OrnessSDK:
    """
    OrnessSDK class to interact with the iBanFirst API.
    
    """
    def __init__(self, host="https://sandbox.ibanfirst.com/api"):
        self.config = Config()
        self.config.host = host
        self.auth = None

    def login(self, username, password) -> None:
        """
        Login to the iBanFirst API with the given credentials.
        """
        self.auth = Authentication(username=username, password=password)
    
    def api_client(self):
        """
        Creates and returns an instance of the ApiClient with the necessary authentication headers.

        Returns:
            ApiClient: Configured API client instance for making requests.
        """
        api_client = ApiClient(configuration=self.config)
        api_client.default_headers = self.auth.header()
        return api_client
        
    def get_nonce_token(self):
        """
        Get the nonce token from the authentication header.
        """
        
        return re.search(r'Nonce="([^"]*)"', self.auth.header()["X-WSSE"]).group(1)
        
    def get_wallets(self) -> list:
        """
        Retrieve a list of wallets.

        :return: A list of wallets
        """
        try:
            api_client = self.api_client()
            wallets_api = WalletsApi(api_client)
            return wallets_api.wallets_get(_preload_content=False).json()['wallets']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")
        return []

    def get_wallet_by_id(self, wallet_id) -> dict:
        """
        Retrieve wallet information by id.

        :param wallet_id: The id of the wallet
        :return: A dictionary containing details of the wallet
        """
        try:
            api_client = self.api_client()
            wallet_api = WalletsApi(api_client)
            return wallet_api.wallets_id_get(id=wallet_id, _preload_content=False).json()['wallet']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")
        return {}

    def get_payments_status(self, status) -> dict:
        """
        Retrieves a list of payments with the given status.

        Args:
            status (str): The status of the payments to retrieve.

        Returns:
            dict: A dictionary containing the list of payments.
        """
        try:
            api_client = self.api_client()
            payments_api = PaymentsApi(api_client)
            return payments_api.payments_status_get(status=status, _preload_content=False).json()
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")
        return {}
 
    def payload(self, excel_data_filename:str):
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
        json_data_from_excel = utils.read_data_from_file(excel_data_filename)
        for data in json_data_from_excel:
            if data['Sender'] == 'Name':
                line += 1
                continue
            payment_submit, errors = Mapping(self.get_wallets_holder_info(), self.get_external_bank_account_info()).mapping_payment_submit(data)
            if payment_submit:
                options= self.retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
                properties, opt_errors  = utils.get_payment_fee_and_priority(priority=payment_submit["priorityPaymentOption"], options=options)

                if opt_errors:
                    payload_returned["ERROR"].append((opt_errors, f"Line-{line}"))
                    continue
                payment_submit["feePaymentOption"] = properties['feePaymentOption']
                payment_submit["feeCurrency"] = properties['feeCurrency']
                payload_returned['payment'].append(payment_submit)
                payload_returned["ERROR"].append((errors, f"Line-{line}"))
            else:
                payload_returned["ERROR"].append((errors,f"Line-{line}"))

            line += 1
        return payload_returned
    
    def post_mass_payment(self, excel_data_filename: str) -> tuple:

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
                logger.error("Error in the file: %s", er)
                flag = 0
                return post_payment_response, error
        if flag == 1:
            for val in payment_sub:               
                if isinstance(val, dict):
                    try:
                        post_payment_response.append(self.post_payment(val))  
                    except ApiException as e:
                        logger.error(f"Error [postpay]: {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")         
                     
        return post_payment_response, error
    
    def post_payment(self, payload):
        """
        post payement submit on
        """
        
        val = payload
        
        api_client = self.api_client()
        payments_api = PaymentsApi(api_client)
        return payments_api.payments_post(body=val, _preload_content=False).json()
        
    def retreive_option_list(self, external_id:str, wallet_id:str) -> list:
        """Retreive list of fee options between wallet and external bank account

        Parameters
        ----------
        external_id : str
            The external bank account id
        wallet_id : str
            The wallet id

        Returns
        -------
        list
            A list of fee options
        """
        try:
            api_client = self.api_client()
            payments_api = PaymentsApi(api_client)
            if self.check_if_external_bank_account_exist(external_bank_account_id=external_id) and self.check_if_wallet_exist(wallet_id=wallet_id):
                return payments_api.payments_options_wallet_id_external_bank_account_id_get(external_bank_account_id=external_id, wallet_id=wallet_id, _preload_content=False).json()['paymentOption']['options']
            
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
        return []
    
    def check_if_wallet_exist(self, wallet_id):
        """Check if the wallet exists

        Parameters
        ----------
        wallet_id : str
            The wallet id

        Returns
        -------
        bool
            True if the wallet exists, False otherwise
        """

        return self.get_wallet_by_id(wallet_id=wallet_id) != {}
    
    

    def check_if_external_bank_account_exist(self, external_bank_account_id) -> bool:
        """Check if the external bank account exists

        Parameters
        ----------
        external_bank_account_id : str
            The external bank account id

        Returns
        -------
        bool
            True if the external bank account exists, False otherwise
        """
        
        return  self.get_external_bank_account_by_id(external_id=external_bank_account_id) != {}
    

    def get_wallets_holder_info(self) -> list: 
        """
        Return a list of wallets with their id, amountValue, amountCurrency and info of the holder
        """
        list_of_wallet_by_id = [{"id": i['id'], 
                                 "amountValue": i["bookingAmount"]["value"], 
                                 'amountCurrency': i["bookingAmount"]["currency"]} for i in self.get_wallets()]
        list_of_wallet_info = [{'id': i['id'], 
                    'holderName': self.get_wallet_by_id(wallet_id=i['id'])['holder']['name'], 
                    'holderIBAN': self.get_wallet_by_id(wallet_id=i['id'])['accountNumber'], 
                    'holderBankBic': self.get_wallet_by_id(wallet_id=i['id'])['holderBank']['bic'], 
                    "amountValue": i["amountValue"], 'amountCurrency': i["amountCurrency"] } for i in list_of_wallet_by_id]


        return list_of_wallet_info  
    
    def get_external_bank_account_by_id(self, external_id) -> dict:
        """
        Retrieve external bank account information by id.

        :param external_id: The id of the external bank account
        :return: A dictionary containing details of the external bank account
        """
        try:
            api_client = self.api_client()
        
            external_bank_account_api = ExternalBankAccountApi(api_client)
            return external_bank_account_api.external_bank_accounts_id_get(id=external_id, _preload_content=False).json()['account']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

        
    def get_external_bank_accounts(self) -> list:
        """
        Return a list of external bank accounts
        Parameters
        ----------
        None

        Returns
        -------
        list
            A list of external bank accounts
        """
        try:
            api_client = self.api_client()
            external_bank_account_api = ExternalBankAccountApi(api_client)
            return external_bank_account_api.external_bank_accounts_get(_preload_content=False).json()['accounts']
        except ApiException as e:
            logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

    
    def get_external_bank_account_info(self):
        """
        Retrieve external bank account information.
        

        Returns:
            list: A list of dictionaries, each containing details of an external bank account, 
                  including 'id', 'holderName', 'holderBankBic', 'holderIBAN', and 'currency'.
        """
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
    

    
