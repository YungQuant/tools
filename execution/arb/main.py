import gdax
from bittrex import Bittrex
import json, hmac, hashlib, time, requests, base64

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin
import requests

BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

BASE_URL = 'https://bittrex.com/api/v1.1/%s/'

MARKET_SET = {'getopenorders', 'cancel', 'sellmarket', 'selllimit', 'buymarket', 'buylimit'}

ACCOUNT_SET = {'getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorderhistory'}

class Bittrex(object):
    """
    Used for requesting Bittrex with API key and API secret
    """
    def __init__(self, api_key, api_secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''

    def api_query(self, method, options=None):
        """
        Queries Bittrex with given method and options
        :param method: Query method for getting info
        :type method: str
        :param options: Extra options for query
        :type options: dict
        :return: JSON response from Bittrex
        :rtype : dict
        """
        if not options:
            options = {}
        nonce = str(int(time.time() * 1000))
        method_set = 'public'
        if method in MARKET_SET:
            method_set = 'market'
        elif method in ACCOUNT_SET:
            method_set = 'account'

        request_url = (BASE_URL % method_set) + method + '?'

        if method_set != 'public':
            request_url += 'apikey=' + self.api_key + "&nonce=" + nonce + '&'

        request_url += urlencode(options)

        return requests.get(
            request_url,
            headers={"apisign": hmac.new(self.api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()}
        ).json()

    def get_ticker(self, market):
        return self.api_query('getticker', {'market': market})

    def get_orderbook(self, market, depth_type, depth=20):
        return self.api_query('getorderbook', {'market': market, 'type': depth_type, 'depth': depth})

    def cancel(self, uuid):
        return self.api_query('cancel', {'uuid': uuid})

    def get_open_orders(self, market):
        return self.api_query('getopenorders', {'market': market})

    def get_balances(self):
        return self.api_query('getbalances', {})

    def get_balance(self, currency):
        return self.api_query('getbalance', {'currency': currency})

    def get_deposit_address(self, currency):
        return self.api_query('getdepositaddress', {'currency': currency})

    def withdraw(self, currency, quantity, address):
        return self.api_query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})

    def get_order_history(self, market, count):
        return self.api_query('getorderhistory', {'market':market, 'count': count})
        
# b = Bittrex()

auth_client = gdax.AuthenticatedClient('bde025abf416c7030d46e246f9b82f9f', 'nPA2emjTpHuOUVfqitvhOLL4XgdTjywRV21G/18TU9MTJOpwvjPXkZaulms87jrVB97zPsuleD1xHw5+sYKsUg==', 'xr8nind7yob')
COINBASE_ID = ''
# print(auth_client.get_accounts())

# def transfer(org_exchange, dest_exchange, dest_address = 0, ticker, amount):
#     if org_exchange == "gdax" and dest_address == "bittrex":
#         if dest_address == 0:
#             addr = b.getdepositaddress(ticker)
#         auth_client.crypto_withdraw(amount, ticker, dest_address)
    
#     if org_exchange == 'bittrex' and dest_exchange == 'gdax':
#         if dest_address == 0:
#             addr = auth_client.deposit(amount, ticker, COINBASE_ID) # <- not real call
#         b.Withdraw(ticker, amount, dest_address)
        


# Withdraw from GDAX 
# auth_client.crypto_withdraw('1.00','LTC','LhmTyzr2Vpj3KPGanrGg8JoAnjmWbxZUFr')

# my_bittrex = Bittrex("60986d49a16a46fab28c320bf93730f4", "0b4e83a129f54cfaa2b3168e2e15424f")

# print(my_bittrex.withdraw('LTC','1','LY7kuibfErUCQaQjRL74sTXoZMjuHW1LmY'))
