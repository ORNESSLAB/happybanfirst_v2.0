#Normalize format

import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import country_converter as coco
import pandas as pd


def valid(json_data_to_check: dict, json_schema_file_dir: str) -> bool:
    try:
        with open(json_schema_file_dir) as f:
            schema = json.load(f)
        
        try:
            validate(instance=json_data_to_check, schema=schema)
            return True
        except ValidationError:
            return False

    except Exception as e:
        raise e

def mapping_wallet_values(data):
    wallet = data['wallet']
    correspondentBank_bic = wallet['correspondentBank']['bic']
    correspondentBank_name = wallet['correspondentBank']['name']
    correspondentBank_address_street = wallet['correspondentBank']['address']['street']
    correspondentBank_address_postCode = wallet['correspondentBank']['address']['postCode']
    correspondentBank_address_city = wallet['correspondentBank']['address']['city']
    correspondentBank_address_province = wallet['correspondentBank']['address']['province']
    correspondentBank_address_country = wallet['correspondentBank']['address']['country']
    holderBank_bic = wallet['holderBank']['bic']
    holderBank_name = wallet['holderBank']['name']
    holderBank_address_street = wallet['holderBank']['address']['street']
    holderBank_address_postCode = wallet['holderBank']['address']['postCode']
    holderBank_address_city = wallet['holderBank']['address']['city']
    holderBank_address_province = wallet['holderBank']['address']['province']
    holderBank_address_country = wallet['holderBank']['address']['country']
    holder_name = wallet['holder']['name']
    holder_type = wallet['holder']['type']
    holder_address_street = wallet['holder']['address']['street']
    holder_address_postCode = wallet['holder']['address']['postCode']
    holder_address_city = wallet['holder']['address']['city']
    holder_address_province = wallet['holder']['address']['province']
    holder_address_country = wallet['holder']['address']['country']
    wallet.pop('correspondentBank')
    wallet.pop('holderBank')
    wallet.pop('holder')
    wallet['correspondentBank_bic'] = correspondentBank_bic
    wallet['correspondentBank_name'] = correspondentBank_name
    wallet['correspondentBank_address_street'] = correspondentBank_address_street
    wallet['correspondentBank_address_postCode'] = correspondentBank_address_postCode
    wallet['correspondentBank_address_city'] = correspondentBank_address_city
    wallet['correspondentBank_address_province'] = correspondentBank_address_province
    wallet['correspondentBank_address_country'] = correspondentBank_address_country
    wallet['holderBank_bic'] = holderBank_bic
    wallet['holderBank_name'] = holderBank_name
    wallet['holderBank_address_street'] = holderBank_address_street
    wallet['holderBank_address_postCode'] = holderBank_address_postCode
    wallet['holderBank_address_city'] = holderBank_address_city
    wallet['holderBank_address_province'] = holderBank_address_province
    wallet['holderBank_address_country'] = holderBank_address_country
    wallet['holder_name'] = holder_name
    wallet['holder_type'] = holder_type
    wallet['holder_address_street'] = holder_address_street
    wallet['holder_address_postCode'] = holder_address_postCode
    wallet['holder_address_city'] = holder_address_city
    wallet['holder_address_province'] = holder_address_province
    wallet['holder_address_country'] = holder_address_country
    return wallet


def mapping_payment_values(json_data:str):
    payment = json_data['payment']
    amount_value = payment['amount']['value']
    amount_currency = payment['amount']['currency']
    feePaymentAmount_value = payment['feePaymentAmount']['value']
    feePaymentAmount_currency = payment['feePaymentAmount']['currency']
    rate_currencyPair = payment['rate']['currencyPair']
    rate_midMarket = payment['rate']['midMarket']
    rate_date = payment['rate']['date']
    rate_coreAsk = payment['rate']['coreAsk']
    rate_coreBid = payment['rate']['coreBid']
    rate_appliedAsk = payment['rate']['appliedAsk']
    rate_appliedBid = payment['rate']['appliedBid']
    counterValue_value  = payment['counterValue']['value']
    counterValue_currency = payment['counterValue']['currency']
    payment.pop('counterValue')
    payment.pop('feePaymentAmount')
    payment.pop('rate')
    payment.pop('amount')
    payment['amount_value'] = amount_value
    payment['amount_currency'] = amount_currency
    payment['feePaymentAmount_value'] = feePaymentAmount_value
    payment['feePaymentAmount_currency'] = feePaymentAmount_currency
    payment['rate_currencyPair'] = rate_currencyPair
    payment['rate_midMarket'] = rate_midMarket
    payment['rate_date'] = rate_date
    payment['rate_coreAsk'] = rate_coreAsk
    payment['rate_coreBid'] = rate_coreBid
    payment['rate_appliedAsk'] = rate_appliedAsk
    payment['rate_appliedBid'] = rate_appliedBid
    payment['counterValue_value'] = counterValue_value
    payment['counterValue_currency'] = counterValue_currency
    return payment

def mapping_payment_submit(excel_data:dict) -> dict:
    """
    Mapping function for payment submission.
    
    This function takes a list of excel dictionaries and returns a single dictionary
    that can be used to submit a payment via the API.
    
    Parameters
    ----------
    excel_data : str
        A JSON string containing a list of dictionaries, where each dictionary represents
        a single row of an excel file. The dictionaries should contain the following keys:
            externalBankAccountId : str
            sourceWalletId : str
            amount_value : str
            amount_currency : str
            desiredExecutionDate : str
            feeCurrency : str
            feePaymentOption : str
            priorityPaymentOption : str
            tag : str
            communication : str
    
    Returns
    -------
    payment_submit : dict
        A dictionary containing the payment information.
    """

    payment_submit = {}
    payment_submit['externalBankAccountId'] = excel_data['Destinataire']
    payment_submit['sourceWalletId'] = excel_data['Compte']
    payment_submit['amount'] = {'value':excel_data['montant'], 'currency':excel_data['devise']}
    payment_submit['desiredExecutionDate'] = pd.to_datetime(excel_data['date'], format='%Y-%m-%d').strftime('%Y-%m-%d') #excel_data['date']
    payment_submit['priorityPaymentOption'] = excel_data['priorite']
    payment_submit['feeCurrency'] = excel_data['devise']
    payment_submit['tag'] = excel_data['tag'] if excel_data['tag'] else ''
    payment_submit['communication'] = excel_data['commentaire'] if excel_data['commentaire'] else ''
    return payment_submit

def mapping_wallets_submit(excel_data:dict) -> dict:
    wallet_submit = {}
    wallet_submit["currency"] = excel_data['devise'] if excel_data['devise'] else ''
    wallet_submit["tag"] = excel_data['tag'] if excel_data['tag'] else ''
    wallet_submit["holder"] = {}
    wallet_submit["holder"]["name"] = excel_data['nom'] if excel_data['nom'] else ''
    wallet_submit["holder"]["type"] = excel_data['type'].capitalize() if excel_data['type'] else ''
    wallet_submit["holder"]["address"] = {}
    wallet_submit["holder"]["address"]["street"] = excel_data['rue'] if excel_data['rue'] else ''
    wallet_submit["holder"]["address"]["postCode"] = excel_data['code postal'] if excel_data['code postal'] else ''
    wallet_submit["holder"]["address"]["city"] = excel_data['ville'] if excel_data['ville'] else ''
    wallet_submit["holder"]["address"]["province"] = excel_data['province'] if excel_data['province'] else ''
    wallet_submit["holder"]["address"]["country"] = coco.convert(excel_data['pays'], to='ISO2') if excel_data['pays'] else ''
    return wallet_submit
    
if __name__ == '__main__':
    print(mapping_payment_submit({'Compte': 'NjczODE', 'Destinataire': 'NjczODA', 'devise': 'USD', 'montant': 24, 'tag': 'ha', 'commentaire': 'euh', 'date': '2025-04-06', 'priorite': '24H'}))
