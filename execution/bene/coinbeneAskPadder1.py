import sys
import os
import json
import time
import hmac
import hashlib
import base64
import requests
import numpy as np
import urllib.request
import urllib, time, datetime
import os.path
import time
import hmac
import hashlib
from decimal import *
try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin

from coinbene import post_balance

def filter_balance(b):
    result = []
    for balance in b['balance']:
        if balance['available'] != '0':
            result.append(balance)
    return result

args = sys.argv

ticker, depth, mtu = args[1], float(args[2]), float(args[3])
#ticker, depth, mtu = "OMX-BTC", 50, 0.00000001


print("Coinbene Ask Padder Version 1 -hugo")
print("Ticker:", ticker, "depth:", depth, "mtu:", mtu)
timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
orders = get_orderbook(ticker, 999999)['orderbook']
print("balances:", filter_balance(post_balance({ "account": "exchange" })))
print("time:", timeStr)
bi, ai = 0, 0

while(1):
    try:
        ps = [order['price'] for order in orders['asks']]
        for i in range(1, depth):
            ords = str(np.random.uniform(2000, 5000))[:4]
            ordp = ps['price'] + (i * mtu)
            if ordp not in ps:
                print("client.create_sell_order(", ticker, str(ordp),
                      ords, ")")
                print(client.create_sell_order(ticker, str(ordp),
                                              ords))
                # time.sleep(1)
            if ordp <= ps['price']:
              exit(code=0)
        exit(code=0)

    except kucoin.exceptions.KucoinAPIException as e:
        print("FUUUUUUUCK", e)


