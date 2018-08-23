import hashlib
import requests
import time

# https://github.com/coinsuperapi/API_docs/wiki#21-%E4%B9%B0%E5%85%A5%E5%A7%94%E6%89%98

accesskey = '8691a3f9-f9cb-4925-bf2c-241650319975'
secretkey = 'a4d55587-c333-4e60-ab28-428435176736'
url_prefix = 'https://api.coinsuper.com'

def get_request_data(params):
    # 组装验签参数
    param_for_sign = params.copy()
    timestamp = int(round(time.time() * 1000))
    param_for_sign["accesskey"] = accesskey
    param_for_sign["secretkey"] = secretkey
    param_for_sign["timestamp"] = timestamp
    sign = '&'.join(['{}={}'.format(k, param_for_sign[k]) for k in sorted(param_for_sign.keys())])
    print('sign: ', sign, ' econded: ', sign.encode("utf8"))
    # 生成签名
    md5_str = hashlib.md5(sign.encode("utf8")).hexdigest()
    # 组装请求参数
    request_data = {
        "common": {
            "accesskey": accesskey,
            "timestamp": timestamp,
            "sign": md5_str
        },
        "data": params
    }
    return request_data


def http_post(resource, params):
    r = requests.post(url_prefix + resource, json=params, timeout=1)
    result = r.json()
    return result


def create_buy_order(ticker, price, quantity):
    params = {
        "symbol": ticker,
        "orderType": 'LMT',
        "quantity": quantity,
        'amount': 0, # wtf?
        "priceLimit": price
    }
    return http_post("/api/v1/order/buy", get_request_data(params))

def create_sell_order(ticker, price, quantity):
    params = {
        "symbol": ticker,
        "orderType": 'LMT',
        "quantity": quantity,
        'amount': 0, # wtf?
        "priceLimit": price
    }
    return http_post("/api/v1/order/sell", get_request_data(params))

def cancel_order(id):
    return http_post("/api/v1/order/cancel", get_request_data({ "orderNo": id }))

def get_orderbook(ticker, limit = 20):
    return http_post("/api/v1/market/orderBook", get_request_data({
        "symbol": ticker,
        "num": limit
    }))['data']['result']


def open_orders():
    return http_post("/api/v1/order/openList", get_request_data({ "num": '1000' }))['data']['result']


def balances():
    response = http_post("/api/v1/asset/userAssetInfo", get_request_data({}))['data']['result']['asset']
    result = {}
    for coin, data in response.items():
        if float(data['total']) > 0:
            result[coin] = data

    return result


