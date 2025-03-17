import logging
import re
import pandas as pd
import json
from pprint import pprint
from datetime import datetime
from orness import utils
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




logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


    
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
            payment_submit, ERRORS = Mapping(self.get_wallets_holder_info(), self.get_external_bank_account_info()).mapping_payment_submit_v2(data)
            if payment_submit:
                options= self.retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
                properties, OPT_ERROR  = utils.get_payment_fee_and_priority(priority=payment_submit["priorityPaymentOption"], options=options)

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

    
    
