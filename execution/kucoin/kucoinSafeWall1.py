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

ticker, quantity, window, pBuff, vBuff = args[1], float(args[2]), int(args[3]), float(args[4]), float(args[5])
if ticker[-3:] == "BTC":
    mtu = 0.00000001
    mtu2 = 0.00000002
    precision = 9
elif ticker[-3:] == "ETH":
    mtu = 0.0000001
    mtu2 = 0.0000002
    precision = 8
# if window < 10800:
#     print("Recommend window setting > 10800")
#     if window < 3600:
#         print("Recommend window setting > 10800, setting window to 3600")
#         window = 3600
#ticker, quantity, above = "ETH-BTC", 1, 0
sQuantity = quantity
midpoints = []
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while quantity > 0:
    try:
        print("Kucoin Safe Wall Version 1 -yungquant")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity, "vBuff:", vBuff, "pBuff:", pBuff)
        balances = filterBalances(client.get_all_balances())
        print("balances:", balances)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        orders = client.get_order_book(ticker, limit=99999)
        bid, ask = orders['BUY'][0][0],  orders['SELL'][0][0]
        midpoint = np.mean([bid, ask])
        midpoints.append(midpoint)
        print("starttime:", starttime, "time:", timeStr, "midpoint", midpoint)
        if timeCnt > window:
            pPerc = midpoint / 100
            vol = np.std(midpoints)
            mmp = np.mean(midpoints)
            ub, mb, lb = mmp + vol, mmp, mmp - vol
            up, mp, lp = midpoint + (pPerc * pBuff), midpoint, midpoint - (pPerc * pBuff)

            print("Volatility:", vol, "MMP:", mmp, "pPerc:", pPerc)
            print("ub/mb/lb:", ub, mb, lb, "up/mp/lp:", up, mp, lp)

            # FUTURE VERSION (1.1) BASED ON VOLUME OVER/UNDER IP

            ip = min([lb, lp])

            print("client.cancel_all_orders(ticker)")
            # print(client.cancel_all_orders(ticker))

            print("client.create_buy_order(", ticker, str(ip)[:precision], str(quantity), ")")
            # print(client.create_sell_order(ticker, str(ip)[:precision], str(quantity)))

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(1)
    except:
        print("FUUUUUUUUUUCK",  sys.exc_info())

