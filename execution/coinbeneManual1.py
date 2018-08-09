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

from coinbene import create_buy_order, create_sell_order, post_balance

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


def filter_balance(b):
    result = []
    for balance in b['balance']:
        if balance['available'] != '0':
            result.append(balance)
    return result


args = sys.argv

ticker, type, vol, price = args[1], args[2], float(args[3]), float(args[4])
#ticker, type, vol, price = "OMX-BTC", "SELL", .25, 0.00000100
# timeCnt = 0
# starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

balance = post_balance({ "account": "exchange" })
print("balances: ", filter_balance(balance))

# print("Kucoin Manual Version 1 -yungquant")
# timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
# orders = client.get_order_book(ticker, limit=99999)
# midpoint = np.mean([orders['BUY'][0][0], orders['SELL'][0][0]])

avgVol = vol
if type == "SELL":
    print("create_sell_order(", ticker, str(price), str(avgVol / price)[:7], ")")
    print(create_sell_order(ticker, str(price), str(avgVol / price)[:7]))
elif type == "BUY":
    print("create_buy_order(", ticker, str(price), str(avgVol / price)[:7], ")")
    print(create_buy_order(ticker, str(price), str(avgVol / price)[:7]))


