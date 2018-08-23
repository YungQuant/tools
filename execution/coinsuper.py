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
    r = requests.post(url_prefix + resource, json=params, timeout=5)
    result = r.json()
    return result


def create_buy_order(ticker, price, quantity):
    params = {
        "symbol": ticker,
        "orderType": 'LMT',
        "quantity": quantity,
        'amount': 0, # wtf?
        "priceLimit": '%f' % price
    }
    return http_post("/api/v1/order/buy", get_request_data(params))

def create_sell_order(ticker, price, quantity):
    params = {
        "symbol": ticker,
        "orderType": 'LMT',
        "quantity": quantity,
        'amount': 0, # wtf?
        "priceLimit": '%f' % price
    }
    return http_post("/api/v1/order/sell", get_request_data(params))

def open_orders():
    return http_post("/api/v1/order/openList", get_request_data({ "num": '1000' }))['data']['result']

def cancel_order(id):
    return http_post("/api/v1/order/cancel", get_request_data({ "orderNo": id }))

def cancel_all_orders():
    orders = open_orders()
    for id in orders:
        cancel_order(id)

def all_floats(order):
    for k, v in order.items():
        order[k] = float(order[k])
    return order


def get_orderbook(ticker, limit = 20):
    response = http_post("/api/v1/market/orderBook", get_request_data({
        "symbol": ticker,
        "num": limit
    }))
    result = response['data']['result']
    result['asks'] = list(map(all_floats, result['asks']))
    result['bids'] = list(map(all_floats, result['bids']))
    return result

# {'action': 'BUY', 'amount': '0.00000000', 'amountRemaining': '0.00000000', 'fee': '0.00000000', 'orderNo': 1609502468891668481, 'orderType': 'LMT', 'priceLimit': '0.00000103', 'quantity': '141.60040000', 'quantityRemaining': '141.60040000',
 # 'state': 'UNDEAL', 'symbol': 'OMX/BTC', 'utcCreate': 1534941166781, 'utcUpdate': 1534941166832}

def clean_order_details(order):
    del order['fee']
    del order['orderNo']
    del order['orderType']
    del order['amount']
    del order['amountRemaining']
    del order['utcCreate']
    del order['utcUpdate']
    del order['state']
    return order

def order_details(ids):
    # you can only get order details 50 orders at a time
    chunks = [ids[0:50]]
    while len(ids) > 0:
        chunks.append(ids[0:50])
        del ids[0:50]

    result = []
    for chunk in chunks:
        response = http_post("/api/v1/order/list", get_request_data({
            "orderNoList": ",".join(chunk)
        }))
        orders = response['data']['result']
        orders = list(map(clean_order_details, orders))
        result = result + orders
    return result


def all_order_details():
    orders = open_orders()
    ids = []
    for id in orders:
        ids.append(id)
    return order_details(ids)

def balances():
    response = http_post("/api/v1/asset/userAssetInfo", get_request_data({}))
    data = response['data']['result']['asset']
    result = {}
    for coin, data in data.items():
        if float(data['total']) > 0:
            result[coin] = data

    return result


