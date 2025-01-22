import ibanfirst_client 
from ibanfirst_client.api_client import ApiClient
from ibanfirst_client.api.wallets_api import WalletsApi


class IbWalletApi(WalletsApi):
    def wallets_get(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        kwargs['_preload_content'] = False
        if kwargs.get('async_req'):
            return self.wallets_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.wallets_get_with_http_info(**kwargs)  # noqa: E501
            return data
    def wallets_id_get(self, id):
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
        

class IBanfirstClient(ApiClient):
    pass


if __name__ == "__main__":
    import json
    class Cust(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, list):
                return ''.join(str(i) for i in obj)
            return super().default(obj)

    ib = IBanfirstClient()
    tt = IbWalletApi()
    #print(dir(tt.api_client))
    tt.api_client.configuration.host = "http://127.0.0.1:8980"
    la = tt.wallets_get(_preload_content=False).json()
    js = json.dumps(la, indent=1)
    print(dir(js))
              
