import pandas as pd
import json
from ibanfirst_client.rest import ApiException
import orness.bind as bind
from orness.orness_api import IbExternalBankAccountApi, IbWalletApi, IbPaymentsApi

def get_wallets():
    wallets = IbWalletApi()
    return wallets.wallets_get().json()

def get_wallet_id(id):
    wallet = IbWalletApi()
    return wallet.wallets_id_get(id).json()

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
                    "priorityPaymentOption": option['priorityPaymentOption'],
                    "feePaymentOption": option["feePaymentOption"],
                    "feeCurrency": option["feeCost"]["currency"]
                }
        return {}

def payload(excel_data_filename:str):
    priority = "48h"
    json_data_from_excel = read_excel(excel_data_filename)
    payment_submit = bind.mapping_payment_submit(json_data_from_excel)
    try:
        options = retreive_option_list(external_id=payment_submit['externalBankAccountId'], wallet_id=payment_submit['sourceWalletId'])
        
        properties = get_payment_fee_and_priority(priority=priority, options=options)
        payment_submit["feeCurrency"] = properties['feeCurrency']
        payment_submit["feePaymentOption"] = properties['feePaymentOption']
        payment_submit["priorityPaymentOption"] = properties['priorityPaymentOption']
        return json.dumps(payment_submit)
        
    except TypeError:
        print('The wallet or external bank account does not exist')
        return payment_submit
    
def post_payment(payment_submit: dict) -> dict:
    api = IbPaymentsApi()
    print(f"ok :        {payment_submit}")
    return api.payments_post(payment=payment_submit)

def retreive_option_list(wallet_id:str, external_id:str) -> list: 
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


if __name__ == '__main__':
    #print(read_excel("new_payment.xlsx"))
    print(payload("new_payment.xlsx"))
    #print(post_payment(payload("new_payment.xlsx")))
    #t = retreive_option_list("NjczODM", "NjczODA")
    #print(get_payment_fee_and_priority(t, "48h".upper()))
