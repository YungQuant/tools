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

# has to be run from the execution folder to pick up models
import sys
sys.path.append("..")
from kucoin.client import Client
kucoin_api_key = 'api_key'
kucoin_api_secret = 'api_secret'
# client = Client(
#     api_key= '5b579193857b873dcbd2eceb',
#     api_secret= '0ca53c55-39d2-45aa-8a75-cbeb7c735d26')
client = Client(
    api_key= '5b648d9908d8b114d114636f',
    api_secret= '7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0')



def getMaximalImpact(buys, sells, size):
    bidImpact, askImpact = getImpact(buys, sells, size)

    ogCC = size / bidImpact

    impact, cc, s, i = 0, 0, 0, 0
    initPrice = sells[0][0]
    while cc < ogCC:
        impact = sells[i][0] - initPrice
        s += sells[i][-1]
        if impact > bidImpact:
            cc = s / impact
        i += 1

    return sells[i][0], s

def getMinimalImpact(buys, sells, size):
    bidImpact, askImpact = getImpact(buys, sells, size)

    ogCC = size / askImpact

    impact, cc, s, i = 0, 0, 0, 0
    initPrice = buys[0][0]
    while cc > ogCC:
        impact = buys[i][0] - initPrice
        s += buys[i][-1]
        if impact > askImpact:
            cc = s / impact
        i += 1

    return buys[i][0], s


def getImpact(buys, sells, size=1.0):
    bidVol = 0
    bidInitPrice = buys[0][0]
    for k in range(len(buys)):
        bidVol += buys[k][-1]
        # print(f'bidVol: {bidVol}')
        if bidVol >= size:
            # print("bidVol >= size")
            askImpacts = bidInitPrice - buys[k][0]
            break
        elif k == len(buys) - 1:
            askImpacts = bidInitPrice
            break

    askVol = 0
    askInitPrice = sells[0][0]
    for k in range(len(sells)):
        askVol += sells[k][-1]
        # print(f'askvol:{askVol}')
        if askVol >= size:
            # print("askVol >= size")
            bidImpacts = sells[k][0] - askInitPrice
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
ticker, d, a = args[1], int(args[2]), int(args[3])
initBook = client.get_order_book(ticker, limit=99999)
timeCnt, execTrades = 0, 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while (1):
    try:
        orders = client.get_order_book(ticker, limit=10)
        bid, ask = orders['BUY'][0][0], orders['SELL'][0][0]
        midpoint = np.mean([bid, ask])
        bals = filterBalances(client.get_all_balances())

        print("PosFeed Version 1 -yungquant")
        print("Ticker:", ticker)
        print("starttime:", starttime)
        print("balances:", bals)
        print("price:", midpoint, "\n")
        if d == 1:
            dealt_orders = client.get_dealt_orders(ticker)
            print("dealt:", dealt_orders, "\n")
        if a == 1:
            active_orders = client.get_active_orders(ticker)
            print("active bids:", active_orders['BUY'], "\nactive asks", active_orders['SELL'], "\n")

        time.sleep(1)
        timeCnt += 1
        print("timeCnt:", timeCnt, ",", timeCnt / 60, "minutes\n")
    except:
        print("FUUUUUUUUUUCK", sys.exc_info())
        time.sleep(1)

