# coding: utf-8



from __future__ import absolute_import

import unittest
from orness.orness_api import IbWalletApi # noqa: E501

class TestWalletsApi(unittest.TestCase):
    """WalletsApi unit test stubs"""

    def setUp(self):
        self.api2 = IbWalletApi() # noqa: E501
     
    def tearDown(self):
        pass

    def test_wallets_get(self):
        """Test case for wallets_get

        Get wallet list  # noqa: E501
        """
        print(self.api2.wallets_get().json())

    def test_wallets_id_balance_date_get(self):
        """Test case for wallets_id_balance_date_get

        Retrieve wallet balance for a given date  # noqa: E501
        """
       

    def test_wallets_id_get(self):
        """Test case for wallets_id_get

        Get wallet details  # noqa: E501
        """

    def test_wallets_post(self):
        """Test case for wallets_post

        Submit a new wallet  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
