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

args = sys.argv
# ticker: OMXETH
ticker, d, a = args[1], int(args[2]), int(args[3])

timeCnt, execTrades = 0, 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while (1):
    try:
        orders = get_orderbook(ticker, 10)['orderbook']
        bid, ask = orders['bids'][0]['price'], orders['asks'][0]['price']
        midpoint = np.mean([bid, ask])
        bals = filter_balance(post_balance({ "account": "exchange" }))

        print("PosFeed Version 1 -yungquant")
        print("Ticker:", ticker)
        print("starttime:", starttime)
        print("balances:", bals)
        print("price:", midpoint, "\n")
        if d == 1:
            pass # print("coinbene doesn't return executed orders")
        if a == 1:
            active_orders = post_open_orders({ "symbol": ticker })
            print("active:", active_orders, "\n")

        time.sleep(1)
        timeCnt += 1
        print("timeCnt:", timeCnt, ",", timeCnt / 60, "minutes\n")
    except:
        print("FUUUUUUUUUUCK", sys.exc_info())
        time.sleep(1)

