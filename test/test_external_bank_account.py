# Coding: ufc-8
from __future__ import absolute_import
import unittest
from orness  import utils

class Testbeneficiary(unittest.TestCase):

    def setUp(self):
        self.ext = {
            "currency": "EUR",
            "tag": "mon extern",
            "accountNumber": "FR1130002005440000007765L61",
            "correspondentBankBic": "",
            "holderBank": {
                "bic": "CRLYFRPPXXX",
                "clearingCodeType": "",
                "clearingCode": "3000200561",
                "name": "LE CREDIT LYONNAIS",
                "address": {
                    "street": "19 BOULEVARD DES ITALIENS",
                    "postCode": "75002",
                    "city": "paris",
                    "country": "FR",
                    "state": ""
                }
            },
            "holder": {
                "name": "Julien",
                "type": "corporate",
                "address": {
                    "street": "21 rue du lac",
                    "postCode": "21000",
                    "city": "dijon",
                    "country": "FR",
                    "state": ""
                }
            }
        }
        self.holdername = "314b065159e8e9c"
    def test_create_benifecary(self):
        self.assertIsNotNone(utils.create_beneficiary(self.ext))

    def test_beneficiary_existance(self):
        self.assertTrue(utils.check_if_beneficiary_name(self.holdername))

    
    
if __name__ == "__main__":
    unittest.main(verbosity=2)


        