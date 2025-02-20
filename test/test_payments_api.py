# coding: utf-8

"""
    IBANFIRST API documentation

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 1.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import unittest

from orness import utils


class TestPaymentsApi(unittest.TestCase):
    """PaymentsApi unit test stubs"""

    def setUp(self):
        self.opt = [{'priorityPaymentOption': '24H', 
                'feePaymentOption': 'BEN', 
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
    
    
    def test_payment_from_form(self):
        subm = {'Priorité': '24H', 'Bénéficiaire': 'FR1130002005440000007765L61', 
                'Expéditeur': 'BE39914001921319', 'Commentaire': '', 'Libellé': '', 
                'Montant': '1', 'Date désirée': ''}
        self.assertIsInstance(utils.post_payment_from_form(subm), dict)

    def test_payments_options_wallet_id_external_bank_account_id_get(self):
        """Test case for payments_options_wallet_id_external_bank_account_id_get

        Get payment options for a wallet and an external bank account  # noqa: E501
        """
        self.assertIsNotNone(utils.retreive_option_list(wallet_id='NjczODE', external_id='NjczODA'))

    # def test_payments_post_true(self):
    #     """Test case for payments_post

    #     Submit a payment  # noqa: E501
    #     """
    #     submit_pay = utils.post_payment(self.file)
    #     self.assertNotIsInstance(submit_pay, str)

      

    def test_payments_status_get(self):
        """Test case for payments_status_get

        Get payment list by status  # noqa: E501
        """
        self.assertIsInstance(utils.get_payments_status('awaitingconfirmation'), dict)
    
    def test_payments_status_get(self):
        """Test case for payments_status_get

        Get payment list by status  # noqa: E501
        """
        self.assertIsInstance(utils.get_payments_status('planified'), dict)

    def test_no_priorities_between_two_accounts(self):
        #OTg1OTE, NjczODE
        
        self.assertIsNotNone(utils.retreive_option_list(wallet_id='NjczODE', external_id='NzA2MTA'))
    
    def test_get_payment_fee_and_priority(self):
        self.assertTrue(utils.get_payment_fee_and_priority(options=self.opt, priority='24H'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
