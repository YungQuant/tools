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

from coinbene import create_buy_order, get_orderbook, cancel_all_orders, balances


args = sys.argv

ticker, quantity, r1, r2, T, s1, s2, cooldown = args[1], float(args[2]), int(args[3]), int(args[4]), int(args[5]), int(args[5]), int(args[6]), int(args[7])
#ticker, quantity, aggression, window, ovAgg = "OMX-ETH", 1, 1, 60, 10
sQuantity = quantity
midpoints, spreads = [], []
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        orders = get_orderbook(ticker, limit=99999)['orderbook']
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        bid, ask = float(orders['bids'][0]['price']), float(orders['asks'][0]['price'])
        bVol, aVol = float(orders['bids'][0]['quantity']), float(orders['asks'][0]['quantity'])
        spread = ask - bid
        spreads.append(spread)
        print("Coinsuper RandBuyAsk Version 1 -hugo")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity)
        print("balances:", balances())
        print("starttime:", starttime, "time:", timeStr)
        print("r1:", r1, "r2:", r2, "T:", T)
        t = np.random.uniform(r1, r2)
        print("try:", t, " > ", T, "?")
        if t > T:
            print("client.cancel_all_orders(ticker)")
            print(cancel_all_orders(ticker))
            if quantity <= aVol:
                print("quantity <= aVol", quantity, aVol)
                exit(code=0)
            print("client.create_buy_order(", ticker, ask, np.random.uniform(s1, s2), ")")
            print(create_buy_order(ticker, ask, str(np.random.uniform(s1, s2))[:6]))
            quantity -= aVol

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(cooldown)
    except :
        print("FUUUUUUUUUUCK", sys.exc_info())

