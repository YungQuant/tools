"""
   See https://bittrex.com/Home/Api
"""
from joblib import Parallel, delayed
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

def my_buy(ticker, amount, type):
    if type == 'ask':
        price = b.get_ticker(ticker)['result']['Ask']
        amount /= price
        b.buy_market(ticker, amount)
        print("BUY ticker, price, amount", ticker, price, amount)

    if type == 'bid':
        price = b.get_ticker(ticker)['result']['Bid']
        amount /= price
        b.buy_limit(ticker, amount, price)
        print("BUY ticker, price, amount", ticker, price, amount)

    if type == 'mid':
        tick = b.get_ticker(ticker)['result']
        price = np.mean([float(tick['Ask']), float(tick['Bid'])])
        amount /= price
        b.buy_limit(ticker, amount, price)
        print("BUY ticker, price, amount", ticker, price, amount)

def my_sell(ticker, amount, type):
    if type == 'ask':
        price = b.get_ticker(ticker)['result']['Ask']
        amount /= price
        b.sell_limit(ticker, amount, price)
        print("SELL ticker, price, amount", ticker, price, amount)

    if type == 'bid':
        price = b.get_ticker(ticker)['result']['Bid']
        amount /= price
        b.sell_market(ticker, amount)
        print("SELL ticker, price, amount", ticker, price, amount)

    if type == 'mid':
        tick = b.get_ticker(ticker)['result']
        price = np.mean([float(tick['Ask']), float(tick['Bid'])])
        amount /= price
        b.sell_limit(ticker, amount, price)
        print("SELL ticker, price, amount", ticker, price, amount)

def alert_duncan(message):
    m = client.messages.create(
        "+12026316400",
        body=message,
        from_="+12028888138")

    print(m)

def clear_orders(ticker):
    UUIDs = []
    orders = b.get_open_orders(ticker)['result']
    if orders != []:
        for i in range(len(orders)):
            UUIDs.append(orders[i]['OrderUuid'])
            b.cancel(UUIDs[i])
            print("CANCELED:", orders[i])
    else:
        print("No Orders (", orders,")")


def OLD_auto_buy(ticker, amount, time_limit=10):
    hist_price = [];
    buy_price_book = [];
    buy_vol_book = [];
    sell_price_book = [];
    sell_vol_book = [];
    time_cnt = 0;
    executed = 0;
    stddev = 1.25;
    adj_time_limit = time_limit * 6
    adj_stddev_increment = stddev / adj_time_limit
    while 1:
        time_cnt += 1
        print("OLD_auto_buy Time Count:", time_cnt)
        buy_book = b.get_orderbook(ticker, 'buy', 30)['result']
        sell_book = b.get_orderbook(ticker, 'sell', 30)['result']
        for i in range(30):
            buy_price_book.append(float(buy_book[i]['Rate']))
            buy_vol_book.append(float(buy_book[i]['Quantity']))
        for i in range(30):
            sell_price_book.append(float(sell_book[i]['Rate']))
            sell_vol_book.append(float(sell_book[i]['Quantity']))
        hist_price.append(np.mean([buy_price_book[0], sell_price_book[0]]))
        if time_cnt > adj_time_limit and time_cnt < adj_time_limit * 2 and executed < amount:
            stddev -= adj_stddev_increment * (time_cnt - adj_time_limit)
            adj_amount_intervals = (amount - executed) / ((adj_time_limit - (time_cnt - adj_time_limit)) / 3)
            pos = BBmomma(hist_price, adj_time_limit, stddev)
            print("BBmomma pos:", pos)
            if pos < 0:
                print("Buying", adj_amount_intervals, "at the ask.")
                #my_buy(ticker, adj_amount_intervals, 'ask')
                executed += adj_amount_intervals
            elif pos > 1 and time_cnt % 10 == 0:
                print("MARKET OVERBOUGHT\n RECONFIGURE FOR AGGRESSIVE EXECUTION IF NECESSARY")

        if time_cnt > adj_time_limit and time_cnt % 10 == 0:
            print((time_cnt - adj_time_limit), "/", adj_time_limit)
            print("Executed", executed, "/", amount)

        if time_cnt > (adj_time_limit * 2):
            print("EXECUTION FAILED, RESTARTING NOW")
            time_cnt = adj_time_limit
            stddev += (adj_time_limit * adj_stddev_increment);

        if executed > amount * 0.99:
            for i in range(20): print("EXECUTED", executed, "/", amount)
            break

        time.sleep(10)


def OLD_auto_sell(ticker, amount, time_limit=10):
    hist_price = [];
    buy_price_book = [];
    buy_vol_book = [];
    sell_price_book = [];
    sell_vol_book = [];
    time_cnt = 0;
    executed = 0;
    stddev = 1.25;
    adj_time_limit = time_limit * 6
    adj_stddev_increment = stddev / adj_time_limit
    while 1:
        time_cnt += 1
        print("OLD_auto_sell Time Count:", time_cnt)
        buy_book = b.get_orderbook(ticker, 'buy', 30)['result']
        sell_book = b.get_orderbook(ticker, 'sell', 30)['result']
        for i in range(30):
            buy_price_book.append(float(buy_book[i]['Rate']))
            buy_vol_book.append(float(buy_book[i]['Quantity']))
        for i in range(30):
            sell_price_book.append(float(sell_book[i]['Rate']))
            sell_vol_book.append(float(sell_book[i]['Quantity']))
        hist_price.append(np.mean([buy_price_book[0], sell_price_book[0]]))
        if time_cnt > adj_time_limit + 2 and time_cnt < adj_time_limit * 2 and executed < amount:
            stddev -= adj_stddev_increment * (time_cnt - adj_time_limit)
            adj_amount_intervals = (amount - executed) / ((adj_time_limit - (time_cnt - adj_time_limit)) / 3)
            pos = BBmomma(hist_price, adj_time_limit, stddev)
            print("BBmomma pos:", pos)
            if pos > 1:
                print("Selling", adj_amount_intervals, "at the bid.")
                #my_sell(ticker, adj_amount_intervals, 'bid')
                executed += adj_amount_intervals
            elif pos < 0.1 and time_cnt % 10 == 0:
                print("MARKET OVERSOLD\n RECONFIGURE FOR AGGRESSIVE EXECUTION IF NECESSARY")

        if time_cnt > adj_time_limit and time_cnt % 2 == 0:
            print((time_cnt - adj_time_limit), "/", adj_time_limit)
            print("Executed", executed, "/", amount)

        if time_cnt > (adj_time_limit * 2):
            print("EXECUTION FAILED, RESTARTING NOW")
            time_cnt = adj_time_limit
            stddev += (adj_time_limit * adj_stddev_increment);

        if executed > amount * 0.99:
            for i in range(20): print("EXECUTED", executed, "/", amount)
            break

        time.sleep(10)

def liquidate(ticker):
    bal = float(b.get_balance(ticker)['result']['Balance'])
    amount = bal
    goal_bal = 0
    time_cnt = 0
    while bal > goal_bal:
        tick = b.get_ticker('BTC-' + ticker)['result']
        price = np.mean([float(tick['Ask']), float(tick['Bid'])])
        clear_orders('BTC-' + ticker)
        bal = float(b.get_balance(ticker)['result']['Balance'])
        time_cnt += 1
        print("Liquidate Time Count (10 seconds / cnt):", time_cnt)
        print("Balance:", bal, "Goal Balance:", goal_bal)
        my_sell('BTC-' + ticker, (bal - goal_bal) * price, type='ask')
        time.sleep(10)

def auto_ask(ticker, amount):
    bal = float(b.get_balance(ticker)['result']['Balance'])
    start_bal = bal
    tick = b.get_ticker('BTC-' + ticker)['result']
    price = np.mean([float(tick['Ask']), float(tick['Bid'])])
    goal_bal = bal - (amount / price)
    if goal_bal < 0: goal_bal = 0
    time_cnt = 0
    while bal > goal_bal + (start_bal * 0.001):
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            clear_orders('BTC-' + ticker)
            if ((bal - goal_bal) * price) < 0.001:
                print("insufficient balance")
                time.sleep(60)
            elif ((bal - goal_bal) * price) < 0.1:
                my_sell('BTC-' + ticker, ((bal - goal_bal) * price), type='ask')
            else:
                my_sell('BTC-' + ticker, 0.025, type='ask')
            time_cnt += 1
            print("AUTOASK Time Count (15 seconds / cnt):", time_cnt)
            print("Starting Balance:", start_bal, "Balance:", bal, "Goal Balance:", goal_bal)
            print("\n")
            time.sleep(15)
        except:
            print("AUTO_ASK FAILED ON TIME_CNT:", time_cnt, "(15 seconds / cnt)")

def auto_bid(ticker, amount):
    bal = float(b.get_balance(ticker)['result']['Balance'])
    tick = b.get_ticker('BTC-' + ticker)['result']
    price = np.mean([float(tick['Ask']), float(tick['Bid'])])
    goal_bal = bal + (amount / price)
    time_cnt = 0
    while bal < goal_bal * 0.999:
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            clear_orders('BTC-' + ticker)
            if (goal_bal - bal) * price < 0.05:
                my_buy('BTC-' + ticker, ((goal_bal - bal) * price) * 0.99, type='bid')
            else:
                my_buy('BTC-' + ticker, 0.05, type='bid')
            time_cnt += 1
            print("AUTOBID Time Count:", time_cnt, "(30 seconds / cnt)")
            print("Balance:", bal, "Goal Balance:", goal_bal)
            print("\n")
            time.sleep(30)
        except:
            print("AUTO_BID FAILED ON TIME_CNT:", time_cnt, "(15 seconds / cnt)")


def auto_passive_buy(ticker, amount, target, stop, alerts = 0):
    tick = b.get_ticker('BTC-' + ticker)['result']
    price = np.mean([float(tick['Ask']), float(tick['Bid'])])
    org_bal = float(b.get_balance(ticker)['result']['Balance'])
    goal_bal = org_bal + (amount / price)
    bal = org_bal
    time_cnt = 0
    while bal < goal_bal * 0.999:
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            clear_orders('BTC-' + ticker)

            if price >= target:
                print("Target Reached, Attempting AUTO_ASK\n")
                if alerts == 0: auto_ask(ticker, (bal * price))
                if alerts == 1:
                    try:
                        str_message = "Target reached on" + str(ticker) + "! Amount, Target, Stop:" + str(amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_ask(ticker, (bal * price))
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0
            elif price <= stop:
                print("Stop Reached, Attempting AUTO_AGGRESIVE_SELL\n")
                if alerts == 0: auto_aggresive_sell(ticker, (bal * price))
                elif alerts == 1:
                    try:
                        str_message = "Stop reached on" + str(ticker) + "! Amount, Target, Stop:" + str(
                            amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_aggresive_sell(ticker, (bal * price), alerts=1)
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0

            if (goal_bal - bal) * price < 0.1:
                my_buy('BTC-' + ticker, (goal_bal - bal) * price, type='bid')
            else:
                my_buy('BTC-' + ticker, 0.1, type='bid')
            time_cnt += 1
            print("AUTO_PASSIVE_BUY Time Count:", time_cnt, "(15 seconds / cnt)")
            print("Balance:", bal, "Goal Balance:", goal_bal)
            print("\n")
            time.sleep(15)
        except:
            print("AUTO_PASSIVE_BUY FAILED ON TIME_CNT:", time_cnt, "(15 seconds / cnt)")

    while bal > 0:
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            print("AUTO_PASSIVE_BUY PHASE 2 Time Count:", time_cnt, "(15 seconds / cnt)")
            print("Balance:", bal, "Ticker", ticker)
            print("\n")
            time_cnt += 1
            if price >= target:
                print("Target Reached, Attempting AUTO_ASK\n")
                if alerts == 0: auto_ask(ticker, (bal * price))
                elif alerts == 1:
                    try:
                        str_message = "Target reached on" + str(ticker) + "! Amount, Target, Stop:" + str(
                            amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_ask(ticker, (bal * price))
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0
            elif price <= stop:
                print("Stop Reached, Attempting AUTO_AGGRESIVE_SELL\n")
                if alerts == 0:
                    auto_aggresive_sell(ticker, (bal * price))
                elif alerts == 1:
                    try:
                        str_message = "Stop reached on" + str(ticker) + "! Amount, Target, Stop:" + str(
                            amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_aggresive_sell(ticker, (bal * price), alerts=1)
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0
            time.sleep(15)
        except:
            print("AUTO_PASSIVE_BUY PHASE 2 FAILED ON TIME_CNT:", time_cnt, "(15 seconds / cnt)")


def auto_passive_sell(ticker, amount, target, stop, alerts = 0):
    tick = b.get_ticker('BTC-' + ticker)['result']
    price = np.mean([float(tick['Ask']), float(tick['Bid'])])
    org_bal = float(b.get_balance(ticker)['result']['Balance'])
    goal_bal = org_bal - (amount / price)
    if goal_bal < 0: goal_bal = 0
    bal = org_bal
    time_cnt = 0
    while bal > goal_bal + (org_bal * 0.001):
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            clear_orders('BTC-' + ticker)

            if price <= target:
                print("Target Reached, Attempting AUTO_BID\n")
                if alerts == 0: auto_bid(ticker, (org_bal * price))
                if alerts == 1:
                    try:
                        str_message = "Target reached on" + str(ticker) + "! Amount, Target, Stop:" + str(
                            amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_bid(ticker, (org_bal * price))
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0
            elif price >= stop:
                print("Stop Reached, Attempting AUTO_AGGRESIVE_BUY\n")
                if alerts == 0: auto_aggresive_buy(ticker, (org_bal * price))
                elif alerts == 1:
                    try:
                        str_message = "Stop reached on" + str(ticker) + "! Amount, Target, Stop:" + str(
                            amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_aggresive_buy(ticker, (org_bal * price), alerts=1)
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0

            if (bal * price) < 0.1:
                my_sell('BTC-' + ticker, bal * price, type='ask')
            else:
                my_sell('BTC-' + ticker, 0.1, type='ask')
            time_cnt += 1
            print("AUTO_PASSIVE_SELL Time Count:", time_cnt, "(15 seconds / cnt)")
            print("Balance:", bal, "Goal Balance:", goal_bal)
            print("\n")
            time.sleep(15)
        except:
            print("AUTO_PASSIVE_SELL FAILED ON TIME_CNT:", time_cnt, "(15 seconds / cnt)")

    while bal > 0:
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            print("AUTO_PASSIVE_SELL PHASE 2 Time Count:", time_cnt, "(15 seconds / cnt)")
            print("Balance:", bal, "Ticker", ticker)
            print("\n")
            time_cnt += 1
            if price <= target:
                print("Target Reached, Attempting AUTO_BID\n")
                if alerts == 0: auto_bid(ticker, (org_bal * price))
                elif alerts == 1:
                    try:
                        str_message = "Target reached on" + str(ticker) + "! Amount, Target, Stop:" + str(
                            amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_bid(ticker, (org_bal * price))
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0
            elif price >= stop:
                print("Stop Reached, Attempting AUTO_AGGRESIVE_BUY\n")
                if alerts == 0:
                    auto_aggresive_buy(ticker, (org_bal * price))
                elif alerts == 1:
                    try:
                        str_message = "Stop reached on" + str(ticker) + "! Amount, Target, Stop:" + str(
                            amount) + "," + str(target) + "," + str(stop)
                        alert_duncan(str_message)
                        auto_aggresive_buy(ticker, (org_bal * price), alerts=1)
                    except:
                        for f in range(10): print("ALERT FAILED")
                return 0
            time.sleep(15)
        except:
            print("AUTO_PASSIVE_SELL PHASE 2 FAILED ON TIME_CNT:", time_cnt, "(15 seconds / cnt)")


def auto_aggresive_sell(ticker, amount, alerts = 0):
    tick = b.get_ticker('BTC-' + ticker)['result']
    price = np.mean([float(tick['Ask']), float(tick['Bid'])])
    org_bal = float(b.get_balance(ticker)['result']['Balance'])
    goal_bal = org_bal - (amount / price)
    if goal_bal < 0: goal_bal = 0
    bal = org_bal
    time_cnt = 0
    while bal > goal_bal + (org_bal * 0.001):
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            clear_orders('BTC-' + ticker)
            if (bal * price) < 0.1:
                my_sell('BTC-' + ticker, bal * price, type='bid')
            else:
                my_sell('BTC-' + ticker, 0.1, type='bid')
            time_cnt += 1
            print("AUTO_AGGRESIVE_SELL Time Count:", time_cnt, "(10 seconds / cnt)")
            print("Balance:", bal, "Goal Balance:", goal_bal)
            print("\n")
            time.sleep(10)
        except:
            print("AUTO_AGGRESIVE_SELL FAILED ON TIME_CNT:", time_cnt, "(10 seconds / cnt)")
            if alerts == 1:
                try:
                    str_message = "AUTO AGGRESIVE SELL FAILED!"
                    alert_duncan(str_message)
                except:
                    for f in range(10): print("ALERT FAILED")

def auto_aggresive_buy(ticker, amount, alerts = 0):
    tick = b.get_ticker('BTC-' + ticker)['result']
    price = np.mean([float(tick['Ask']), float(tick['Bid'])])
    org_bal = float(b.get_balance(ticker)['result']['Balance'])
    goal_bal = org_bal + (amount / price)
    bal = org_bal
    time_cnt = 0
    while bal < goal_bal * 0.999:
        try:
            tick = b.get_ticker('BTC-' + ticker)['result']
            price = np.mean([float(tick['Ask']), float(tick['Bid'])])
            bal = float(b.get_balance(ticker)['result']['Balance'])
            clear_orders('BTC-' + ticker)
            if (goal_bal - bal) * price < 0.1:
                my_buy('BTC-' + ticker, (goal_bal - bal) * price, type='ask')
            else:
                my_buy('BTC-' + ticker, 0.1, type='ask')
            time_cnt += 1
            print("AUTO_AGGRESIVE_BUY Time Count:", time_cnt, "(10 seconds / cnt)")
            print("Balance:", bal, "Goal Balance:", goal_bal)
            print("\n")
            time.sleep(10)
        except:
            print("AUTO_AGGRESIVE_BUY FAILED ON TIME_CNT:", time_cnt, "(10 seconds / cnt)")
            if alerts == 1:
                try:
                    str_message = "AUTO AGGRESIVE BUY FAILED!"
                    alert_duncan(str_message)
                except:
                    for f in range(10): print("ALERT FAILED")





#auto_passive_buy("EMC", 0.05, 0.00030000, 0.00010000, alerts=1)
print(auto_bid("XMR", 0.743))

################### VV TO-DO VV ####################
    #trailing stops
    #more nuanced order types
    #adaptive logic

