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
client = Client(
    api_key= '5b7dfd773232924f8607f128',
    api_secret= '5e399779-df87-4980-b392-36130d2be4ee')
# client = Client(
#     api_key= '5b648d9908d8b114d114636f',
#     api_secret= '7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0')



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

def filter_dealt_orders(data):
    result = data['datas']
    for datum in result:
        datum['ticker'] = datum['coinType'] + '-' + datum['coinTypePair']
        del datum['coinType']
        del datum['coinTypePair']
        del datum['orderOid']
        del datum['oid']
        del datum['createdAt']
        del datum['id']
        del datum['dealDirection']

    return result

args = sys.argv
ticker, posLim, account = args[1], float(args[2]), args[3]
if account == "personal":
    client = Client(
        api_key='5b7dfd773232924f8607f128',
        api_secret='5e399779-df87-4980-b392-36130d2be4ee')
elif account == "temp":
    client = Client(
        api_key='5b88e20991ed2916697b54b9',
        api_secret='d4e64666-39e9-4fea-85f5-e9d052dee0ec')
else:
    client = Client(
        api_key='5b648d9908d8b114d114636f',
        api_secret='7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0')
initBook = client.get_order_book(ticker, limit=99999)
timeCnt, execTrades = 0, 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
sBals = filterBalances(client.get_all_balances())

while (1):
    try:
        orders = client.get_order_book(ticker, limit=10)
        bid, ask = orders['BUY'][0][0], orders['SELL'][0][0]
        midpoint = np.mean([bid, ask])
        bals = filterBalances(client.get_all_balances())

        print("PosFeed Version 1 -yungquant")
        print("Ticker:", ticker)
        print("starttime:", starttime)
        print("sBals:", sBals, "bals:", bals)
        btcB, ethB, omxB = float(sBals[1]) - float(bals[1]), float(sBals[3]) - float(bals[3]), float(sBals[5]) - float(bals[5])
        print("BTC burn:", btcB, "ETH burn:", ethB, "OMX burn:", omxB)
        if timeCnt > 6:
            print("BTC burn per hour:", (btcB / timeCnt) * 360, "ETH burn per hour:", (ethB / timeCnt) * 360, "OMX burn per hour:", (omxB / timeCnt) * 360)
        print("price:", midpoint, "\n")
        dealt_orders = filter_dealt_orders(client.get_dealt_orders(ticker))
        buys, sells, bps, sps = [], [], [], []
        for i in range(len(dealt_orders)):
            if dealt_orders[i]['direction'] == "BUY":
                buys.append(dealt_orders[i])
            else:
                sells.append(dealt_orders[i])
        for k in range(len(buys)):
            bps.append(buys[k]['dealPrice'])
        for k in range(len(sells)):
            sps.append(sells[k]['dealPrice'])
        avgB, avgS = np.mean(bps), np.mean(sps)
        for o in dealt_orders: print("dealt:", o)
        active = client.get_active_orders(ticker)
        print("\nactive bids:", active['BUY'], "\nactive asks", active['SELL'], "\n")
        aBV, aAV = sum([order[3] for order in active['BUY']]) * midpoint, sum(
            [order[3] for order in active['SELL']]) * midpoint
        av = aBV + aAV
        print("avg buy price:", avgB, "avg sell price:", avgS)
        print("aBV:", aBV, "aAV:", aAV, "av:", av)
        if av > posLim:
            for i in range(10): print("!!!!!!!!!!!!!! AV > POSLIM !!!!!!!!!!!!!!!!!")
            print("client.cancel_all_orders(", ticker, ")")
            print(client.cancel_all_orders(ticker))
        time.sleep(10)
        timeCnt += 1
        print("timeCnt:", timeCnt, ",", timeCnt / 6, "minutes\n")
    except:
        print("FUUUUUUUUUUCK", sys.exc_info())
        time.sleep(1)

