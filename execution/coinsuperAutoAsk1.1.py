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

from coinsuper import balances, get_orderbook

args = sys.argv

ticker, quantity, above = args[1], float(args[2]), float(args[3])
#ticker, quantity, above = "ETH-BTC", 1, 0
sQuantity = quantity
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        print("Coinbene AutoAsk Version 1.1 -hugo")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity, "above:", above)
        balances = balances()
        print("balances:", balances)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        orders = get_orderbook(ticker, 999999)['orderbook']
        bid, ask = orders['bids'][0]['price'], orders['asks'][0]['price']
        midpoint = np.mean([bid, ask])
        print("starttime:", starttime, "time:", timeStr, "midpoint", midpoint)
        if midpoint > above:
            print("client.cancel_all_orders(ticker)")
            print(cancel_all_orders(ticker))

            avgVol = np.mean([float(order['quantity']) for order in orders['asks'][:10]])
            # if avgVol > balances[ticker[:3]]:
            #     avgVol = balances[ticker[:3]]
            print("client.create_sell_order(", ticker, str(float(orders['asks'][0][0])), str(np.floor(avgVol / float(orders['asks'][0][0]))), ")")
            print(create_sell_order(ticker, str(float(orders['asks'][0][0])), str(np.floor(avgVol / float(orders['asks'][0][0])))))

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(60)
    except:
        print("FUUUUUUUUUUCK",  sys.exc_info())

