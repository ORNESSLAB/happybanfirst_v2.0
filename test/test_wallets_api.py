# coding: utf-8



from __future__ import absolute_import

import unittest
from orness.ornessSDK  import OrnessSDK

class TestWalletsApi(unittest.TestCase):
    """WalletsApi unit test stubs"""

    def setUp(self):
         # noqa: E501
        self.sdk = OrnessSDK()
        self.sdk.login(password="61JyoSK8GW6q395cXJTy0RtuhaFpIaxJCiMRESAVjEAO5kXJ+h0XsGGRD3gJu/pRrJyrr6C5u8voxAzleA/k6g==", username="mn11256")
        
     
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
        wallet = self.sdk.get_wallets_holder_info()
        self.assertIsInstance(wallet, list)
        self.assertIsNotNone(wallet)

    def test_if_external_bank_account_existt(self):
        """Test case for external_bank_account_id_get

        Get external bank account details  # noqa: E501
        """
        self.assertTrue(self.sdk.check_if_external_bank_account_exist('NjczODA'))
        
    def test_fund_wallet(self): 
        """
        Test case for fund_wallet
        """
        self.assertTrue(self.sdk.check_account_value('NjczODE', 10))
    
    def test_fund_wallet_false(self): 
        """
        Test case for not enough fund in wallet
        """
        self.assertFalse(self.sdk.check_account_value('NjczODE', 10000))

    def test_wallets_post(self):
        """Test case for wallets_post

        Submit a new wallet  # noqa: E501
        """
        pass
    
    
    


if __name__ == '__main__':
    unittest.main(verbosity=2)
