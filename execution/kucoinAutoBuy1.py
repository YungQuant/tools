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
client = Client(
    api_key= '5b579193857b873dcbd2eceb',
    api_secret= '0ca53c55-39d2-45aa-8a75-cbeb7c735d26')

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

#ticker, quantity = args[1], float(args[2])
ticker, quantity = "OMX-ETH", 1
sQuantity = quantity
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        print("Kucoin AutoBuy Version 1 -yungquant")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        print("balances:", filterBalances(client.get_all_balances()))
        print("starttime:", starttime, "time:", timeStr)
        midpoints = []
        orders = client.get_order_book(ticker, limit=99999)
        print("client.cancel_all_orders(ticker)")
        print(client.cancel_all_orders(ticker))

        avgVol = np.mean([float(order[-1]) for order in orders['BUY'][:10]])
        print("client.create_buy_order(", ticker, str(float(orders['BUY'][0][0]) * 1.00001), str(np.floor(avgVol / float(orders['BUY'][0][0]))), ")")
        print(client.create_buy_order(ticker, str(float(orders['BUY'][0][0]) * 1.00001), (np.floor(avgVol / float(orders['BUY'][0][0])))))

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(30)
    except kucoin.exceptions.KucoinAPIException as e:
        print("FUUUUUUUUUUCK",  e)

