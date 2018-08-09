import time
import hashlib
import requests
import json

apiid = '85822c1ac6e3a90897802348f11f4911'
secret = '1ff7386b582a41048f44c1baa3fbed8d'

market_url = "http://api.coinbene.com/v1/market/"
trade_url = "http://api.coinbene.com/v1/trade/"
header_dict = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",\
    "Content-Type":"application/json;charset=utf-8","Connection":"keep-alive"}

def sign(**kwargs):
    sign_list = []
    for key, value in kwargs.items():
        sign_list.append("{}={}".format(key, value))
    sign_list.sort()
    sign_str = "&".join(sign_list)
    mysecret = sign_str.upper().encode()
    m = hashlib.md5()
    m.update(mysecret)
    return m.hexdigest()

def create_timestamp():
    timestamp = int(round(time.time() * 1000))
    return timestamp

def make_params(dic):
    dic['apiid'] = apiid
    dic['secret'] = secret
    dic['timestamp'] = create_timestamp()
    return dic

def http_get_nosign(url):
    return http_request(url, data=None)

def http_post_sign(url,dic):
    dic = make_params(dic)
    mysign = sign(**dic)
    del dic['secret']
    dic['sign'] = mysign
    return http_request(url, data=dic)

def http_request(url, data) :
    if data == None:
        reponse = requests.get(url,headers=header_dict)
    else:
        reponse = requests.post(url,data=json.dumps(data),headers=header_dict)
    try:
        if reponse.status_code == 200:
            return json.loads(reponse.text)
        else:
            return None
    except Exception as e:
        print('http failed : %s' % e)
        return None

def get_ticker(symbol):
    """
    symbol必填，为all或交易对代码:btcusdt
    """
    url = market_url + "ticker?symbol=" + str(symbol)
    return http_get_nosign(url)


def get_orderbook(symbol, depth=200):
    """
    depth为选填项，默认为200
    """
    url = market_url + "orderbook?symbol=" + symbol + "&depth=" + str(depth)
    return http_get_nosign(url)


def get_trade(symbol, size=300):
    """
    size:获取记录数量，按照时间倒序传输。默认300
    """
    url = market_url + "trades?symbol=" + symbol + "&size=" + str(size)
    return http_get_nosign(url)


def post_balance(dic):
    """
    apiid, secret, timestamp, account
    """
    url = trade_url + "balance"
    return http_post_sign(url, dic)


def post_order_place(dic):
    """
    以字典形式传参
    apiid,symbol,timestamp
    type:可选 buy-limit/sell-limit
    price:购买单价
    quantity:购买数量
    """
    url = trade_url + "order/place"
    return http_post_sign(url, dic)


def post_info(dic):
    """
    apiid,timestamp,secret,orderid
    """
    url = trade_url + "order/info"
    return http_post_sign(url, dic)


def post_open_orders(dic):
    """
    apiid,timestamp,secret,symbol
    """
    url = trade_url + "order/open-orders"
    return http_post_sign(url, dic)


def post_cancel(dic):
    """
    apiid,timestamp,secret,orderid
    """
    url = trade_url + "order/cancel"
    return http_post_sign(url, dic)


def create_buy_order(ticker, price, quantity):
    return post_order_place({
        "type": 'buy-limit',
        "price": price,
        "quantity": quantity
    })

def create_sell_order(ticker, price, quantity):
    return post_order_place({
        "type": 'sell-limit',
        "price": price,
        "quantity": quantity
    })
