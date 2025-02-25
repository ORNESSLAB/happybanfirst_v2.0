ERROR_FUNDS = 0
ERROR_PRIORITY = 1
ERROR_NO_PRIORITY = 2




class NoFund(ValueError):
    pass

class PriorityError(ValueError):
    pass

class NoPriorityError(ValueError):
    pass


