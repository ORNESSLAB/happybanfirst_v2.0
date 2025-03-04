ERROR_FUNDS = 0
ERROR_PRIORITY = 10
ERROR_NO_PRIORITY = 20
WALLETS_NAME_EMPTY = 30 # si dans le nom tu compte expéditeur n'est pas reseigné
TOO_MUCH_BENEFICIARY_IBAN = 40
NO_BENEFICIARY_FOUND = 50







class NoFund(ValueError):
    pass

class PriorityError(ValueError):
    pass

class NoPriorityError(ValueError):
    pass


