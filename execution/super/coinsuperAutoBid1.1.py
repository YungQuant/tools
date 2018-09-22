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

from coinsuper import cancel_all_orders, get_orderbook, create_buy_order

def filter_balance(b):
    result = []
    for balance in b['balance']:
        if balance['available'] != '0':
            result.append(balance)
    return result

args = sys.argv

ticker, quantity, below = args[1], float(args[2]), float(args[3])
#ticker, quantity = "OMX-ETH", 1
sQuantity = quantity
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        print("Coinsuper AutoBuy Version 1.1 -hugo")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity, "below", below)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        balances = filter_balance(post_balance({ "account": "exchange" }))
        print("balances:", balances)
        orders = get_orderbook(ticker, 999999)
        bid, ask = orders['bids'][0]['limitPrice'], orders['asks'][0]['limitPrice']
        midpoint = np.mean([bid, ask])
        print("starttime:", starttime, "time:", timeStr, "midpoint", midpoint)
        if midpoint < below:
            print("client.cancel_all_orders(ticker)")
            print(cancel_all_orders(ticker))

            avgVol = np.mean([float(order['quantity']) for order in orders['bids'][:10]])
            if avgVol > balances[ticker[-3:]]:
                avgVol = balances[ticker[-3:]]
            print("client.create_buy_order(", ticker, str(float(orders['bids'][0]['limitPrice']) * 1.00001), str(np.floor(avgVol / float(orders['bids'][0]['limitPrice']))), ")")
            print(create_buy_order(ticker, float(orders['bids'][0]['limitPrice']) * 1.00001, np.floor(avgVol / float(orders['bids'][0]['limitPrice']))))

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(30)
    except Exception as e:
        print("FUUUUUUUUUUCK",  e)

