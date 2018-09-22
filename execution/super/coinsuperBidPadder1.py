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
from coinsuper import cancel_all_orders, get_orderbook, create_buy_order, balances

def filter_balance(b):
    result = []
    for balance in b['balance']:
        if balance['available'] != '0':
            result.append(balance)
    return result
args = sys.argv

ticker, depth, mtu, r1, r2 = args[1], int(args[2]), float(args[3]), int(args[4]), int(args[5])
#ticker, depth, mtu = "OMX-BTC", 50, 0.00000002


print("Coinsuper Bid Padder Version 1 -hugo")
print("Ticker:", ticker, "depth:", depth, "mtu:", mtu, "r1:", r1, "r2:", r2)
# timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
orders = get_orderbook(ticker, limit=99999)
# print("balances:", filterBalances(client.get_all_balances()))
# print("time:", timeStr)
bi, ai = 0, 0

while(1):
    try:
        ps = [order['limitPirce'] for order in orders['bid']]
        for i in range(1, depth):
            ords = str(np.random.uniform(1000, 3000))[:4]
            ordp = ps[0] - (i * mtu)
            if ordp not in ps:
                print("client.create_buy_order(", ticker, str(ordp),
                      ords, ")")
                print(create_buy_order(ticker,ordp,
                                              ords))
                # time.sleep(1)
            if ordp >= ps[0]:
              exit(code=0)
        exit(code=0)

    except kucoin.exceptions.KucoinAPIException as e:
        print("FUUUUUUUCK", e)


