
from ibanfirst_client.api_client import ApiClient
from ibanfirst_client.api.wallets_api import WalletsApi
from ibanfirst_client.api.payments_api import PaymentsApi
from ibanfirst_client.api.external_bank_account_api import ExternalBankAccountApi
from orness.config import Config
from orness.jsonvalidator import valid

API = ApiClient(configuration=Config())




class IbWalletApi(WalletsApi):
    """_IbWalletApi operations  
    """
    def __init__(self):
        """
        Constructor for the class.
        It sets the variables from the environment variables.
        """
        super().__init__()
        header = API.configuration.get_header()
        API.set_default_header('X-WSSE', header['X-WSSE'])
        self.api_client = API

    def wallets_get(self, **kwargs):
        """Get wallet list  # noqa: E501

        With the Retrieve wallet list service, you can list obtain the list of all wallet account hold with IBANFIRST. The object return in the Array is a simplified version of the Wallet providing you the main information on the wallet without any additional request.    # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.wallets_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str page: Index of the page. 
        :param str per_page: Inumber of items returned. 
        :param str sort: A string representing the rendering order of objects. For wallet objects, the sorting is made by wallet's creation date. 
        :return: list[InlineResponse200]
                If the method is called asynchronously,
                returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        kwargs['_preload_content'] = False
        if kwargs.get('async_req'):
            return self.wallets_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.wallets_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def wallets_id_get(self, id, **kwargs):
        """Get wallet details  # noqa: E501

        This request allows you to see the details related to a specific wallet.    # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.wallets_id_get(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: The code identifying the external bank account you want.  (required)
        :return: Wallet
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        kwargs['_preload_content'] = False
        if kwargs.get('async_req'):
            return self.wallets_id_get_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.wallets_id_get_with_http_info(id, **kwargs)  # noqa: E501
            return data
        
    def wallets_post(self, wallet, **kwargs):  # noqa: E501

        """Submit a new wallet  # noqa: E501

        This request allows you to submit a new wallet.   **Caution :** The holder object in the parameters will only be considered if you suscribed to the `Multi account per currency with holder` wallet option.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.wallets_post(wallet, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param Wallet wallet: The wallet to create  (required)
        :return: Wallet
                 If the method is called asynchronously,
                 returns the request thread.
        """
        
        kwargs['_return_http_data_only'] = True
        kwargs['_preload_content'] = False
        
        if kwargs.get('async_req'):
            return self.wallets_post_with_http_info(wallet, **kwargs)  # noqa: E501
        else:
            (data) = self.wallets_post_with_http_info(wallet, **kwargs)  # noqa: E501
            return data
        

class IbPaymentsApi(PaymentsApi):
    def __init__(self):
        super().__init__()
        header = API.configuration.get_header()
        API.set_default_header('X-WSSE', header['X-WSSE'])
        self.api_client = API
    
    def payments_id_get(self, id, **kwargs):
        kwargs['_return_http_data_only'] = True
        kwargs['_preload_content'] = False
        if kwargs.get('async_req'):
            return self.payments_id_get_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.payments_id_get_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def payments_status_get(self, status, **kwargs):  # noqa: E501
        """Get payment list by status  # noqa: E501

        Request the list of payments that has been created on a specific period of time.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.payments_status_get_with_http_info(status, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str status: A code representing the status of the payments you want to get.  (required)
        :param str from_date: The starting date to search payments.
        :param str to_date: The ending date to search payments.
        :param str page: Index of the page.
        :param str per_page: Inumber of items returned.
        :param str sort: A code representing the order of rendering objects.
        :return: list[Payment]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        kwargs['_preload_content'] = False
        if kwargs.get('async_req'):
            return self.payments_status_get_with_http_info(status, **kwargs)  # noqa: E501
        else:
            (data) = self.payments_status_get_with_http_info(status, **kwargs)  # noqa: E501
            return data
         
    def payments_post(self, payment, **kwargs):  # noqa: E501
        """Submit a payment  # noqa: E501

        You can use this request in order to schedule a new payment.  
        You may want to use the GET `/payments/options/-{walletId}/-{externalBankAccountId}/` 
        before calling this service to get proper values for `feePaymentOption` and `priorityPaymentOption` 
        concerning your payment.  You can also use this request to get the cost of a payment.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.payments_post(payment, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param Payment payment: The payment to post  (required)
        :return: Payment
                 If the method is called asynchronously,
                 returns the request thread.
                 """

        kwargs['_return_http_data_only'] = True
        kwargs['_preload_content'] = False
        if kwargs.get('async_req'):
            return self.payments_post_with_http_info(payment, **kwargs)  # noqa: E501
        else:
            (data) = self.payments_post_with_http_info(payment, **kwargs)  # noqa: E501
            return data
    def check_if_wallet_exist(self, wallet_id:str)-> bool:
        api = IbWalletApi()
        return True  if api.wallets_id_get(wallet_id) else False

    def check_if_external_bank_account_exist(self, external_bank_account_id):
        api = IbExternalBankAccountApi()
        return True if api.external_bank_accounts_id_get(external_bank_account_id) else False

    def payments_options_wallet_id_external_bank_account_id_get(self, wallet_id, external_bank_account_id, **kwargs):  # noqa: E501
        """Get payment options for a wallet and an external bank account  # noqa: E501

        Before doing any payments, you may use this request to get payments options for the payment you want to do. 
        This will give you the `priorityPaymentOption` and `feePaymentOption` available for the given wallet and 
        external bank account. You will also get fee cost for each `priorityPaymentOption` and `feePaymentOption` 
        combinations, and minimal source and target amount to use this combination.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.payments_options_wallet_id_external_bank_account_id_get(wallet_id, external_bank_account_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str wallet_id: The source wallet ID you want to put your payment debit on.  (required)
:param str external_bank_account_id: The target external bank account ID you want to put your payment credit on.  (required)
        :return: PaymentOption
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_preload_content'] = False
        kwargs['_return_http_data_only'] = True
        if self.check_if_external_bank_account_exist(external_bank_account_id) and self.check_if_wallet_exist(wallet_id):
            if kwargs.get('async_req'):
                return self.payments_options_wallet_id_external_bank_account_id_get_with_http_info(wallet_id, external_bank_account_id, **kwargs)  # noqa: E501
            else:
                (data) = self.payments_options_wallet_id_external_bank_account_id_get_with_http_info(wallet_id, external_bank_account_id, **kwargs)  # noqa: E501
                return data

class IbExternalBankAccountApi(ExternalBankAccountApi):
    def __init__(self):
            super().__init__()
            header = API.configuration.get_header()
            API.set_default_header('X-WSSE', header['X-WSSE'])
            self.api_client = API
            
    def external_bank_accounts_get(self, **kwargs):
        """Get external bank accounts list  # noqa: E501

        With the IBANFIRST API, you can list all the external bank accounts referenced with your account.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.external_bank_accounts_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str sort: A code representing the order of rendering external bank accounts with their creation date.
        :param str page: Index of the page.
        :param str per_page: Inumber of items returned.
        :return: list[ExternalBankAccount]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_preload_content'] = False
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.external_bank_accounts_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.external_bank_accounts_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def external_bank_accounts_id_get(self, id, **kwargs):  # noqa: E501
            """Get external bank account details  # noqa: E501

            This request allows you to see the details related to an external bank account.   # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True
            >>> thread = api.external_bank_accounts_id_get(id, async_req=True)
            >>> result = thread.get()

            :param async_req bool
            :param str id: The ID of the external bank account you want. As ID's are listed with the External Bank Account Objects, You can retrieve this by listing all external bank accounts for the current user.   (required)
            :return: ExternalBankAccount
                     If the method is called asynchronously,
                     returns the request thread.
            """
            kwargs['_preload_content'] = False
            kwargs['_return_http_data_only'] = True
            if kwargs.get('async_req'):
                return self.external_bank_accounts_id_get_with_http_info(id, **kwargs)  # noqa: E501
            else:
                (data) = self.external_bank_accounts_id_get_with_http_info(id, **kwargs)  # noqa: E501
                return data


if __name__ == "__main__":
    
    #pay = IbPaymentsApi()
    tt = IbWalletApi()
    to = IbExternalBankAccountApi()
    print("Same" if id(to.api_client.configuration.host) == id(to.api_client.configuration.host) else 'niet!')

