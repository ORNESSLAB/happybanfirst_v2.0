import json
import logging

import os
import sys
import pprint
import inspect

import traceback
from orness import error_exception as  errorExceptions
import pandas as pd
from orness import mappings
from ibanfirst_client.rest import ApiException
from orness.orness_api import IbExternalBankAccountApi
from orness.orness_api import IbWalletApi
from orness.orness_api import IbPaymentsApi
import re
from dotenv import load_dotenv, dotenv_values, set_key
from orness.cache import RedisCache

load_dotenv()

#TODO: verifier que le wallet a bien assez d'argent
#TODO: verifier les option de frais entre deux contreparties (counterparty)
#TODO: si l'external bank account n'existe pas, demander d'en ajouter 
#TODO: pour les resutat des paiement, creer un mappage pour les options
#TODO: creer une fonction qui confirme le paiement
#TODO: creer une fonction qui annule le paiement


rd = RedisCache()
#rd.clear()

logger = logging.getLogger(__name__)

def get_wallets():
    """
    Retrieve the list of all wallets.

    This function uses the IbWalletApi to fetch and return a list of all wallet accounts held with IBANFIRST.

    :return: A JSON object containing a list of all wallets.
    """
    logger.debug("Get wallets list")
    try:
        api = IbWalletApi()
        return api.wallets_get().json()
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'\"ErrorMessage\"\s*:\s*\"(.*)\"', str(e.body))}")

def get_wallet_id(id):
    """
    Retrieve wallet details by ID.

    This function uses the IbWalletApi to fetch and return the details of a wallet
    associated with the given wallet ID.

    :param id: The ID of the wallet to retrieve.
    :return: A JSON object containing the wallet details.
    """
    try:
        api = IbWalletApi()
        return api.wallets_id_get(id).json()
    except ApiException as e:
        logger.error(pprint.pprint(e.reason))
    


def read_data_from_file(filename):
    """
    Read the excel file and return the content in a json format.

    Parameters:
        filename (str): name of the excel file to read

    Returns:
        dict: the content of the excel file in json format
    """
    exc = pd.read_excel(filename).dropna(how='all')
    
    exc['Date d’exécution'] = pd.to_datetime(exc['Date d’exécution'], errors="coerce").dt.strftime('%Y-%m-%d')
    myjson = json.loads(exc.to_json(orient='records')) #convert str to dict
    
    return myjson

def get_payment_fee_and_priority(options: list, priority: str, who_pays:str = "OUR") -> dict:
        
     
        """
        Given a list of options and a priority, return the feePaymentOption, feeValue and feeCurrency associated with the given priority.

        Parameters:
            options (list): list of options
            priority (str): priority to look for

        Returns:
            dict: a dictionary containing the feePaymentOption, feeValue and feeCurrency associated with the given priority
        """
        frame = inspect.currentframe()
        func = frame.f_code.co_name
        try:
            
            if not options:
                logger.error(f"No priorities found between the two accounts")
                raise errorExceptions.NoPriorityError("No links between both accounts found")
            if [option for option in options if option["priorityPaymentOption"] == priority.upper() and option['feePaymentOption'] == who_pays] == []:
                
                logger.error(f"Priority {priority} and fee payer {who_pays} not found in options: {options}")
                raise errorExceptions.PriorityError("Priority not found")
                
            else:
                result = [option for option in options if option["priorityPaymentOption"] == priority.upper()]
                return {
                    
                    "feePaymentOption": result[0]["feePaymentOption"],
                    "feeValue": result[0]["feeCost"]["value"],
                    "feeCurrency": result[0]["feeCost"]['currency']
                }

        except errorExceptions.NoPriorityError as e:
            logger.error(f"Error {func}: {e}")
            traceback.print_exc()
            return errorExceptions.ERROR_NO_PRIORITY
          
        except errorExceptions.PriorityError as e:
            logger.error(f"Error {func}: {e}")
            traceback.print_exc()
            return errorExceptions.ERROR_PRIORITY
        
        except TypeError as e:
            logger.error(f"Error {func}: {e}")

def payload(excel_data_filename:str):
    #if we want to ask the user to select the priority option
    payload_returned = []
    
    json_data_from_excel = read_data_from_file(excel_data_filename)
    for data in json_data_from_excel:
        if data['Expéditeur'] == 'Titulaire':
            continue
        payment_submit = mappings.mapping_payment_submit_v2(data)
        if not payment_submit['externalBankAccountId']:
            logger.error(f'Recipient IBAN {payment_submit['externalBankAccountId']} -> has not been entered')
            continue
        if not payment_submit['sourceWalletId']:
            logger.error(f'Issuing Account IBAN {payment_submit['externalBankAccountId']} has not been given')
            continue
        if not check_account_value(wallet_id=payment_submit['sourceWalletId'], amount=float(payment_submit['amount']['value'])):
            logger.error(f'Insufficient funds in the account {payment_submit['sourceWalletId']}')
            continue
        #payload_returned.append(payload_dict(payment_submit))
        # Get fee priority Payment Options
        options = retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
        logger.debug(f"Build the JSON body for payment operation with {payment_submit['externalBankAccountId']} and {payment_submit['sourceWalletId']}")
        properties = get_payment_fee_and_priority(priority=payment_submit["priorityPaymentOption"], options=options)
        
        if properties == errorExceptions.ERROR_PRIORITY or properties == errorExceptions.ERROR_NO_PRIORITY or properties == errorExceptions.ERROR_FUNDS:
            continue
        
        payment_submit["feePaymentOption"] = properties['feePaymentOption']
        payment_submit["feeCurrency"] = properties['feeCurrency']
        payload_returned.append(payment_submit)
    return payload_returned
def payload_dict(data:dict):
    
    """
    Take a dict data as parameter and return a dict that will be used to create a payment operation
    
    data should contain the following keys:
        - externalBankAccountId: str
        - sourceWalletId: str
        - amount: dict
            - value: str
            - currency: str
        - desiredExecutionDate: str
        - feeCurrency: str
        - feePaymentOption: str
        - priorityPaymentOption: str
        - tag: str
        - communication: str
        
    if the account of sourceWalletId does not have enough funds, raise a NoFund exception
    if the priorityPaymentOption is not found in the options, raise a PriorityError exception
    """
    payment_submit = mappings.mapping_payment_submit(data)
    if not check_account_value(wallet_id=payment_submit['sourceWalletId'], amount=float(payment_submit['amount']['value'])):
            logger.error(f'Insufficient funds in the account {payment_submit['sourceWalletId']}')
            raise errorExceptions.NoFund("fund not enough")
            
    # Get fee priority Payment Options
    options = retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
    logger.debug(f"Build the JSON body for payment operation with {payment_submit['externalBankAccountId']} and {payment_submit['sourceWalletId']}")
    properties = get_payment_fee_and_priority(priority=payment_submit["priorityPaymentOption"], options=options)
    if properties == errorExceptions.ERROR_PRIORITY:
        return errorExceptions.ERROR_PRIORITY
    if properties == errorExceptions.ERROR_NO_PRIORITY:
        return errorExceptions.ERROR_NO_PRIORITY
    
    
    payment_submit["feePaymentOption"] = properties['feePaymentOption']
    payment_submit["feeCurrency"] = properties['feeCurrency']
    return payment_submit

def walletload(excel_data_filename: str) -> list:
    return [
        walletdump for data in read_data_from_file(excel_data_filename)
        if mappings.valid(
            json_data_to_check=(walletdump := mappings.mapping_wallets_submit(data)),
            json_schema_file_dir="orness/file/submit_wallet_schema.json"
        )
    ]

def post_payment(excel_data_filename: str) -> list:

    payment_submit = payload(excel_data_filename)
    post_payment_response = []
    
    
    for payment in payment_submit:
        try:
            
            
            
            if payment == errorExceptions.ERROR_FUNDS:
                continue
            if payment == errorExceptions.ERROR_PRIORITY:
                continue
            if payment_submit == errorExceptions.ERROR_NO_PRIORITY:
                continue
                        #logger.info("Start payment of {}".format(pprint.pprint(payment)))

            api = IbPaymentsApi()
            post_payment_response.append(api.payments_post(payment=payment).json())
                    
            
        except errorExceptions.PriorityError as e:
            logger.error(f"Error : {e}")
            traceback.print_exc()
            return errorExceptions.ERROR_PRIORITY
        except errorExceptions.NoFund as e:
            logger.error(f"Error : {e}")
            traceback.print_exc()
            return errorExceptions.ERROR_FUNDS
        except ApiException as e:
            logger.error(f"Error [postpay]: {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")

    return post_payment_response
    
def post_payment_from_form(form_data: dict):
    
    """
    Post a payment from form data.

    Args:
        form_data (dict): the form data to submit the payment

    Returns:
        dict: the response from the API
    """
    payment_submit = payload_dict(form_data)

    if mappings.valid(json_data_to_check=payment_submit, json_schema_file_dir="orness/file/submit_payment_schema.json"):
        return transfert(payment_to_submit=payment_submit)

   

def transfert(payment_to_submit:dict):
    
    """
    Make a payment using the provided payment information.
    
    The function will validate the payment information, then use the API
    to make the payment. The function will return the response from the API
    as a dictionary.
    
    If there is an error, the function will log the error and return
    an appropriate error code.
    
    """
    try:
        api = IbPaymentsApi()
        post_payment_response = api.payments_post(payment=payment_to_submit).json()
        return post_payment_response
    except ApiException as e:
        logger.error(f"Error  [postfromform]: {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
        return e.status

def create_wallets(excel_data_filename: str) -> list:
    
    try:
        wallets = walletload(excel_data_filename)
        for wallet in wallets:
            logger.debug(f"Create wallet {lwallet}")
            api = IbWalletApi()
            api.wallets_post(wallet=wallet)
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")

def retreive_option_list(wallet_id:str, external_id:str) -> list: 
    """
    Retrieve the list of options for a given wallet and external bank account.

    :param wallet_id: The id of the wallet
    :param external_id: The id of the external bank account
    :return: The list of options for the given wallet and external bank account
    """
    # print("Wallet id: ", wallet_id)
    # print("External id: ", external_id)
    try:
        api = IbPaymentsApi()
        if check_if_external_bank_account_exist(external_bank_account_id=external_id) and check_if_wallet_exist(wallet_id=wallet_id):
            return api.payments_options_wallet_id_external_bank_account_id_get(external_bank_account_id=external_id, wallet_id=wallet_id).json()['paymentOption']['options']
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
    

def check_if_wallet_exist(wallet_id: str) -> bool:
        """
        Check if a wallet exists on the API
        :param wallet_id: The id of the wallet to check
        :return: True if the wallet exists, False otherwise
        """
        try:
            return any(i['id'] == wallet_id for i in rd.get('wallets_info'))
        except ApiException as e:
            if e.status == 404:
                return False
            

def check_if_external_bank_account_exist(external_bank_account_id) -> bool:
    """
    Check if an external bank account exists on the API.

    :param external_bank_account_id: The ID of the external bank account to check.
    :return: True if the external bank account exists, False otherwise.
    """
    api = IbExternalBankAccountApi()
    try:
        return any(i['id'] == external_bank_account_id for i in rd.get('external_bank_accounts_info'))
    except ApiException as e:
        if e.status == 404: 
            return False
        
    
def get_payments_status(status="all"):
    logging.info("Get payments by status")
    try:
        api = IbPaymentsApi()
        
        payments = api.payments_status_get(status=status).json()
        
        return payments
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")

def get_payment_by_id(id):
    logging.info("Get payment by id")
    try:
        api = IbPaymentsApi()
        result = api.payments_id_get(id=id).json()
        logger.info(pprint.pprint(result))
        return result
    except ApiException as e:
        logger.error(pprint.pprint(e.reason))
        
def get_external_bank_account_id(id):
    logging.debug("Get external bank account by id")
    try:
        api = IbExternalBankAccountApi()
        result = api.external_bank_accounts_id_get(id=id).json()
        logger.debug(pprint.pprint(result))
        return result
    except ApiException as e:
        logger.error(pprint.pprint(e.reason))


def get_wallet_holder_info():
    logging.debug("Get holder info ")
    try:
        list_of_wallet_by_id = [{"id": i['id'], 
                                 "amountValue": i["bookingAmount"]["value"], 
                                 'amountCurrency': i["bookingAmount"]["currency"]} for i in get_wallets()['wallets'] ]
        list_of_wallet_info = [{'id': i['id'], 
                    'holderName': get_wallet_id(id=i['id'])['wallet']['holder']['name'], 
                    'holderIBAN': get_wallet_id(id=i['id'])['wallet']['accountNumber'], 
                    'holderBankBic': get_wallet_id(id=i['id'])['wallet']['holderBank']['bic'], 
                    "amountValue": i["amountValue"], 'amountCurrency': i["amountCurrency"] } for i in list_of_wallet_by_id]
       

        
        return list_of_wallet_info  
    except TypeError:
        logger.error("User not found")
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")

def get_external_bank_accounts():
    logger.debug("Get external bank accounts")
    try:
        api = IbExternalBankAccountApi()
        result = api.external_bank_accounts_get().json()
        return result
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")

def get_external_bank_account_info():
    logger.debug("Get external bank BICs")
    try:
        accounts = get_external_bank_accounts()
        
        list_info = [{'id': acc['id'], 'holderName': acc['holder']['name'], 'holderBankBic': acc['holderBank']['bic'], 'holderIBAN': acc['accountNumber'], 'currency': acc['currency']} for acc in accounts['accounts']]
        return list_info
    except TypeError:
        logger.error("User not found")
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
        

def confirm_paymet(id):
    api = IbPaymentsApi()
    logger.debug("Payment confirmed")
    return api.payments_id_confirm_put(id=id)

def delete_paymet(id):
    api = IbPaymentsApi()
    logger.debug("Payment deleted")
    return api.payments_id_delete(id=id)

def modify_env(key, value):
    variables = dotenv_values('.env')
    variables[key] = value
    for k, v in variables.items():
        set_key('.env', k, v)

def authentication(user_id, password):
    try:
        modify_env('IB_USERNAME', user_id)
        modify_env('IB_PASSWORD', password)
        check = get_wallet_holder_info()
        return f"{os.getenv('IB_USERNAME')} Connected! " if check[0]['id'] else "User not found"
    except TypeError:
        logger.error("User not found")
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")


def check_account_value(wallet_id:str, amount:float) -> bool:
    """
    Check if the wallet has enough money to make the payment.

    :param wallet_id: The id of the wallet
    :param amount: The amount of money to check
    :return: True if the wallet has enough money, False otherwise
    """
    try:
        # for i in rd.get('wallets_info'):
        #     if i['id'] == wallet_id and float(i['amountValue']) >= amount:
        #         print("les founds : ", i['id'], wallet_id, i['amountValue'], amount)
        #         return True
        return any(i['id'] == wallet_id and float(i['amountValue']) >= amount for i in rd.get('wallets_info'))
    except Exception as e:
            logger.error(e)
            return False


def create_beneficiary(data:dict):
    try:
        requete = json.loads(json.dumps(mappings.mapping_ben_creation(data), indent=2))
        test = mappings.valid(requete, "orness/file/create_beneficiary_schema.json")
        
        if test:
            api = IbExternalBankAccountApi()
            return api.external_bank_accounts_post(external_bank_account=requete)
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
        traceback.print_exc()
        return None


rd.set('external_bank_accounts_info', json.dumps(get_external_bank_account_info()))
rd.set('wallets_info', json.dumps(get_wallet_holder_info()))
rd.set('payments_histo', json.dumps(get_payments_status()['payments']))
rd.set('payments_planified', json.dumps(get_payments_status('planified')['payments']))

if __name__ == '__main__':
    file_a = 'new_payment.xlsx'
    file_b = 'new_payments_v2.xlsx'

    #print(post_payment(file_b))
    #print(get_wallets())
    #print(post_payment(file_a))
    #print(get_wallet_holder_info())
    #print(list_wallets_from_file(file_a))
    #retreive_option_list(wallet_id="", external_id="Njc1NzI")
    #print(check_if_external_bank_account_exist(external_bank_account_id="Njc1NzI"))
    #payload(file_a)
    kg={"Bénéficiaire": "10943409100132",
        "Expéditeur": "BE39914001921319",
        "Commentaire": "",
        "Libellé": "",
        "Montant": "14",
        "Date d’exécution": "2025-03-18",
        "Urgence": "48H",
        "Détails des frais": ""
    }

    jason2 = {'Priorité': '1H', 'Bénéficiaire': '314b065159e8e9c', 'Expéditeur': 'BE39914001921319', 'Commentaire': '', 'Libellé': '', 'Montant': '2', 'Date désirée': ''}
    ext = {
    "currency": "EUR",
    "tag": "mon extern",
    "accountNumber": "FR1130002005440000007765L61",
    "correspondentBankBic": "",
    "holderBank": {
        "bic": "CRLYFRPPXXX",
        "clearingCodeType": "",
        "clearingCode": "3000200561",
        "name": "LE CREDIT LYONNAIS",
        "address": {
            "street": "19 BOULEVARD DES ITALIENS",
            "postCode": "75002",
            "city": "paris",
            "country": "FR",
            "state": ""
        }
    },
    "holder": {
        "name": "Julien",
        "type": "corporate",
        "address": {
            "street": "21 rue du lac",
            "postCode": "21000",
            "city": "dijon",
            "country": "FR",
            "state": ""
        }
    }
}
    #authentication("mn11256", "61JyoSK8GW6q395cXJTy0RtuhaFpIaxJCiMRESAVjEAO5kXJ+h0XsGGRD3gJu/pRrJyrr6C5u8voxAzleA/k6g==")
    print(post_payment_from_form(kg))
    # print(rd.get('wallets_info'))
    #print(rd.get('payments_histo')[0]['sourceWalletId'])
    #print(check_account_value(wallet_id="OTg1OTE", amount=12))
    #print(rd.get('external_bank_accounts_info'))
    
    

    

    
