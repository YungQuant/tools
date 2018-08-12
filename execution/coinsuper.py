import hashlib
import requests
import time

accesskey = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
secretkey = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
url_prefix = 'http://localhost'


# 验证签名
def get_request_data(params):
    # 组装验签参数
    param_for_sign = params.copy()
    timestamp = int(time.time())
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
    r = requests.post(url_prefix + resource, json=params, timeout=1)
    result = r.json()
    return result


def create_buy_order(ticker, price, volume):
    params = {
        "symbol": ticker,
        "orderType": 'LMT',
        "quantity": quantity,
        'amount': 0, # wtf?
        "priceLimit": price
    }
    return http_post("/api/v1/order/buy", get_request_data(params))

def create_sell_order(ticker, price, volume):
    params = {
        "symbol": ticker,
        "orderType": 'LMT',
        "quantity": quantity,
        'amount': 0, # wtf?
        "priceLimit": price
    }
    return http_post("/api/v1/order/sell", get_request_data(params))
