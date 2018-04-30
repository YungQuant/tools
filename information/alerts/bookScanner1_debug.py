from twilio.rest import Client
from joblib import Parallel, delayed
import gdax
import numpy as np
import time
import hmac
import hashlib
from twilio.rest import Client

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin
import requests

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC822d03400a3abeb205e2ec520eb3dbd7"
auth_token = "753814d986ef6b3fa83302afd83dc324"
client = Client(account_sid, auth_token)

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

    def get_markets(self):
        return self.api_query('getmarkets')

    def get_currencies(self):
        return self.api_query('getcurrencies')

    def get_ticker(self, market):
        return self.api_query('getticker', {'market': market})

    def get_market_summaries(self):
        return self.api_query('getmarketsummaries')

    def get_orderbook(self, market, depth_type, depth=20):
        return self.api_query('getorderbook', {'market': market, 'type': depth_type, 'depth': depth})

    def get_market_history(self, market, count):
        return self.api_query('getmarkethistory', {'market': market, 'count': count})

    def buy_market(self, market, quantity):
        return self.api_query('buymarket', {'market': market, 'quantity': quantity})

    def buy_limit(self, market, quantity, rate):
        return self.api_query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_market(self, market, quantity):
        return self.api_query('sellmarket', {'market': market, 'quantity': quantity})

    def sell_limit(self, market, quantity, rate):
        return self.api_query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

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

b = Bittrex('4d314f07d8fb4c6a89622846b30e918e', 'e67bdd178aba478d954f54b6e5afccf7')
# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC822d03400a3abeb205e2ec520eb3dbd7"
auth_token = "753814d986ef6b3fa83302afd83dc324"
client = Client(account_sid, auth_token)


def alert_duncan(message):
    m = client.messages.create(
        "+12026316400",
        body=message,
        from_="+12028888138")

    print(m)

def scan_c(ticker):
    return b.get_orderbook(ticker, "buy", 99999999)['result'], b.get_orderbook(ticker, "sell", 99999999)['result']

def lite_scan_c(ticker):
    return b.get_orderbook(ticker, "buy", 1)['result'], b.get_orderbook(ticker, "sell", 1)['result']

def lite_scan_g(ticker):
    return gdax.PublicClient().get_product_order_book(ticker, 1)

def format_d(buy_book, sell_book):
    buy_size_arr, buy_price_arr, sell_size_arr, sell_price_arr = [],[],[],[]
    for i in range(len(buy_book)):
        buy_price_arr.append(buy_book[i]['Rate'])
        buy_size_arr.append(buy_book[i]['Quantity'])
    for k in range(len(sell_book)):
        sell_price_arr.append(sell_book[k]['Rate'])
        sell_size_arr.append(sell_book[k]['Quantity'])
    return buy_size_arr, buy_price_arr, sell_size_arr, sell_price_arr


def landon(cryptos):
    pairs = [];
    for i in range(len(cryptos)):
        pairs.append('BTC-' + cryptos[i])
    while 1:
        try:
            for i in range(len(pairs)):
                buy_book, sell_book = scan_c(pairs[i])
                buy_size_arr, buy_price_arr, sell_size_arr, sell_price_arr = format_d(buy_book, sell_book)
                print(pairs[i], "Price:", np.mean([min(sell_price_arr), max(buy_price_arr)]), "Largest Bid:", max(buy_size_arr), "Largest Ask:", max(sell_size_arr))

                if max(buy_size_arr) > (np.mean(buy_size_arr) * 100):
                    print("********* Max Bid Size > (100 x Avg Bid Size) ****************")
                if max(buy_size_arr[:int(np.floor(len(buy_size_arr) * 0.1))]) > (np.mean(buy_size_arr) * 100):
                    print("********* Max Bid Size in First 10% of Orders > (100 x Avg Bid Size) ****************")

                print("\n")


                #print("DEBUG:", buy_size_arr, "\n", buy_price_arr, "\n", sell_size_arr, "\n", sell_price_arr)


            print("Sleeping for 10 seconds...\n\n\n")
            time.sleep(10)

        except:
            print("Sorry, I've broken.")
            #time.sleep(5)

def bittrex_price_alerts(cryptos, prices):
    pairs = [];
    for i in range(len(cryptos)):
        pairs.append('BTC-' + cryptos[i])
    try:
        for i in range(len(pairs)):
            buy_book, sell_book = lite_scan_c(pairs[i])
            buy_size_arr, buy_price_arr, sell_size_arr, sell_price_arr = format_d(buy_book, sell_book)
            print(pairs[i], np.mean([buy_price_arr, sell_price_arr]))


        print("Sleeping for 10 seconds...")
        time.sleep(10)

    except:
        print("Sorry, I've broken.")


def gdax_price_alerts(pairs, prices):
    for i in range(len(pairs)):
        res = lite_scan_g(pairs[i])
        print(pairs[i], res)
        p = np.mean([float(res['bids'][0][0]), float(res['asks'][0][0])])
        if p > prices[i][0]:
            alert_duncan(str(pairs[i]) + str(p))
        elif p < prices[i][1]:
            alert_duncan(str(pairs[i]) + str(p))

    print("Sleeping for 10 seconds...")
    time.sleep(10)




cryptos = ['NEO', 'GNT', 'ZEC', 'XMR', 'XEM', 'DASH', 'MAID', 'STORJ', 'XRP', 'LTC', 'ETH']
g_cs = ['BTC-USD']
prices = [[0.5, 0.5]]
#landon(cryptos)
gdax_price_alerts(g_cs, prices)





################ VV TO-DO VV ###############
#look for large bids, watch post, see if hit & how large hit, record time on board
#text alerts via twilio