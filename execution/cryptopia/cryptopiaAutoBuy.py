import json
import time
import hmac
import hashlib
import base64
import requests
import numpy as np
import quandl
import urllib.request
import urllib, time, datetime
import scipy.stats as sp
from matplotlib import pyplot as plt
import os.path
from multiprocessing import Pool
import numpy as np
import time
import hmac
import hashlib
from twilio.rest import Client
# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC822d03400a3abeb205e2ec520eb3dbd7"
auth_token = "753814d986ef6b3fa83302afd83dc324"
client = Client(account_sid, auth_token)
try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin

# using requests.compat to wrap urlparse (python cross compatibility over 9000!!!)
from requests.compat import quote_plus


class Api(object):
    """ Represents a wrapper for cryptopia API """

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.public = ['GetCurrencies', 'GetTradePairs', 'GetMarkets',
                       'GetMarket', 'GetMarketHistory', 'GetMarketOrders', 'GetMarketOrderGroups']
        self.private = ['GetBalance', 'GetDepositAddress', 'GetOpenOrders',
                        'GetTradeHistory', 'GetTransactions', 'SubmitTrade',
                        'CancelTrade', 'SubmitTip', 'SubmitWithdraw', 'SubmitTransfer']

    def api_query(self, feature_requested, get_parameters=None, post_parameters=None):
        """ Performs a generic api request """
        if feature_requested in self.private:
            url = "https://www.cryptopia.co.nz/Api/" + feature_requested
            post_data = json.dumps(post_parameters)
            headers = self.secure_headers(url=url, post_data=post_data)
            req = requests.post(url, data=post_data, headers=headers)
            if req.status_code != 200:
                try:
                    req.raise_for_status()
                except requests.exceptions.RequestException as ex:
                    return None, "Status Code : " + str(ex)
            req = req.json()
            if 'Success' in req and req['Success'] is True:
                result = req['Data']
                error = None
            else:
                result = None
                error = req['Error'] if 'Error' in req else 'Unknown Error'
            return (result, error)
        elif feature_requested in self.public:
            url = "https://www.cryptopia.co.nz/Api/" + feature_requested + "/" + \
                  ('/'.join(i for i in get_parameters.values()
                            ) if get_parameters is not None else "")
            req = requests.get(url, params=get_parameters)
            if req.status_code != 200:
                try:
                    req.raise_for_status()
                except requests.exceptions.RequestException as ex:
                    return None, "Status Code : " + str(ex)
            req = req.json()
            if 'Success' in req and req['Success'] is True:
                result = req['Data']
                error = None
            else:
                result = None
                error = req['Error'] if 'Error' in req else 'Unknown Error'
            return (result, error)
        else:
            return None, "Unknown feature"

    def get_currencies(self):
        """ Gets all the currencies """
        return self.api_query(feature_requested='GetCurrencies')

    def get_tradepairs(self):
        """ GEts all the trade pairs """
        return self.api_query(feature_requested='GetTradePairs')

    def get_markets(self):
        """ Gets data for all markets """
        return self.api_query(feature_requested='GetMarkets')

    def get_market(self, market):
        """ Gets market data """
        return self.api_query(feature_requested='GetMarket',
                              get_parameters={'market': market})

    def get_history(self, market):
        """ Gets the full order history for the market (all users) """
        return self.api_query(feature_requested='GetMarketHistory',
                              get_parameters={'market': market})

    def get_orders(self, market):
        """ Gets the user history for the specified market """
        return self.api_query(feature_requested='GetMarketOrders',
                              get_parameters={'market': market})

    def get_ordergroups(self, markets):
        """ Gets the order groups for the specified market """
        return self.api_query(feature_requested='GetMarketOrderGroups',
                              get_parameters={'markets': markets})

    def get_balance(self, currency):
        """ Gets the balance of the user in the specified currency """
        result, error = self.api_query(feature_requested='GetBalance',
                                       post_parameters={'Currency': currency})
        if error is None:
            result = result[0]
        return (result, error)

    def get_openorders(self, market):
        """ Gets the open order for the user in the specified market """
        return self.api_query(feature_requested='GetOpenOrders',
                              post_parameters={'Market': market})

    def get_deposit_address(self, currency):
        """ Gets the deposit address for the specified currency """
        return self.api_query(feature_requested='GetDepositAddress',
                              post_parameters={'Currency': currency})

    def get_tradehistory(self, market):
        """ Gets the trade history for a market """
        return self.api_query(feature_requested='GetTradeHistory',
                              post_parameters={'Market': market})

    def get_transactions(self, transaction_type):
        """ Gets all transactions for a user """
        return self.api_query(feature_requested='GetTransactions',
                              post_parameters={'Type': transaction_type})

    def submit_trade(self, market, trade_type, rate, amount):
        """ Submits a trade """
        return self.api_query(feature_requested='SubmitTrade',
                              post_parameters={'Market': market,
                                               'Type': trade_type,
                                               'Rate': rate,
                                               'Amount': amount})

    def cancel_trade(self, trade_type, order_id, tradepair_id):
        """ Cancels an active trade """
        return self.api_query(feature_requested='CancelTrade',
                              post_parameters={'Type': trade_type,
                                               'OrderID': order_id,
                                               'TradePairID': tradepair_id})

    def submit_tip(self, currency, active_users, amount):
        """ Submits a tip """
        return self.api_query(feature_requested='SubmitTip',
                              post_parameters={'Currency': currency,
                                               'ActiveUsers': active_users,
                                               'Amount': amount})

    def submit_withdraw(self, currency, address, amount):
        """ Submits a withdraw request """
        return self.api_query(feature_requested='SubmitWithdraw',
                              post_parameters={'Currency': currency,
                                               'Address': address,
                                               'Amount': amount})

    def submit_transfer(self, currency, username, amount):
        """ Submits a transfer """
        return self.api_query(feature_requested='SubmitTransfer',
                              post_parameters={'Currency': currency,
                                               'Username': username,
                                               'Amount': amount})

    def secure_headers(self, url, post_data):
        """ Creates secure header for cryptopia private api. """
        nonce = str(time.time())
        md5 = hashlib.md5()
        jsonparams = post_data.encode('utf-8')
        md5.update(jsonparams)
        rcb64 = base64.b64encode(md5.digest()).decode('utf-8')

        signature = self.key + "POST" + quote_plus(url).lower() + nonce + rcb64
        hmacsignature = base64.b64encode(hmac.new(base64.b64decode(self.secret),
                                                  signature.encode('utf-8'),
                                                  hashlib.sha256).digest())
        header_value = "amx " + self.key + ":" + hmacsignature.decode('utf-8') + ":" + nonce
        return {'Authorization': header_value, 'Content-Type': 'application/json; charset=utf-8'}




def plot(a):
    y = np.arange(len(a))
    plt.plot(y, a, 'g')
    plt.ylabel('Price')
    plt.xlabel('Time Periods')
    plt.show()


def alert_duncan(message):
    m = client.messages.create(
        "+12026316400",
        body=message,
        from_="+12028888138")

    print(m)

def clear_orders(ticker):
    openOrders = api.get_openorders(ticker)
    print("Clearing Open Orders:", openOrders)
    if openOrders[0] == None:
        return "empty"
    orderIds, tradeTypes, tradePairIds = [], [], []
    for i, order in enumerate(openOrders[0]):
        orderIds.append(order['OrderId'])
        tradeTypes.append(order['Type'])
        tradePairIds.append(order["TradePairId"])
    for i, orderId in enumerate(orderIds):
        api.cancel_trade(trade_type=tradeTypes[i], order_id=orderId, tradepair_id=tradePairIds[i])
    print("Cleared Open Orders:", api.get_openorders(ticker))

def force_sell(ticker):
    openOrders = api.get_openorders(ticker)
    print("DEBUG force sell open orders:", openOrders)
    if openOrders[0] == None:
        return "empty"
    mrktInfo = api.api_query(feature_requested="GetMarketOrderGroups", get_parameters={'market': ticker})
    bid, ask = mrktInfo[0][0]['Buy'][0]['Price'], mrktInfo[0][0]['Sell'][0]['Price']
    print("FORCE SELLING Bid:", bid, "Ask:", ask)
    print(api.submit_trade(ticker, 'sell', bid, 5))

def force_buy(ticker):
    openOrders = api.get_openorders(ticker)
    print("DEBUG force buy open orders:", openOrders)
    if openOrders[0] == None:
        return
    mrktInfo = api.api_query(feature_requested="GetMarketOrderGroups", get_parameters={'market': ticker})
    bid, ask = mrktInfo[0][0]['Buy'][0]['Price'], mrktInfo[0][0]['Sell'][0]['Price']
    print("FORCE Buying Bid:", bid, "Ask:", ask)
    print(api.submit_trade(ticker, 'buy', ask, 5))

api = Api(key="3f8b7c40eeb04befb8d0cca362d8c017", secret="hws7Dbh/Nu1nHsRljYwtrdFydzmib6ihfTu2bva0xiE=")
initTimeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
ticker = "BITG_BTC"
ticker1 = "BITG/BTC"
file = "../../../data" + ticker[0] + "_cryptopiaData/"

while(1):
    try:
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||\nAutoBuy start:" + timeStr)
        print("Using:" + ticker + "\n" + file + "\n")
        print("BTC Avail./Total:", api.get_balance("BTC")[0]['Available'], api.get_balance("BTC")[0]['Total'], ticker[:4], "Avail./Total:", api.get_balance(ticker[:4])[0]['Available'], "/", api.get_balance(ticker[:4])[0]['Total'], "\n")
        # if clear_orders(ticker) != "empty":
        #     force_buy(ticker)
        clear_orders(ticker1)
        mrktInfo = api.api_query(feature_requested="GetMarketOrderGroups", get_parameters={'market': ticker})
        # print(mrktInfo[0][0]['Buy'][0]['Price'])
        bid, ask = mrktInfo[0][0]['Buy'][0]['Price'], mrktInfo[0][0]['Sell'][0]['Price']
        print("Bid:", bid, "Ask:", ask)
        print("Submitting Trade on", ticker)
        print(api.submit_trade(ticker, "buy", float(bid), np.random.uniform(1, 2)))

        # print("Submitting MedianTrade on", ticker)
        # print(api.submit_trade(ticker, "buy", np.mean([float(ask), float(bid)]), 2))

        print("Open Orders:", api.get_openorders(ticker))
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        print("AutoBuy end: " + timeStr + "\n||||||||||||||||||||||||||||||||||||||||||||||||||||||")
        time.sleep(30)
    except:
        print("FUUUUUUUUUU")

