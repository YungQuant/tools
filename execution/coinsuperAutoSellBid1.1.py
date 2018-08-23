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

args = sys.argv

ticker, quantity, aggression, window, ovAgg, depth = args[1], float(args[2]), float(args[3]), float(args[4]), float(args[5]), float(args[6])
#ticker, quantity, aggression, window, ovAgg = "OMX-ETH", 1, 1, 60, 10
sQuantity = quantity
midpoints, spreads = [], []
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        orders = get_orderbook(ticker, 999999)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        bid, ask = float(orders['bids'][0]['limitPrice']), float(orders['asks'][0]['limitPrice'])
        bVol, aVol = float(orders['bids'][0]['quantity']), float(orders['asks'][0]['quantity'])
        spread = bVol
        spreads.append(spread)
        print("Coinbene AutoSellBid Version 1.1 -hugo")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity, "window:", window, "aggression:", aggression, "ovAgg:", ovAgg, "depth:", )
        print("balances:", balances())
        print("starttime:", starttime, "time:", timeStr)
        if len(spreads) > window and timeCnt % ovAgg == 0:
            spreadStd = np.std(spreads[:])
            spreadMean = np.mean(spreads[:])
            print("spread:", spread, "spreadT:", spreadMean + (spreadStd * aggression), "spreadMean:", spreadMean, "spreadStd:", spreadStd, )
            if spread > spreadMean + (spreadStd * aggression):
                print("client.cancel_all_orders(ticker)")
                print(cancel_all_orders(ticker))
                if quantity <= bVol:
                    print("quantity <= aVol", quantity, aVol)
                    exit(code=0)
                print("client.create_sell_order(", ticker, bid, bVol, ")")
                print(create_sell_order(ticker, bid, str(bVol/bid)[:5]))
                quantity -= aVol

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(1)
    except kucoin.exceptions.KucoinAPIException as e:
        print("FUUUUUUUUUUCK",  e)

