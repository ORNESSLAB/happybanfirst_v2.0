#Normalize format

import json
from locale import currency

from jsonschema import validate
from jsonschema.exceptions import ValidationError
import country_converter as coco
from datetime import datetime   
from orness import utils
import redis

rd = redis.Redis(host='localhost', port=6379, db=0)

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


def mapping_payment_submit(data:dict) -> dict:
    """
    Mapping function for payment submission.
    
    This function takes a list of excel dictionaries and returns a single dictionary
    that can be used to submit a payment via the API.
    
    Parameters
    ----------
    data : str
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
    #TODO: manage date conversion
    
    
    

    source_Id = "".join(k['id'] for k in json.loads(rd.get('wallets_info'))if k['holderIBAN'] == data['Expéditeur'])
    amount_currency = "".join(k['amountCurrency'] for k in json.loads(rd.get('wallets_info'))if k['holderIBAN'] == data['Expéditeur'])
    external_Id = "".join(k['id'] for k in json.loads(rd.get('external_bank_accounts_info')) if k['holderIBAN'] == data['Bénéficiaire'])
    payment_submit = {}
    payment_submit['externalBankAccountId'] = external_Id
    payment_submit['sourceWalletId'] = source_Id
    payment_submit['amount'] = {'value':data['Montant'], 'currency': amount_currency}
    payment_submit['desiredExecutionDate'] = data['Date désirée'] if data['Date désirée'] else datetime.today().strftime('%Y-%m-%d') #data['date']
    payment_submit['priorityPaymentOption'] = data['Urgence'] if data['Urgence'] else '24H' #data['priorite']
    payment_submit["feePaymentOption"] = data['Détails des frais'] if data['Détails des frais'] else 'OUR'
    payment_submit['tag'] = data['Libellé'] if data['Libellé'] else ''
    payment_submit['communication'] = data['Commentaire'] if data['Commentaire'] else ''
    return payment_submit

def mapping_wallets_submit(data:dict) -> dict:
    wallet_submit = {}
    wallet_submit["currency"] = data['devise'] if data['devise'] else ''
    wallet_submit["tag"] = data['tag'] if data['tag'] else ''
    wallet_submit["holder"] = {}
    wallet_submit["holder"]["name"] = data['nom'] if data['nom'] else ''
    wallet_submit["holder"]["type"] = data['type'].capitalize() if data['type'] else ''
    wallet_submit["holder"]["address"] = {}
    wallet_submit["holder"]["address"]["street"] = data['rue'] if data['rue'] else ''
    wallet_submit["holder"]["address"]["postCode"] = data['code postal'] if data['code postal'] else ''
    wallet_submit["holder"]["address"]["city"] = data['ville'] if data['ville'] else ''
    wallet_submit["holder"]["address"]["province"] = data['province'] if data['province'] else ''
    wallet_submit["holder"]["address"]["country"] = coco.convert(data['pays'], to='ISO2') if data['pays'] else ''
    return wallet_submit

def mapping_ben_creation(data:dict):
    ben = {}
    ben['holder'] = {}
    ben['holderBank'] = {}
    ben["holderBank"]["address"] = {}
    ben["holder"]["address"] = {}

    ben["currency"]             = data["currency"]          if data["currency"]          else ""  
    ben["accountNumber"]        = data["accountNumber"]     if data["accountNumber"]     else ""
    ben["tag"]                  = data["tag"]               if data["tag"]               else ""
    ben["correspondentBankBic"] = data["correspondentBankBic"] if data["correspondentBankBic"] else ""
    
    ben["holder"]["name"]                  = data["holder"]["name"] if data["holder"]["name"] else ""
    ben["holder"]["address"]["street"]     = data["holder"]["address"]["street"] if data["holder"]["address"]["street"] else ""
    ben["holder"]["address"]["postCode"] = data["holder"]["address"]["postCode"] if data["holder"]["address"]["postCode"] else ""
    ben["holder"]["address"]["city"] = data["holder"]["address"]["city"] if data["holder"]["address"]["city"] else ""
    ben["holder"]["address"]["country"] = data["holder"]["address"]["country"] if data["holder"]["address"]["country"] else ""
    ben["holder"]["type"] = data["holder"]["type"] if data["holder"]["type"] else ""
    ben["holderBank"]["address"]["street"]= data["holderBank"]["address"]["street"] if data["holderBank"]["address"]["street"] else ""
    ben["holderBank"]["address"]["postCode"] = data["holderBank"]["address"]["postCode"]  if data["holderBank"]["address"]["postCode"] else  ""
    ben["holderBank"]["address"]["city"] = data["holderBank"]["address"]["city"]  if data["holderBank"]["address"]["city"] else ""
    ben["holderBank"]["address"]["country"] = coco.convert(data["holderBank"]["address"]["country"], to='ISO2') if data["holderBank"]["address"]["country"] else ""
    ben["holderBank"]["address"]["state"]= data["holderBank"]["address"]["state"] if data["holderBank"]["address"]["state"] else ""
    ben["holderBank"]["bic"] = data["holderBank"]["bic"] if data["holderBank"]["bic"] else ""
    ben["holderBank"]["name"] = data["holderBank"]["name"]  if data["holderBank"]["name"]  else ""
    ben["holderBank"]["clearingCodeType"] = data["holderBank"]["clearingCodeType"] if data["holderBank"]["clearingCodeType"] else ""
    ben["holderBank"]["clearingCode"] = data["holderBank"]["clearingCode"] if data["holderBank"]["clearingCode"] else ""



    return  ben

if __name__ == '__main__':
   print(rd.get('wallets_info'))
    
