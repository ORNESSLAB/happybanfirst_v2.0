ERROR_PRIORITIES_FOUND_BUT_NOT_WHAT_ENTER = 10
ERROR_NO_PRIORITY = 20
SENDERS_NAME_EMPTY = 30 # si dans le nom tu compte expéditeur n'est pas reseigné
TOO_MUCH_BENEFICIARY_IBAN = 40
NO_BENEFICIARY_FOUND = 50
SENDER_IBAN_NOT_PROVIDED=60
BENEFICIARY_IBAN_NOT_PROVIDED=70
BENEFICIARY_NAME_NOT_PROVIDED=80
NOT_THE_RIGHT_CURRENCY=90
SENDER_NOT_RETREIVED=100
ERROR_NO_FUNDS = 110
NOT_ENOUGH_FUND=120
CURRENCY_NOT_THE_SAME_BETWEEN_SENDER_AND_BEN=130
AMOUNT_NOT_PROVIDED = 140
BENEFICIARY_NAME_AND_IBAN_NOT_PROVIDED=150
TOO_MUCH_SENDER_IBAN_FOUND = 160
NO_ERROR = 0











class NoFund(ValueError):
    pass

class PriorityError(ValueError):
    pass

class NoPriorityError(ValueError):
    pass


