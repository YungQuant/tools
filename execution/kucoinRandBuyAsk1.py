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

import kucoin
from kucoin.client import Client
kucoin_api_key = 'api_key'
kucoin_api_secret = 'api_secret'
# client = Client(
#     api_key= '5b579193857b873dcbd2eceb',
#     api_secret= '0ca53c55-39d2-45aa-8a75-cbeb7c735d26')
client = Client(
    api_key= '5b648d9908d8b114d114636f',
    api_secret= '7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0')

def getImpact(buys, sells, size=1.0):
    bidVol = 0
    bidInitPrice = buys[0][0]
    for k in range(len(buys)):
        bidVol += buys[k][-1]
        #print(f'bidVol: {bidVol}')
        if bidVol >= size:
            #print("bidVol >= size")
            askImpacts = bidInitPrice-buys[k][0]
            break
        elif k == len(buys) - 1:
            askImpacts = bidInitPrice
            break

    askVol = 0
    askInitPrice = sells[0][0]
    for k in range(len(sells)):
        askVol += sells[k][-1]
        #print(f'askvol:{askVol}')
        if askVol >= size:
            #print("askVol >= size")
            bidImpacts = sells[k][0]-askInitPrice
            break
        elif k == len(sells) - 1:
            bidImpacts = (1)
            break

    return bidImpacts, askImpacts

def filterBalances(balances):
    retBals = {}
    for i in range(len(balances)):
        if balances[i]['balance'] != 0:
            retBals[balances[i]['coinType']] = balances[i]['balance']
    return retBals

args = sys.argv

ticker, quantity, r1, r2, T, s1, s2, cooldown = args[1], float(args[2]), int(args[3]), int(args[4]), int(args[5]), int(args[5]), int(args[6]), int(args[7])
#ticker, quantity, aggression, window, ovAgg = "OMX-ETH", 1, 1, 60, 10
sQuantity = quantity
midpoints, spreads = [], []
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        orders = client.get_order_book(ticker, limit=99999)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        bid, ask = float(orders['BUY'][0][0]), float(orders['SELL'][0][0])
        bNatVol, aNatVol = float(orders['BUY'][0][1]), float(orders['SELL'][0][1])
        bVol, aVol = float(orders['BUY'][0][2]), float(orders['SELL'][0][2])
        spread = ask - bid
        spreads.append(spread)
        print("Kucoin RandBuyAsk Version 1 -yungquant")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity)
        print("balances:", filterBalances(client.get_all_balances()))
        print("starttime:", starttime, "time:", timeStr)
        print("r1:", r1, "r2:", r2, "T:", T)
        t = np.random.uniform(r1, r2)
        print("try:", t, " > ", T, "?")
        if t > T:
            print("client.cancel_all_orders(ticker)")
            print(client.cancel_all_orders(ticker))
            if quantity <= aVol:
                print("quantity <= aVol", quantity, aVol)
                exit(code=0)
            print("client.create_buy_order(", ticker, ask, np.random.uniform(s1, s2), ")")
            print(client.create_buy_order(ticker, str(ask), str(np.random.uniform(s1, s2))[:4]))
            quantity -= aVol

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(cooldown)
    except :
        print("FUUUUUUUUUUCK", sys.exc_info())

