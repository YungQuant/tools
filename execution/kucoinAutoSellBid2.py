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
ticker, quantity, askAggression, window, ref, ovAgg, pm = args[1], float(args[2]), float(args[3]), float(args[4]), float(args[5]), float(args[6]), float(args[7])
#ticker, quantity, bidAggression, askAggression, window, ref, ovAgg = "OMX-BTC", 5, 2, 2, 6, 1, 6
sQuantity = quantity
initBook = client.get_order_book(ticker, limit=99999)
bidImpacts, askImpacts, midpoints = [], [], []
timeCnt, execTrades = 0, 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
sPrice = np.mean([initBook['BUY'][0][0], initBook['SELL'][0][0]])

while (1):
    try:
        orders = client.get_order_book(ticker, limit=99999)
        recent_orders = client.get_recent_orders(ticker, limit=99999)
        bidImpact, askImpact = getImpact(orders['BUY'], orders['SELL'], size=ref)
        bid, ask = orders['BUY'][0][0], orders['SELL'][0][0]
        midpoints.append(np.mean([bid, ask]))
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        bals = filterBalances(client.get_all_balances())
        print("AutoSellBid Version 2 -yungquant")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity, "sPrice:", sPrice, "price:", midpoints[-1],
              "askAggression:", askAggression, "Window:", window, "ovAgg:", ovAgg, "pm:", pm)
        print("starttime:", starttime, "time:", timeStr)
        print("balances:", bals)
        print("price:", midpoints[-1], "ref:", ref, "bidImpact:", bidImpact, "askImpact:", askImpact)
        bidImpacts.append(bidImpact)
        askImpacts.append(askImpact)

        if timeCnt > window:
            # bidIM, askIM = np.mean(bidImpacts[-int(window):]), np.mean(askImpacts[-int(window):])
            # bidIS, askIS = np.std(bidImpacts[-int(window):]), np.std(askImpacts[-int(window):])
            bidIM, askIM = np.mean(bidImpacts), np.mean(askImpacts)
            bidIS, askIS = np.std(bidImpacts), np.std(askImpacts)
            if askImpact > 0:
                minp, mins = getMinimalImpact(orders['BUY'], orders['SELL'], ref)
            else:
                minp, mins = 0, 0
            print("AskIT:", askIM - (askIS * askAggression))
            print("Bid Impact Max, Min", max(bidImpacts), ",", min(bidImpacts), "Ask Impact Max, Min", max(askImpacts), ",", min(askImpacts))
            print("BidIV:", np.var(bidImpacts), "askIV:", np.var(askImpacts))
            print("bidIM:", bidIM, "bidIS:", bidIS, "askIM:", askIM, "askIS:", askIS)
            print("MINIMAL:", minp, mins)
            print("executed trades:", execTrades)

            if midpoints[-1] > pm:
                border, aorder, bResp, aResp = "None", "None", "None", "None"

                if askImpact <= askIM - (askIS * askAggression):
                    if mins > ref and mins < ref * 1.95:
                        print("MINIMAL client.create_sell_order(", ticker, minp,
                              str((mins * 1.03 / np.mean([bid, minp])))[:6], ")")
                        aResp = client.create_sell_order(ticker, minp,
                                                         str((mins * 1.03 / np.mean([bid, minp])))[:6])
                        print(aResp)
                        quantity -= mins * 1.03
                        execTrades += 1
                    else:
                        print("NON_MINIMAL client.create_sell_order(", ticker, bid - askImpact,
                              str((ref * 1.03 / np.mean([bid, bid - askImpact])))[:6], ")")
                        aResp = client.create_sell_order(ticker, bid - askImpact,
                                                         str((ref * 1.03 / np.mean([bid, bid - askImpact])))[
                                                         :6])
                        print(aResp)
                        quantity -= ref * 1.03
                        execTrades += 1


        if quantity < 0:
            exit(code=0)
        time.sleep(ovAgg)
        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
    except:
        print("FUUUUUUUUUUCK", sys.exc_info())
        time.sleep(1)

