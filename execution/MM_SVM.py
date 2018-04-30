import time
import hmac
import hashlib
import numpy as np
from sklearn.svm import SVC
from sklearn.linear_model import Ridge, LinearRegression
import os
import urllib.request
import urllib, time, datetime
import scipy.stats as sp
from matplotlib import pyplot as plt
import os.path
from multiprocessing import Pool
from joblib import Parallel, delayed
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
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

def getNum(str):
    tmp = ""
    for i, l in enumerate(str):
        if l.isnumeric() or l == ".":
            tmp += l

    if str[-4:].find('e-') > 0 or str[-4:].find('e+') > 0:
        tmp += str[-3:]

    return float(tmp)

def CryptoQuote1(the_symbol):
    class ohlcvObj():
        open, high, low, close, volume = [], [], [], [], []
    the_url = "https://poloniex.com/public?command=returnChartData&currencyPair={0}&start=1435699200&end=9999999999&period=300".format(the_symbol)
    response = urllib.request.urlopen(the_url).read().decode("utf-8").split(",")
    for i, curr in enumerate(response):
        if curr.find('open') > 0:
            ohlcvObj.open.append(getNum(curr))
        elif curr.find('high') > 0:
            ohlcvObj.high.append(getNum(curr))
        elif curr.find('low') > 0:
            ohlcvObj.low.append(getNum(curr))
        elif curr.find('close') > 0:
            ohlcvObj.close.append(getNum(curr))
        elif curr.find('volume') > 0:
            ohlcvObj.volume.append(getNum(curr))
    return ohlcvObj



class Quote(object):
    DATE_FMT = '%Y-%m-%d'
    TIME_FMT = '%H:%M:%S'

    def __init__(self):
        self.symbol = ''
        self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = ([] for _ in range(7))

    def append(self, dt, open_, high, low, close, volume):
        self.date.append(dt.date())
        self.time.append(dt.time())
        self.open_.append(float(open_))
        self.high.append(float(high))
        self.low.append(float(low))
        self.close.append(float(close))
        self.volume.append(int(volume))

    def to_csv(self):
        return ''.join(["{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n".format(self.symbol,
                                                                                   self.date[bar].strftime('%Y-%m-%d'),
                                                                                   self.time[bar].strftime('%H:%M:%S'),
                                                                                   self.open_[bar], self.high[bar],
                                                                                   self.low[bar], self.close[bar],
                                                                                   self.volume[bar])
                        for bar in range(len(self.close))])

    def write_csv(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_csv())

    def read_csv(self, filename):
        self.symbol = ''
        self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = ([] for _ in range(7))
        for line in open(filename, 'r'):
            symbol, ds, ts, open_, high, low, close, volume = line.rstrip().split(',')
            self.symbol = symbol
            dt = datetime.datetime.strptime(ds + ' ' + ts, self.DATE_FMT + ' ' + self.TIME_FMT)
            self.append(dt, open_, high, low, close, volume)
        return True

    def __repr__(self):
        return self.to_csv()



def create_orderbook_training_set(buy_arr, sell_arr, lookback):
    lookback *= 10
    x, y = [], []
    k = 0
    while k < (len(buy_arr) - lookback):
        x.append(sell_arr[k:k + lookback] + buy_arr[k:k + lookback])
        y.append(np.mean([float(sell_arr[k + lookback]), float(buy_arr[k + lookback])]))
        k += 2
    return np.array(x), np.array(y)

def create_binary_orderbook_training_set(buy_arr, sell_arr, price_arr, lookback):
    #lookback *= 10
    x, y = [], []
    k = 0
    while k < (len(buy_arr) - lookback - 1):
        # for i in range(len(buy_arr[k:k + lookback])):
        #     x.append(buy_arr[k:k + lookback][i])
        # for g in range(len(sell_arr[k:k + lookback])):
        #     x.append(sell_arr[k:k + lookback][g])

        x.append(buy_arr[k:k + lookback] + sell_arr[k:k + lookback])
        if price_arr[k + lookback] > price_arr[k + lookback + 1]:
            y.append(0)
        else:
            y.append(1)

        k += 1
    return np.array(x), np.array(y)

def create_orderbook_magnitude_training_set(buy_arr, sell_arr, lookback):
    lookback *= 10
    x, y = [], []
    k = 0
    while k < (len(buy_arr) - lookback):
        x.append(sell_arr[k:k + lookback] + buy_arr[k:k + lookback])
        y.append((np.mean([float(sell_arr[k + lookback]), float(buy_arr[k + lookback])]) -
                 np.mean([float(sell_arr[k + lookback - 2]), float(buy_arr[k + lookback - 2])])) /
                 np.mean([float(sell_arr[k + lookback - 2]), float(buy_arr[k + lookback - 2])]))
        k += 2
    return np.array(x), np.array(y)

def books2arrays(buy_tick, sell_tick):
    buy_arr, sell_arr = [], []
    with open(buy_tick, 'r') as bf:
        with open(sell_tick, 'r') as sf:
            buy_file = bf.readlines()
            sell_file = sf.readlines()
            if len(buy_file) != len(sell_file): print(buy_tick, "SCRAPER DATA LENGTH DISCREPANCY!!!!")
            for i in range(min([len(buy_file), len(sell_file)])):
                bObj = buy_file[i].split("\t")
                sObj = sell_file[i].split("\t")
                bp, bv = bObj[0], bObj[1]
                sp, sv = sObj[0], sObj[1]
                buy_arr.append(float(bp))
                buy_arr.append(float(bv))
                sell_arr.append(float(sp))
                sell_arr.append(float(sv))
    bf.close()
    sf.close()
    return buy_arr, sell_arr

def books_to_arrays(buy_book, sell_book, depth):
    BB_array, SB_array = [], []
    for i in range(depth):
        #try:
        #print("DEBUG:", i)
        BB_array.append(buy_book['result'][i]['Rate'] * buy_book['result'][i]['Quantity'])
        SB_array.append(sell_book['result'][i]['Rate'] * sell_book['result'][i]['Quantity'])
        # except:
        #     print("Your Data is Fucked Bro")
    price = np.mean([buy_book['result'][0]['Rate'], sell_book['result'][0]['Rate']])
    return BB_array, SB_array, price


class GoogleIntradayQuote(Quote):
    ''' Intraday quotes from Google. Specify interval seconds and number of days '''

    def __init__(self, symbol, interval_seconds=60, num_days=10):
        super(GoogleIntradayQuote, self).__init__()
        self.symbol = symbol.upper()
        url_string = "http://www.google.com/finance/getprices?q={0}".format(self.symbol)
        url_string += "&i={0}&p={1}d&f=d,o,h,l,c,v".format(interval_seconds, num_days)
        thing = urllib.request.urlopen(url_string)
        csv = thing.read().decode('utf-8').split('\n')
        for bar in range(7, len(csv)):
            if csv[bar].count(',') != 5: continue
            offset, close, high, low, open_, volume = csv[bar].split(',')
            if offset[0] == 'a':
                day = float(offset[1:])
                offset = 0
            else:
                offset = float(offset)
            open_, high, low, close = [float(x) for x in [open_, high, low, close]]
            dt = datetime.datetime.fromtimestamp(day + (interval_seconds * offset))
            self.append(dt, open_, high, low, close, volume)


def create_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 5):
        a = dataset[i:(i+look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back + 5])
    return np.array(dataX), np.array(dataY)

def plot(a):
    y = np.arange(len(a))
    plt.plot(y, a, 'g')
    plt.ylabel('Price')
    plt.xlabel('Time Periods')
    plt.show()

def plot2(a, b):
    y = np.arange(len(a))
    plt.plot(y, a, 'g', y, b, 'r')
    plt.ylabel('Price')
    plt.xlabel('Time Periods')
    plt.show()



b = Bittrex('4d314f07d8fb4c6a89622846b30e918e', 'e67bdd178aba478d954f54b6e5afccf7')
ticker = 'BTC-BCC'; LOOKBACK = 5; DEPTH = 10; MODULO = 60;
time_cnt = 0
HIST_BID_BOOK = []; HIST_ASK_BOOK = []; HIST_PRICE = [];

while 1:

    buy_book = b.get_orderbook(ticker, 'buy', DEPTH)#['result']
    sell_book = b.get_orderbook(ticker, 'sell', DEPTH)#['result']

    BB_array, SB_array, price = books_to_arrays(buy_book, sell_book, DEPTH)
    #print("DEBUG BB_array, SB_array, price:", BB_array, SB_array, price)
    #print("DEBUG HIST_BID_BOOK, HIST_ASK_BOOK, HIST_PRICE:", HIST_BID_BOOK, HIST_ASK_BOOK, HIST_PRICE)

    if time_cnt > MODULO:#0 and time_cnt % MODULO == 0:
        #scaler = MinMaxScaler(feature_range=(-1, 1))
        #scaler = StandardScaler()
        #print("DEBUG HIST_BID_BOOK, HIST_ASK_BOOK, HIST_PRICE:", HIST_BID_BOOK, HIST_ASK_BOOK, HIST_PRICE)
        X, Y = create_binary_orderbook_training_set(HIST_BID_BOOK[:-LOOKBACK], HIST_ASK_BOOK[:-LOOKBACK], HIST_PRICE[:-LOOKBACK], LOOKBACK)
        #print("Post-Creation DEBUG X, Y:", X, Y)
        X = np.reshape(X, [X.shape[0], X.shape[1] * DEPTH])
        #scaler = MinMaxScaler().partial_fit(X)
        #print("Post-Shaping DEBUG X, Y:", X, Y)
        #X = scaler.fit_transform(X)
        #print("Post-Scaling DEBUG X:", X)
        print("Formatted data, generating model.")
        # R = Ridge(alpha=a, fit_intercept=True, normalize=True)
        # R = LinearRegression(fit_intercept=True, normalize=True, n_jobs=8)
        R = SVC()
        print("Fitting model.")
        print(R.fit(X, Y))
        x = HIST_BID_BOOK[-LOOKBACK:] + HIST_ASK_BOOK[-LOOKBACK:]
        #print("Post-Creation DEBUG x:", x)
        x = np.reshape(x, [1, (DEPTH * LOOKBACK) * 2])
        #print("Post-Shaping DEBUG x:", x)
        print("Predicting based on unseen data:")
        pred = R.predict(x)
        #err = abs(pred - y)
        print("PREDICTED:", pred, "PRICES[-5:]", HIST_PRICE[-5:])#"ERROR:", err)


    print("time_cnt:", time_cnt, "(1 second / cnt) MODULO:", MODULO, "\n")
    HIST_BID_BOOK.append(BB_array)
    HIST_ASK_BOOK.append(SB_array)
    HIST_PRICE.append(price)
    time_cnt += 1
    time.sleep(1)