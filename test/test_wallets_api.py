# coding: utf-8



from __future__ import absolute_import

import unittest
from orness import utils
class TestWalletsApi(unittest.TestCase):
    """WalletsApi unit test stubs"""

    def setUp(self):
         # noqa: E501
         pass
     
    def tearDown(self):
        pass

    def test_wallets_get(self):
        """Test case for wallets_get

        Get wallet list  # noqa: E501
        """
        

    def test_wallets_id_balance_date_get(self):
        """Test case for wallets_id_balance_date_get

        Retrieve wallet balance for a given date  # noqa: E501
        """
       

    def test_wallets_id_get(self):
        """Test case for wallets_id_get

        Get wallet details  # noqa: E501
        """
    def test_fund_wallet(self): 
        """
        Test case for fund_wallet
        """
        self.assertTrue(utils.check_account_value('NjczODE', 10))
    
    def test_fund_wallet_false(self): 
        """
        Test case for fund_wallet
        """
        self.assertFalse(utils.check_account_value('NjczODE', 10000))

    def test_wallets_post(self):
        """Test case for wallets_post

        Submit a new wallet  # noqa: E501
        """
        pass
    
    def test_number_of_same_external_holder_name(self):
        """
        Test case for number_of_same_external_holder_name
        """
        self.assertEqual(utils.number_of_same_external_holder_name('09cf660e9747a34'), 1)
    
    def test_number_of_same_external_holder_name(self):
        """
        Test case for number_of_same_external_holder_name
        """
        self.assertNotEqual(utils.number_of_same_external_holder_name('314b065159e8e9c'), 1)
    
    


if __name__ == '__main__':
    unittest.main()
