import json
import logging
import pprint
import pandas as pd
from orness import mappings
from ibanfirst_client.rest import ApiException
from orness.orness_api import IbExternalBankAccountApi, IbWalletApi, IbPaymentsApi


logger = logging.getLogger(__name__)

def get_wallets():
    """
    Retrieve the list of all wallets.

    This function uses the IbWalletApi to fetch and return a list of all wallet accounts held with IBANFIRST.

    :return: A JSON object containing a list of all wallets.
    """
    logger.info("Get wallets list")
    try:
        api = IbWalletApi()
        logger.info(pprint.pprint(api.wallets_get().json()))
        return api.wallets_get().json()
    except ApiException as e:
        logger.error(pprint.pprint(e.reason))

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
        logger.info(pprint.pprint(api.wallets_id_get(id).json()))
        return api.wallets_id_get(id).json()
    except ApiException as e:
        logger.error(pprint.pprint(e.reason))
    

def list_wallets_from_file(filename: str) -> list:
    """
    Read the content of the given file and return the content in a json format.

    Parameters:
        filename (str): name of the file to read

    Returns:
        list: the content of the file in json format
    """
    if 'xls' in filename:
        wallets_data = read_excel(filename=filename)
        list_of_wallets = []
        for wallet in wallets_data:
            list_of_wallets.append(get_wallet_id(id=wallet['WalletID'])) #wallet['WalletID']))
        return list_of_wallets
        
    if 'json' in filename:
        # TODO: implement this branch
        pass

def read_excel(filename):
    """
    Read the excel file and return the content in a json format.

    Parameters:
        filename (str): name of the excel file to read

    Returns:
        dict: the content of the excel file in json format
    """
    exc = pd.read_excel(filename)
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
        
        for option in options:
            if option["priorityPaymentOption"] == priority.upper():
                return {
                    "feePaymentOption": option["feePaymentOption"],
                    "feeCurrency": option["feeCost"]["currency"]
                }
        return {}

def payload(excel_data_filename:str):
    #if we want to ask the user to select the priority option
    print("PAYLOAD")
    payload_returned = []
    try:
        json_data_from_excel = read_excel(excel_data_filename) 
        for data in json_data_from_excel:
            payment_submit = mappings.mapping_payment_submit(data)
            print(f"priorité: {payment_submit}")

            #Get fee priority Payment Options
            options = retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
            logger.info("Build the JSON body for payment operation with {} and {}".format(payment_submit['externalBankAccountId'], payment_submit['sourceWalletId']))
            properties = get_payment_fee_and_priority(priority=payment_submit["priorityPaymentOption"], options=options)
            payment_submit["feeCurrency"] = properties['feeCurrency']
            payment_submit["feePaymentOption"] = properties['feePaymentOption']
            dump =json.loads(json.dumps(payment_submit, indent=2))
            #Check if the JSON body format is 
            if (mappings.valid(json_data_to_check=dump, json_schema_file_dir="orness/file/submit_payment_schema.json")):
                payload_returned.append(dump) 
            else: 
                logger.error("json format is not ok")

    # except TypeError:
    #     logger.error("WalletId or ExternalBankAccountId not found")
    except Exception as e:
        logger.error(pprint.pprint(e))

    return payload_returned       

def walletload(excel_data_filename: str) -> list:
    return [
        walletdump for data in read_excel(excel_data_filename)
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
                #logger.info("Start payment of {}".format(pprint.pprint(payment)))

            api = IbPaymentsApi()
            post_payment_response.append(api.payments_post(payment=payment))
                
        return post_payment_response
    except ApiException as e:
        pprint.pprint(e.reason)
    # except Exception as e:
    #     logger.error(pprint.pprint(e))

def create_wallets(excel_data_filename: str) -> list:
    
    try:
        wallets = walletload(excel_data_filename)
        for wallet in wallets:
            logger.info("Create wallet {}".format(log.display_format_data(wallet)))
            api = IbWalletApi()
            api.wallets_post(wallet=wallet)
    except Exception as e:
        logger.error(pprint.pprint(e))

def retreive_option_list(wallet_id:str, external_id:str) -> list: 
    """
    Retrieve the list of options for a given wallet and external bank account.

    :param wallet_id: The id of the wallet
    :param external_id: The id of the external bank account
    :return: The list of options for the given wallet and external bank account
    """
    api = IbPaymentsApi()
    if check_if_external_bank_account_exist(external_bank_account_id=external_id) and check_if_wallet_exist(wallet_id=wallet_id):
        return api.payments_options_wallet_id_external_bank_account_id_get(external_bank_account_id=external_id, wallet_id=wallet_id).json()['paymentOption']['options']

def check_if_wallet_exist(wallet_id: str) -> bool:
        """
        Check if a wallet exists on the API
        :param wallet_id: The id of the wallet to check
        :return: True if the wallet exists, False otherwise
        """
        api = IbWalletApi()
        try:
            api.wallets_id_get(wallet_id)
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            else:
                raise

def check_if_external_bank_account_exist(external_bank_account_id) -> bool:
    """
    Check if an external bank account exists on the API.

    :param external_bank_account_id: The ID of the external bank account to check.
    :return: True if the external bank account exists, False otherwise.
    """
    api = IbExternalBankAccountApi()
    try:
        api.external_bank_accounts_id_get(external_bank_account_id)
        return True
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            raise
    
def get_payments_status(status="all"):
    logging.info("Get payments by status")
    try:
        api = IbPaymentsApi()
        
        payments = api.payments_status_get(status=status).json()
        logger.info(pprint.pprint(payments))
        return payments
    except ApiException as e:
        logger.error(pprint.pprint(e.reason))

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
    logging.info("Get external bank account by id")
    try:
        api = IbExternalBankAccountApi()
        result = api.external_bank_accounts_id_get(id=id).json()
        logger.info(pprint.pprint(result))
        return result
    except ApiException as e:
        logger.error(pprint.pprint(e.reason))



if __name__ == '__main__':
    #print(payload('new_payment.xlsx'))
    print(mappings.mapping_payment_submit({'Compte': 'NjczODE', 'Destinataire': 'NjczODA', 'devise': 'USD', 'montant': 14, 'tag': 'jjj', 'commentaire': 'opoo', 'date': '2025-04-06', 'priorite': '1H'}))
