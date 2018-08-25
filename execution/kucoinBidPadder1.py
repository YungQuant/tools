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
    retBals = []
    for i in range(len(balances)):
        if balances[i]['balance'] != 0:
            retBals.append(balances[i]['coinType'])
            retBals.append(balances[i]['balance'])
    return retBals

args = sys.argv

ticker, depth, mtu, r1, r2 = args[1], int(args[2]), float(args[3]), int(args[4]), int(args[5])
#ticker, depth, mtu = "OMX-BTC", 50, 0.00000002


print("Kucoin Bid Padder Version 1 -yungquant")
print("Ticker:", ticker, "depth:", depth, "mtu:", mtu, "r1:", r1, "r2:", r2)
# timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
orders = client.get_order_book(ticker, limit=99999)
bid, ask = orders['BUY'][0][0], orders['SELL'][0][0]
print("balances:", filterBalances(client.get_all_balances()))
print("bid:", bid, "ask:", ask)
#print("time:", timeStr)
bi, ai = 0, 0

while(1):
    try:
        ps = [ask] + [order[0] for order in orders['BUY']] #if order[3] > 100]
        for i in range(1, depth):
            ords = str(np.random.uniform(r1, r2))[:5]
            ordp = ps[0] - (i * mtu)
            if ordp not in ps:
                print("client.create_buy_order(", ticker, str(ordp),
                      ords, ")")
                print(client.create_buy_order(ticker, str(round(ordp, 8)),
                                              ords))
                # time.sleep(1)
            if ordp >= ps[0]:
              exit(code=0)
        exit(code=0)

    except kucoin.exceptions.KucoinAPIException as e:
        print("FUUUUUUUCK", e)


