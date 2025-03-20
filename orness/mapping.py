from orness import error_exception
import logging
from orness import utils
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
            return len([i for i in self.wallets if      i['holderIBAN'] == iban])
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
    

    
    def mapping_payment_submit(self, data:dict) -> dict:
        payment_submit = {}
       
        external_Id, BENEFICIARY_ERROR = self.choose_beneficiary(data)
        source_Id, SOURCE_ERROR = self.choose_the_wallet(data=data)
        logger.debug(f" Recipient ID: {external_Id} and Sender ID: {source_Id}")
        if not source_Id or not external_Id:
            return payment_submit, {"SOURCE_ERROR":SOURCE_ERROR, "BENEFICIARY_ERROR":BENEFICIARY_ERROR, "ERROR_CURRENCY": error_exception.NO_ERROR, "AMOUNT_ERROR": error_exception.NO_ERROR}
        if not data['Amount']:
            return payment_submit, {"SOURCE_ERROR":SOURCE_ERROR, "BENEFICIARY_ERROR":BENEFICIARY_ERROR, "AMOUNT_ERROR": error_exception.AMOUNT_NOT_PROVIDED, "ERROR_CURRENCY": error_exception.NO_ERROR}

        #test currencies
        if external_Id[0][1] == data["Currency"] or not data["Currency"]:
            payment_submit['externalBankAccountId'] = external_Id[0][0]
            payment_submit['sourceWalletId'] = source_Id[0][0]
            date_execution = utils.date_format(date=data['Execution date'])
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
        