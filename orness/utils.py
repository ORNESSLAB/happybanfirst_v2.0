import json
import logging
from math import e, log
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
    exc = pd.read_excel(filename)
    exc['Date désirée'] = pd.to_datetime(exc['Date désirée'], unit='d').dt.strftime('%Y-%m-%d')
    myjson = json.loads(exc.to_json(orient='records')) #convert str to dict
    
    return myjson

def get_payment_fee_and_priority(options: list, priority: str) -> dict:
        
        """
            Takes a list of options and a priority and returns the options that match the given priority.

            Parameters
            ----------
            options : list
                A list of dictionaries containing the payment options
            priority : str
                The priority to filter the options by

            Returns
            -------
            list
                A list of dictionaries containing the payment options that match the given priority
        """
        frame = inspect.currentframe()
        func = frame.f_code.co_name
        try:
            
            if not options:
                logger.error(f"No priorities found between the two accounts")
                raise errorExceptions.NoPriorityError("No priorities found")
            if [option for option in options if option["priorityPaymentOption"] == priority.upper()] == []:
                
                logger.error(f"Priority {priority} not found in options: {options}")
                raise errorExceptions.PriorityError("Priority not found")
                
            else:
                result = [option for option in options if option["priorityPaymentOption"] == priority.upper()]
                print("type de Result: {func}", type(result) , "taille de result: ", result)
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
    try:
        json_data_from_excel = read_data_from_file(excel_data_filename)
        for data in json_data_from_excel:
            payment_submit = mappings.mapping_payment_submit(data)

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
            
            if properties == errorExceptions.ERROR_PRIORITY:
                continue
            elif not properties:
                continue
            else:
                payment_submit["feePaymentOption"] = properties['feePaymentOption']

            # Serialize and validate JSON
            try:
                dump = json.loads(json.dumps(payment_submit, indent=2))
                if mappings.valid(json_data_to_check=dump, json_schema_file_dir="orness/file/submit_payment_schema.json"):
                    payload_returned.append(dump)
                else:
                    logger.error("JSON format is not valid")
            except (TypeError, json.JSONDecodeError) as e:
                logger.error(f"Error processing JSON: {e}")

    except TypeError as e:
        logger.error(f"Error : {e}")
        traceback.print_exc()
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
        traceback.print_exc()
    logger.debug(f'payload_returned: {pprint.pprint(payload_returned)}')

    return payload_returned
def payload_dict(data:dict):
    frame = inspect.currentframe()
    func = frame.f_code.co_name
    
    payment_submit = mappings.mapping_payment_submit(data)
    print("Fund: ",check_account_value(wallet_id=payment_submit['sourceWalletId'], amount=float(payment_submit['amount']['value'])))

    try:
        if not check_account_value(wallet_id=payment_submit['sourceWalletId'], amount=float(payment_submit['amount']['value'])):
                logger.error(f'Insufficient funds in the account {payment_submit['sourceWalletId']}')
                raise errorExceptions.NoFund("fund not enough")
                
        # Get fee priority Payment Options
        options = retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
        logger.debug(f"Build the JSON body for payment operation with {payment_submit['externalBankAccountId']} and {payment_submit['sourceWalletId']}")
        properties = get_payment_fee_and_priority(priority=payment_submit["priorityPaymentOption"], options=options)
        if properties == errorExceptions.ERROR_PRIORITY:
            raise errorExceptions.PriorityError("priority not found")
        elif properties == errorExceptions.ERROR_NO_PRIORITY:
            raise errorExceptions.NoPriorityError("there is no priority found between the two accounts")
        else:
            payment_submit["feePaymentOption"] = properties['feePaymentOption']

                # Serialize and validate JSON
        try:
            dump = json.loads(json.dumps(payment_submit, indent=2))
            if mappings.valid(json_data_to_check=dump, json_schema_file_dir="orness/file/submit_payment_schema.json"):
                return dump
            else:
                logger.error("JSON format is not valid")
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error processing JSON: {e}")
    except errorExceptions.NoPriorityError as e:
        logger.error(f"Error {func}: {e}")
        traceback.print_exc()
        return errorExceptions.ERROR_NO_PRIORITY

    except errorExceptions.PriorityError as e:
        logger.error(f"Error {func}: {e}")
        traceback.print_exc()
        return errorExceptions.ERROR_PRIORITY
    except errorExceptions.NoFund as e:
        logger.error(f"Error  {func}: {e}")
        traceback.print_exc()
        return errorExceptions.ERROR_FUNDS
    except TypeError as e:
        logger.error(f"Error {func}: {e}")
        traceback.print_exc()
      
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
        traceback.print_exc()



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
    
    try:
        for payment in payment_submit:
            post_payment_response.append(post_payment_from_form(payment))
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
    # try:
        
    #     for payment in payment_submit:
    #         if payment == errorExceptions.ERROR_FUNDS:
    #             raise errorExceptions.NoFund("funds not enough")
    #         if payment == errorExceptions.ERROR_PRIORITY:
    #             raise errorExceptions.PriorityError("priority not found")
    #                 #logger.info("Start payment of {}".format(pprint.pprint(payment)))

    #         api = IbPaymentsApi()
    #         post_payment_response.append(api.payments_post(payment=payment).json())
                
    #     return post_payment_response
    # except errorExceptions.PriorityError as e:
    #     logger.error(f"Error : {e}")
    #     traceback.print_exc()
    #     return errorExceptions.ERROR_PRIORITY
    # except errorExceptions.NoFund as e:
    #     logger.error(f"Error : {e}")
    #     traceback.print_exc()
    #     return errorExceptions.ERROR_FUNDS
    # except ApiException as e:
    #     logger.error(f"Error [postpay]: {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")

    return post_payment_response
    
def post_payment_from_form(form_data: dict) -> list:
    frame = inspect.currentframe()
    func = frame.f_code.co_name
    payment_submit = payload_dict(form_data)
    print("Payment submit: ", payment_submit)

    try:
        if payment_submit == errorExceptions.ERROR_FUNDS:
            raise errorExceptions.NoFund("funds not enough")
        if payment_submit == errorExceptions.ERROR_PRIORITY:
            raise errorExceptions.PriorityError("priority not found")
        if payment_submit == errorExceptions.ERROR_NO_PRIORITY:
            raise errorExceptions.NoPriorityError("no priority found between the two accounts")
            
        
        api = IbPaymentsApi()
        post_payment_response = api.payments_post(payment=payment_submit).json()
        return post_payment_response
    
    except errorExceptions.NoPriorityError as err1:
        logger.error(f"Error :{func} {err1}")
        traceback.print_exc()
        return errorExceptions.ERROR_NO_PRIORITY
    
    except errorExceptions.PriorityError as err2:
        logger.error(f"Error [{func}]: {err2}")
        traceback.print_exc()
        return errorExceptions.ERROR_PRIORITY
    except errorExceptions.NoFund as err3:
        logger.error(f"Error [{func}]: {err3}")
        traceback.print_exc()
        return errorExceptions.ERROR_FUNDS
    except ApiException as e:
        logger.error(f"Error  [postfromform]: {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")
    

def create_wallets(excel_data_filename: str) -> list:
    
    try:
        wallets = walletload(excel_data_filename)
        for wallet in wallets:
            logger.debug(f"Create wallet {log.display_format_data(wallet)}")
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
    print("Wallet id: ", wallet_id)
    print("External id: ", external_id)
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
        list_info = [{'id': acc['id'], 'holderName': acc['holder']['name'], 'holderBankBic': acc['holderBank']['bic'], 'holderIBAN': acc['accountNumber']} for acc in accounts['accounts']]
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


def create_external_bank_account(data: dict) -> dict:
    """
    Create an external bank account.

    This function uses the IbExternalBankAccountApi to create a new external bank account.

    :param data: A dictionary containing the details of the external bank account to create.
    :return: A dictionary containing the details of the newly created external bank account.
    """
    try:
        api = IbExternalBankAccountApi()
        return api.external_bank_accounts_post(external_bank_account=data).json()
    except ApiException as e:
        logger.error(f"Error : {e.status}\n{e.reason} - {re.search(r'"ErrorMessage":\B"(.*)\B",', str(e.body))}")



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
def number_of_same_external_holder_name(holder_name:str) -> int:
    """
    Get the number of external bank accounts with the same holder name.

    :param holder_name: The name of the holder
    :return: The number of external bank accounts with the same holder name
    """
    try:
        if len([i for i in rd.get('external_bank_accounts_info') if i['holderName'] == holder_name]) > 1:
            return len([i for i in rd.get('external_bank_accounts_info') if i['holderName'] == holder_name])
        else:
            return 1
    except Exception as e:
        logger.error(e)
        return 0

def get_external_iban_with_same_name(name:str):
    return [i['holderIBAN'] for i in rd.get('external_bank_accounts_info') if i['holderName'] == name ]



    

def get_list_of_iban_with_same_name():
    
    return 0

rd.set('external_bank_accounts_info', json.dumps(get_external_bank_account_info()))
rd.set('wallets_info', json.dumps(get_wallet_holder_info()))
rd.set('payments_histo', json.dumps(get_payments_status()['payments']))

if __name__ == '__main__':
    file_a = 'new_payment.xlsx'
    #print(get_wallets())
    # print(post_payment(file_a))
    #print(get_wallet_holder_info())
    #print(list_wallets_from_file(file_a))
    #retreive_option_list(wallet_id="", external_id="Njc1NzI")
    #print(check_if_external_bank_account_exist(external_bank_account_id="Njc1NzI"))
    #payload(file_a)
    #jason = {'Compte Emetteur': 'BE39914001921319', 'Bénéficiaire': 'FR1130002005440000007765L61', 'Montant': 14, 'Libélé': 'jjj', 'Commentaire': 'opoo', 'Date désirée': '2025-02-17'}
    #jason = {'Priorité': '2H', 'Bénéficiaire': '09cf660e9747a34', 'Expéditeur': 'BE12914005042392', 'Commentaire': '', 'Libellé': '', 'Montant': '14', 'Date désirée': ''}
    jason2 = {'Priorité': '1H', 'Bénéficiaire': '314b065159e8e9c', 'Expéditeur': 'BE39914001921319', 'Commentaire': '', 'Libellé': '', 'Montant': '2', 'Date désirée': ''}
    #authentication("mn11256", "61JyoSK8GW6q395cXJTy0RtuhaFpIaxJCiMRESAVjEAO5kXJ+h0XsGGRD3gJu/pRrJyrr6C5u8voxAzleA/k6g==")
    # print(post_payment_from_form(jason2))
    # print(rd.get('wallets_info'))
    #print(rd.get('payments_histo')[0]['sourceWalletId'])
    #print(check_account_value(wallet_id="OTg1OTE", amount=12))
    print(rd.get(''))

    

    
