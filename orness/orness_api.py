
from ibanfirst_client.api_client import ApiClient
from ibanfirst_client.api.wallets_api import WalletsApi
from ibanfirst_client.api.payments_api import PaymentsApi
from ibanfirst_client.api.external_bank_account_api import ExternalBankAccountApi
from ibanfirst_client.api.financial_movements_api import FinancialMovementsApi
from ibanfirst_client.api.logs_api import LogsApi
from ibanfirst_client.rest import ApiException
from orness.config import Config




def generate_api_with_default_header():
    """
    Creates an ApiClient instance with a default header.

    This function initializes an ApiClient instance with configuration
    settings from the Config class. It then retrieves the header from the
    configuration and sets the 'X-WSSE' header for the ApiClient. Finally,
    it returns the configured ApiClient instance.

    :return: An ApiClient instance with the 'X-WSSE' header set.
    :rtype: ApiClient
    """

    API = ApiClient(configuration=Config())
    header = API.configuration.get_header()
    API.set_default_header('X-WSSE', header['X-WSSE'])
    return API


class IbWalletApi(WalletsApi):
    """_IbWalletApi operations  
    """
    def __init__(self):
        """
        Constructor for the class.
        It sets the variables from the environment variables.
        """
        super().__init__()
        
        self.api_client = generate_api_with_default_header()

    def wallets_get(self, **kwargs):
        """Get wallet list  # noqa: E501

        With the Retrieve wallet list service, you can list obtain the list of all wallet account hold with IBANFIRST. 
        The object return in the Array is a simplified version of the Wallet providing you the main information on 
        the wallet without any additional request.    # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.wallets_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str page: Index of the page. 
        :param str per_page: Inumber of items returned. 
        :param str sort: A string representing the rendering order of objects. For wallet objects, the sorting is 
        made by wallet's creation date. 
        :return: list[InlineResponse200]
                If the method is called asynchronously,
                returns the request thread.
        """
        kwargs['_preload_content'] = False
        return super().wallets_get(**kwargs)

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
        
        kwargs['_preload_content'] = False
        return super().wallets_id_get(id, **kwargs)
        
    def wallets_post(self, wallet, **kwargs):  # noqa: E501

        """Submit a new wallet  # noqa: E501

        This request allows you to submit a new wallet.   **Caution :** The holder object in the parameters will only 
        be considered if you suscribed to the `Multi account per currency with holder` wallet option.   # noqa: E501
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
        
        kwargs['_preload_content'] = False
        return super().wallets_post(wallet, **kwargs)
        

class IbPaymentsApi(PaymentsApi):
    def __init__(self):
        super().__init__()
        self.api_client = generate_api_with_default_header()
    
    def payments_id_get(self, id, **kwargs):
       
        kwargs['_preload_content'] = False
        return super().payments_id_get(id, **kwargs)

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
        kwargs['_preload_content'] = False
        return super().payments_status_get(status, **kwargs)
         
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
        :param Payment json: The payment to post  (required)
        :return: Payment
                 If the method is called asynchronously,
                 returns the request thread.
                 """
        
        kwargs['_preload_content'] = False
        return super().payments_post(payment, **kwargs) 

    def payments_options_wallet_id_external_bank_account_id_get(self, wallet_id, external_bank_account_id, **kwargs):  # noqa: E501
        """Get payment options for a wallet and an external bank account  # noqa: E501

        Before doing any payments, you may use this request to get payments options for the payment you want to do. 
        This will give you the `priorityPaymentOption` and `feePaymentOption` available for the given wallet and 
        external bank account. You will also get fee cost for each feePaymentOpti`priorityPaymentOption` and `feePaymentOption` 
        combinations, and minimal source and target amount to use this combination.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.payments_options_wallet_id_external_bank_account_id_get(wallet_id, external_bank_account_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str wallet_id: The source wallet ID you want to put your payment debit on.  (required)
:       param str external_bank_account_id: The target external bank account ID you want to put your payment credit on.  (required)
        :return: PaymentOption
                 If the method is called asynchronously,
                 returns the request thread.
        """
        
        kwargs['_preload_content'] = False
        return super().payments_options_wallet_id_external_bank_account_id_get(wallet_id, external_bank_account_id, **kwargs)
            
    def payments_id_delete(self, id, **kwargs):
        """Delete a payemt  # noqa: E501

        The code identifying the payment you want to delete.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.payments_id_delete(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: The code identifying the payment you want to delete.  (required)
        :return: Payment
                 If the method is called asynchronously,
                 returns the request thread.
        """
        
        kwargs['_preload_content'] = False
        return super().payments_id_delete(id, **kwargs)

    
    def payments_id_confirm_put(self, id, **kwargs):
        """
        Confirm a payment

        Payments that have been scheduled must be confirmed in order to be released.
        If the payment is not confirmed before the end of the scheduled date of operation,
        it will be automatically postponed to the next available operation date.

        :param str id: The code identifying the payment you want to confirm. (required)
        :param async_req bool: Execute request asynchronously
        :return: Payment
                If the method is called asynchronously,
                returns the request thread.
        """
        kwargs['_preload_content'] = False
        return super().payments_id_confirm_put(id, **kwargs)
    def payments_id_proof_of_transaction_put(self, body, id, **kwargs):
        """Upload a proof of transaction for a payment

        We may ask you to provide a proof of transaction under specific terms. You can anticipate our 
        request and send us your invoice or the ID of the beneficiary to avoid any request from us and 
        fully automate your payment process.<br /> To send a file with this request, you have to 
        extract the content of the file with a binary format, and encode it with a base64 algorithm 
        to put in in the “file” field. 

        Args:
            body (ProofOfTransaction): The proof of transaction to upload (file , tag and documentType)
            id (str): The code identifying the payment you want to confirm.

        Returns:
            Payment: _description_
        """
        kwargs['_preload_content'] = False
        return super().payments_id_proof_of_transaction_put(body, id, **kwargs)

class IbExternalBankAccountApi(ExternalBankAccountApi):
    def __init__(self):
        """
        Constructor for IbExternalBankAccountApi
        The IbExternalBankAccountApi class is used to interact with the External Bank Account API.
        """
        super().__init__()
        self.api_client = generate_api_with_default_header()
            
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
        return super().external_bank_accounts_get(**kwargs)

    def external_bank_accounts_id_get(self, id, **kwargs):  # noqa: E501
            """Get external bank account details  # noqa: E501

            This request allows you to see the details related to an external bank account.   # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True
            >>> thread = api.external_bank_accounts_id_get(id, async_req=True)
            >>> result = thread.get()

            :param async_req bool
            :param str id: The ID of the external bank account you want. As ID's are listed with the External Bank Account Objects, 
            You can retrieve this by listing all external bank accounts for the current user.   (required)
            :return: ExternalBankAccount
                     If the method is called asynchronously,
                     returns the request thread.
            """
            kwargs['_preload_content'] = False
            return super().external_bank_accounts_id_get(id, **kwargs)

    def external_bank_accounts_post(self, external_bank_account, **kwargs):  # noqa: E501
            """Submit a new external bank account  # noqa: E501

            This request allows you to submit a new external bank account.   # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True
            >>> thread = api.external_bank_accounts_post(external_bank_account, async_req=True)
            >>> result = thread.get()

            :param async_req bool
            :param ExternalBankAccount external_bank_account: The external bank account to create  (required)
            :return: ExternalBankAccount
                     If the method is called asynchronously,
                     returns the request thread.
            """
            kwargs['_preload_content'] = False
            return super().external_bank_accounts_post(external_bank_account, **kwargs)
    def external_bank_accounts_id_delete(self, id, **kwargs):  # noqa: E501
            """Delete an external bank account  # noqa: E501

            The code identifying the external bank account you want to delete.   # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True
            >>> thread = api.external_bank_accounts_id_delete(id, async_req=True)
            >>> result = thread.get()

            :param async_req bool
            :param str id: The code identifying the external bank account you want to delete.  (required)
            :return: ExternalBankAccount
                     If the method is called asynchronously,
                     returns the request thread.
            """
            kwargs['_preload_content'] = False
            return super().external_bank_accounts_id_delete(id, **kwargs)
    

class IbLogsApi(LogsApi):
    def __init__(self):
        super().__init__()
        self.api_client = generate_api_with_default_header()
    
    def logs_get(self, **kwargs):
        kwargs['_preload_content'] = False
        return super().logs_get(**kwargs)
    
    def logs_id_get(self, id, **kwargs):
        kwargs['_preload_content'] = False
        return super().logs_id_get(id, **kwargs)

class IbFinancialMovementsApi(FinancialMovementsApi):
    def __init__(self):
        super().__init__()
        self.api_client = generate_api_with_default_header()
    
    def financial_movements_get(self, **kwargs):
        kwargs['_preload_content'] = False
        return super().financial_movements_get(**kwargs)
    
    def financial_movements_id_get(self, id, **kwargs):
        kwargs['_preload_content'] = False  
        return super().financial_movements_id_get(id, **kwargs)
   
if __name__ == "__main__":
    import pprint 
    
    to = IbLogsApi()
    print(to.api_client.default_headers)
    tt = pprint.pformat(to.logs_get().json())
    print(tt)
    

