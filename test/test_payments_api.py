# coding: utf-8

from __future__ import absolute_import

import unittest


from orness.ornessSDK import OrnessSDK
from orness import jsonvalidator, utils




class TestPaymentsApi(unittest.TestCase):
    """PaymentsApi unit test stubs"""

    def setUp(self):
        self.sdk = OrnessSDK()
        self.sdk.login(password="61JyoSK8GW6q395cXJTy0RtuhaFpIaxJCiMRESAVjEAO5kXJ+h0XsGGRD3gJu/pRrJyrr6C5u8voxAzleA/k6g==", username="mn11256")
        self.data = {'externalBankAccountId': 'NzA2MTA', 
                    'sourceWalletId': 'NjczODE',
                    'amount': {'value': 25.0, 'currency': 'EUR'}, 
                    'desiredExecutionDate': '2025-03-28', 
                    'priorityPaymentOption': '24H', 'feeCurrency': 'EUR', 
                    'feePaymentOption': 'OUR', 'tag': '', 'communication': ''}
        self.data2 = {'externalBankAccountId': 'NzA2MTA', 
                    'sourceWalletId': 'NjczODE',
                    'amount': {'value': 25.0, 'currency': 'CAD'}, 
                    'desiredExecutionDate': '2025-03-28', 
                    'priorityPaymentOption': '24H', 'feeCurrency': 'EUR', 
                    'feePaymentOption': 'OUR', 'tag': '', 'communication': ''}
        
        self.opt = [
            {'priorityPaymentOption': '24H', 'feePaymentOption': 'BEN',
             'priorityCost': {'value': '6.00', 'currency': 'EUR'},
             'feeCost': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountSource': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountTarget': {'value': '0.00', 'currency': 'EUR'}},
            {'priorityPaymentOption': '24H', 'feePaymentOption': 'OUR',
             'priorityCost': {'value': '6.00', 'currency': 'EUR'},
             'feeCost': {'value': '10.00', 'currency': 'EUR'},
             'minimumAmountSource': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountTarget': {'value': '0.00', 'currency': 'EUR'}},
            {'priorityPaymentOption': '24H', 'feePaymentOption': 'SHARE',
             'priorityCost': {'value': '6.00', 'currency': 'EUR'},
             'feeCost': {'value': '5.00', 'currency': 'EUR'},
             'minimumAmountSource': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountTarget': {'value': '0.00', 'currency': 'EUR'}},
            {'priorityPaymentOption': '48H', 'feePaymentOption': 'BEN',
             'priorityCost': {'value': '0.00', 'currency': 'EUR'},
             'feeCost': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountSource': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountTarget': {'value': '0.00', 'currency': 'EUR'}},
            {'priorityPaymentOption': '48H', 'feePaymentOption': 'OUR',
             'priorityCost': {'value': '0.00', 'currency': 'EUR'},
             'feeCost': {'value': '10.00', 'currency': 'EUR'},
             'minimumAmountSource': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountTarget': {'value': '0.00', 'currency': 'EUR'}},
            {'priorityPaymentOption': '48H', 'feePaymentOption': 'SHARE',
             'priorityCost': {'value': '0.00', 'currency': 'EUR'},
             'feeCost': {'value': '5.00', 'currency': 'EUR'},
             'minimumAmountSource': {'value': '0.00', 'currency': 'EUR'},
             'minimumAmountTarget': {'value': '0.00', 'currency': 'EUR'}}]
        self.file = "new_payments_v2.xlsx"
    
    
    def test_bulk_payment(self):
        """Test case for mass of payments"""
        
        pay = self.sdk.post_mass_payment(self.file)[0]
        self.assertIsInstance(pay, list)
        self.assertIsNotNone(pay)

    def test_single_payment(self):
        """Test case for one payment"""

        pay = self.sdk.post_payment(self.data)
        self.assertIsInstance(pay, dict)
        self.assertIsNotNone(pay)

    def test_payment_with_different_currencies(self):
        """ test payment with different currencies"""
        pay = self.sdk.post_payment(self.data2)
        self.assertIsInstance(pay, dict)
        self.assertIsNotNone(pay)
        
        

    def test_payments_options_wallet_id_external_bank_account_id_get(self):
        """Test case for payments_options_wallet_id_external_bank_account_id_get

        Get payment options for a wallet and an external bank account  # noqa: E501
        """
        self.assertIsNotNone(self.sdk.retreive_option_list(wallet_id='NjczODE', external_id='NjczODA'))

    def test_payment_body(self):
        """Test case for payments_post

        Submit a payment  # noqa: E501
        """
        # self.assertTrue(jsonvalidator.valid(self.sdk.payload(self.file)["payment"][0], "file/submit_payment_schema.json"))

    def test_read_excel_file(self):
       self.assertIsNotNone(utils.read_data_from_file(self.file))

    
    def test_payments_status_planified(self):
        """Test case for payments_status_get

        Get payment list by status  # noqa: E501
        """
        self.assertIsInstance(self.sdk.get_payments_status('planified'), dict)
    
    def test_payments_status_finilized(self):
        """Test case for payments_status_get

        Get payment list by status  # noqa: E501
        """
        self.assertIsInstance(self.sdk.get_payments_status('finalized'), dict)

    def test_no_priorities_between_two_accounts(self):
        #OTg1OTE, NjczODE
        
        self.assertIsNotNone(self.sdk.retreive_option_list(wallet_id='NjczODE', external_id='NzA2MTA'))
    
    # def test_get_payment_fee_and_priority(self):
        
    #     self.assertTrue(self.sdk.get_payment_fee_and_priority(options=self.opt, priority='24H'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
