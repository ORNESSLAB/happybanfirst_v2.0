#Normalize format

import json

from jsonschema import validate
from jsonschema.exceptions import ValidationError
import country_converter as coco
from datetime import datetime  
import logging
import pandas as pd 
import redis
from orness import error_exception

logger = logging.getLogger(__name__)
rd = redis.Redis(host='localhost', port=6379, db=0)
wallets = json.loads(rd.get('wallets_info'))
beneficiary = json.loads(rd.get('external_bank_accounts_info'))


def max_value(wallets):
    return max([float(i["amountValue"]) for i in wallets])
    
   
def number_of_same_object_holder_name(holder_name:str, objet) -> int:
   
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
   

    try:
        
        return len([i for i in json.loads(rd.get(objet)) if i['holderName'] == holder_name])
        
    except Exception as e:
        logger.error(e)
        return 0

def get_object_with_same_name(name:str, objet='external_bank_accounts_info'):
    """_summary_

    Args:
        name (str): _description_
        objet (str, required): _description_. choice: 'external_bank_accounts_info' 'wallets_info'.

    Returns:
        _type_: _description_
    """
    return [i['holderIBAN'] for i in json.loads(rd.get(objet)) if i['holderName'] == name ]



def check_if_beneficiary_name(holderName:str):
    return any(i['holderName'] == holderName  for i in rd.get('external_bank_accounts_info') )


def choose_the_wallet(data, ben_currency):
    error = 0
    source_Id=[]
    if (data['Expéditeur'] and not data['Unnamed: 1']): 
        if number_of_same_object_holder_name(data['Expéditeur'], objet="wallets_info") > 1:
            #si le nom du compte expéditeur est reseigner sans l'IBAN, le compte qui sera choisir sera celui avec soit la même devise que celui du bénéficiaire ou celui avec plus de fonds
            source_Id = [(k['id'], k['amountCurrency']) for k in wallets  if k['holderName'] == data['Expéditeur'] and k['amountCurrency'] == ben_currency and float(k['amountValue']) > float(data['Montant'])]
            if not source_Id:
                error = 1
                source_Id = [(k['id'], k['amountCurrency']) for k in wallets  if k['holderName'] == data['Expéditeur'] and float(k['amountValue']) == max_value(wallets)]
            
        
    elif data['Expéditeur'] and  data['Unnamed: 1']:

        source_Id = [(k['id'], k['amountCurrency'], k["amountValue"]) for k in wallets  if k['holderIBAN'] == data['Unnamed: 1'] and k['holderName'] == data['Expéditeur']]
        if not source_Id:
            error = 1
        elif float(source_Id[0][2]) > float(data['Montant']):
            source_Id = source_Id
        else:
            error = 2
            source_Id = [(k['id'], k['amountCurrency']) for k in wallets  if k['holderName'] == data['Expéditeur'] and float(k['amountValue']) == max_value(wallets)]
            
    elif not data['Expéditeur'] and not data['Unnamed: 1']:
        source_Id = [(k['id'], k['amountCurrency']) for k in wallets  if k['amountCurrency'] == ben_currency and float(k['amountValue']) > float(data['Montant'])]
        if not source_Id:
            source_Id = [(k['id'], k['amountCurrency']) for k in wallets  if float(k['amountValue']) == max_value(wallets)]
        
    else:
        source_Id = [(k['id'], k['amountCurrency'], k["amountValue"]) for k in wallets  if k['holderIBAN'] == data['Unnamed: 1']]
        if not source_Id:
            error = 3
        elif float(source_Id[0][2]) > float(data['Montant']):
            source_Id = source_Id
        else:
            error = 4
            source_Id = [(k['id'], k['amountCurrency']) for k in wallets  if float(k['amountValue']) == max_value(wallets)]
        
            
    return source_Id, error

def choose_beneficiary(data):
    if not data['Unnamed: 3'] and data['Bénéficiaire']: 
        if number_of_same_object_holder_name(data['Bénéficiaire'], objet="external_bank_accounts_info") > 1:
            return error_exception.TOO_MUCH_BENEFICIARY_IBAN
        else:
            benef = [(k['id'], k['currency']) for k in beneficiary  if k['holderName'] == data['Bénéficiaire']]
        
    elif data['Unnamed: 3'] and data['Bénéficiaire']:
        benef = [(k['id'], k['currency']) for k in beneficiary  if k['holderName'] == data['Bénéficiaire'] and k['holderIBAN'] == data['Unnamed: 3']]
        print(f"ben_ tous IBAN et Name: {benef} IBAN:{data['Unnamed: 3']}BEN:{data['Bénéficiaire']}OK")
        if not benef:
            return error_exception.NO_BENEFICIARY_FOUND
    else:
        benef = [(k['id'], k['currency']) for k in beneficiary  if  k['holderIBAN'] == data['Unnamed: 3']]
        if len(benef) > 1:
            return error_exception.TOO_MUCH_BENEFICIARY_IBAN
        if not benef:
            print(f"ben_ juste_IBAN: {benef}")
            return error_exception.NO_BENEFICIARY_FOUND
        
        else:
            benef = benef
    return benef
    


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
    
    
    

    
    payment_submit = {
        "sourceWalletId": "",
        "externalBankAccountId": "",
        "amount": {
          "value": "",
          "currency": ""
           },
        "desiredExecutionDate": "",
        "feeCurrency": "",
        "feePaymentOption": "",
        "priorityPaymentOption": "",
        "tag": "string",
        "communication": "string"
    }
    source_Id = "".join(k['id'] for k in wallets if k['holderIBAN'] == data['Expéditeur'])
    fee_currency = "".join(k['amountCurrency'] for k in wallets  if k['holderName'] == data['Expéditeur'])
        
    amount_currency = "".join(k['currency'] for k in beneficiary if k['holderIBAN'] == data['Bénéficiaire'])
    external_Id = "".join(k['id'] for k in beneficiary  if k['holderIBAN'] == data['Bénéficiaire'])

    payment_submit['externalBankAccountId'] = external_Id
    payment_submit['sourceWalletId'] = source_Id
    #date_execution = pd.to_datetime(data['Date d’exécution']).strftime('%Y-%m-%d')
    payment_submit['amount'] = {'value':data['Montant'], 'currency': amount_currency}
    payment_submit['desiredExecutionDate'] = date_format(date=data['Date d’exécution'])  
    payment_submit['priorityPaymentOption'] = data['Urgence'] if data['Urgence'] else '24H' #data['priorite']
    payment_submit['feeCurrency'] = fee_currency
    payment_submit['feePaymentOption'] = data['Détails des frais'] if data['Détails des frais'] else ''
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

    ben["currency"]             = data["currency"]          if data["currency"]          else "EUR"  
    ben["accountNumber"]        = data["accountNumber"]     if data["accountNumber"]     else ""
    ben["tag"]                  = data["tag"]               if data["tag"]               else ""
    ben["correspondentBankBic"] = data["correspondentBankBic"] if data["correspondentBankBic"] else ""
    
    ben["holder"]["name"] = data["holder"]["name"] if data["holder"]["name"] else ""
    ben["holder"]["address"]["street"] =  data["holder"]["address"]["street"] if data["holder"]["address"]["street"] else ""
    ben["holder"]["address"]["postCode"] = data["holder"]["address"]["postCode"] if data["holder"]["address"]["postCode"] else ""
    ben["holder"]["address"]["city"] = data["holder"]["address"]["city"] if data["holder"]["address"]["city"] else ""
    ben["holder"]["address"]["country"] = data["holder"]["address"]["country"] if data["holder"]["address"]["country"] else ""
    ben["holder"]["type"] = data["holder"]["type"] if data["holder"]["type"] else ""
    ben["holderBank"]["address"]["street"]= data["holderBank"]["address"]["street"] if data["holderBank"]["address"]["street"] else ""
    ben["holderBank"]["address"]["postCode"] = data["holderBank"]["address"]["postCode"]  if data["holderBank"]["address"]["postCode"] else  ""
    ben["holderBank"]["address"]["city"] = data["holderBank"]["address"]["city"]  if data["holderBank"]["address"]["city"] else ""
    ben["holderBank"]["address"]["country"] = data["holderBank"]["address"]["country"] if data["holderBank"]["address"]["country"] else ""
    ben["holderBank"]["address"]["state"]= data["holderBank"]["address"]["state"] if data["holderBank"]["address"]["state"] else ""
    ben["holderBank"]["bic"] = data["holderBank"]["bic"] if data["holderBank"]["bic"] else ""
    ben["holderBank"]["name"] = data["holderBank"]["name"]  if data["holderBank"]["name"]  else ""
    ben["holderBank"]["clearingCodeType"] = data["holderBank"]["clearingCodeType"] if data["holderBank"]["clearingCodeType"] else ""
    ben["holderBank"]["clearingCode"] = data["holderBank"]["clearingCode"] if data["holderBank"]["clearingCode"] else ""



    return  ben



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


# def date_format(date: str):
#     if date == "":
#         return datetime.now().strftime('%Y-%m-%d')

#     try:
#         # Parse the date string into a datetime object
#         input_date = datetime.strptime(date, "%Y-%m-%d")

#         # Compare the input date with the current date
#         if input_date > datetime.now():
#             return input_date.strftime('%Y-%m-%d')
#         else:
#             return datetime.now().strftime('%Y-%m-%d')

#     except ValueError:
#         # Handle invalid date format gracefully
#         return "Invalid date format. Please use YYYY-MM-DD."
    

def mapping_payment_submit_v2(data:dict) -> dict:
    payment_submit = {}
    #TODO: check the amount currency
    #TODO: check wallet holder name
    #TODO: check beneficiary holder name
    #TODO: return error value
    
    try:
        external_Id = choose_beneficiary(data)
        source_Id, error = choose_the_wallet(data=data, ben_currency=external_Id[0][1])
        
        
        
            
        
        payment_submit['externalBankAccountId'] = external_Id[0][0]
        payment_submit['sourceWalletId'] = source_Id[0][0]
        date_execution = date_format(date=data['Date d’exécution'])
        payment_submit['amount'] = {'value':data['Montant'], 'currency': external_Id[0][1]}
        payment_submit['desiredExecutionDate'] = date_execution 
        payment_submit['priorityPaymentOption'] = data['Urgence'] if data['Urgence'] else '24H' #data['priorite']
        payment_submit['feeCurrency'] = source_Id[0][1]
        if data['Détails des frais']:
            if data['Détails des frais'].upper() == "CLIENT":
                payment_submit['feePaymentOption'] = 'OUR'
            if data['Détails des frais'].upper() == "Bénéficiaire".upper():
                payment_submit['feePaymentOption'] = 'BEN'
            if data['Détails des frais'].upper() == "Partagé".upper():
                payment_submit['feePaymentOption'] = 'SHARE'
        else:
            payment_submit['feePaymentOption'] = "OUR"
        payment_submit['tag'] = data['Libellé'] if data['Libellé'] else ''
        payment_submit['communication'] = data['Commentaire'] if data['Commentaire'] else ''
        return payment_submit
    except TypeError as err:
        logger.error(f"erreur [Mapping]: {err}")
        raise ("Erreur [Mapping]")
    

if __name__ == '__main__':
    data = {'Expéditeur': '', 'Unnamed: 1': '', 'Bénéficiaire': '87ac164a37e96db', 'Unnamed: 3': '', 'Montant': 600.0, 'Date d’exécution': "2025-03-24", 'Détails des frais': 'client', 'Urgence': None, 'Libellé': None, 'Commentaire': None}
    #     {'Expéditeur': 'TEST API ORNESS', 'Unnamed: 1': 'BE17914001921521', 'Bénéficiaire': 'b44126a0e90b4d4', 'Unnamed: 3': 'RS35160005010008573607', 'Montant': 25.0, 'Date d’exécution': "2025-03-15", 'Détails des frais': 'bénéficiaire', 'Urgence': None, 'Libellé': None, 'Commentaire': None},
    #data = {'Expéditeur': 'TEST API ORNESS', 'Unnamed: 1': 'BE39914001921319', 'Bénéficiaire': '87ac164a37e96db', 'Unnamed: 3': '44717721356', 'Montant': 9.0, 'Date d’exécution': "2025-03-14", 'Détails des frais': 'partagé', 'Urgence': None, 'Libellé': None, 'Commentaire': None}
    ben = {'id': 'ODYyMjM', 'holderName': '87ac164a37e96db', 'holderBankBic': 'SCBLHKHHXXX', 'holderIBAN': '44717721356', 'currency': 'USD'}
    #print(choose_beneficiary(data))
    #print([(k['id'], k['currency']) for k in beneficiary  if k['holderName'] ==  "87ac164a37e96db" and k['holderIBAN'] == "44717721356"])
    print(date_format(""))

    
