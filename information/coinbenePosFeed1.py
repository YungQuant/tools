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

from coinbene import get_orderbook, post_open_orders, post_balance


def filter_balance(b):
    result = []
    for balance in b['balance']:
        if balance['available'] != '0':
            result.append(balance)
    return result

# def filterActive(active):
#     for a in active:
#         del a['createtime']
#         del a['orderid']
#     return active

args = sys.argv
ticker, d, a = "omxeth", 1, 1
#ticker, d, a = args[1], int(args[2]), int(args[3])

timeCnt, execTrades = 0, 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while (1):
    try:
        orders = get_orderbook(ticker, 10)['orderbook']
        bid, ask = orders['bids'][0]['price'], orders['asks'][0]['price']
        midpoint = np.mean([bid, ask])
        bals = filter_balance(post_balance({ "account": "exchange" }))

        if d == 1:
            pass # print("coinbene doesn't return executed orders")
        if a == 1:
            active = post_open_orders({ "symbol": ticker })['orders']['result']
            #active = filterActive(active_orders)
            #print("active:", active[])
            for i in range(len(active)):
                print("active:", active[i])

        print("PosFeed Version 1 -yungquant")
        print("Ticker:", ticker)
        print("starttime:", starttime)
        print("balances:", bals)
        print("price:", midpoint, "\n")

        time.sleep(10)
        timeCnt += 1
        print("timeCnt:", timeCnt, ",", timeCnt / 6, "minutes\n")
    except:
        print("FUUUUUUUUUUCK", sys.exc_info())
        time.sleep(1)

