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
# client = Client(
#     api_key= '5b648d9908d8b114d114636f',
#     api_secret= '7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0')

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

ticker, quantity, above, account = args[1], float(args[2]), float(args[3]), args[4]
if account == "personal":
    client = Client(
            api_key='5b7dfd773232924f8607f128',
            api_secret='5e399779-df87-4980-b392-36130d2be4ee')
elif account == "wc":
    api_key="5b648d9908d8b114d114636f"
    api_secret="7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0"
    client = Client(api_key, api_secret)
elif account == "temp":
    client = Client(
        api_key='5b88e20991ed2916697b54b9',
        api_secret='d4e64666-39e9-4fea-85f5-e9d052dee0ec')

#ticker, quantity, above = "ETH-BTC", 1, 0
sQuantity = quantity
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        print("Kucoin AutoAsk Version 1.1 -yungquant")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity, "above:", above)
        balances = filterBalances(client.get_all_balances())
        print("balances:", balances)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        orders = client.get_order_book(ticker, limit=99999)
        midpoint = np.mean([orders['BUY'][0][0], orders['SELL'][0][0]])
        print("starttime:", starttime, "time:", timeStr, "midpoint", midpoint)
        if midpoint > above:
            print("client.cancel_all_orders(ticker)")
            print(client.cancel_all_orders(ticker))

            avgVol = np.mean([float(order[-1]) for order in orders['SELL'][:10]])
            # if avgVol > balances[ticker[:3]]:
            #     avgVol = balances[ticker[:3]]
            print("client.create_sell_order(", ticker, str(float(orders['SELL'][0][0])), str(np.floor(avgVol / float(orders['SELL'][0][0]))), ")")
            print(client.create_sell_order(ticker, str(float(orders['SELL'][0][0])), str(np.floor(avgVol / float(orders['SELL'][0][0])))))

        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(10)
    except:
        print("FUUUUUUUUUUCK",  sys.exc_info())

