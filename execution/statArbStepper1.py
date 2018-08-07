import os
import sys
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

def filterBalances(balances):
    retBals = []
    for i in range(len(balances)):
        if balances[i]['balance'] != 0:
            retBals.append(balances[i]['coinType'])
            retBals.append(balances[i]['balance'])
    return retBals

from kucoin.client import Client
kucoin_api_key = 'api_key'
kucoin_api_secret = 'api_secret'
client = Client(
    api_key= '5b579193857b873dcbd2eceb',
    api_secret= '0ca53c55-39d2-45aa-8a75-cbeb7c735d26')

args = sys.argv
# squantity = float(args[1])
squantity = 1
bOrderP, aOrderP = False, False
quantity = squantity
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")


while quantity > squantity * 0.1:
    ctime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
    #balances = client.get_all_balances()
    balances = filterBalances(client.get_all_balances())
    print("KuCoin Statistical Arbitrage Stepper 1.0 -yungquant \n starttime:", starttime, "time:", ctime)
    print("Quantity:", quantity, "sQuantity:", squantity, "Balances:", balances)
    btcOrders = client.get_order_book("OMX-BTC", limit=999999)
    ethOrders = client.get_order_book("OMX-ETH", limit=999999)
    #{'SELL': [[1532481319000, 'SELL', 1.28e-06, 7440.8878, 9772.1122, '5b57cf26d594660aa9470b4e', 1.28e-06]], 'BUY': []}
    #{'SELL': [[1532481777000, 'SELL', 2.27e-05, 73709.0, 0.0, '5b57d0f1555e12444df82503', 0.0]], 'BUY': []}
    #{'SELL': [], 'BUY': []}
    ethPrice = client.get_tick("ETH-BTC")['lastDealPrice']
    btcBid, btcAsk, ethBid, ethAsk = btcOrders['BUY'][0][0], btcOrders['SELL'][0][0], ethOrders['BUY'][0][0], ethOrders['SELL'][0][0]

    btcMarketPrice = np.mean([btcOrders['BUY'][0][0], btcOrders['SELL'][0][0]])
    ethMarketPrice = np.mean([ethOrders['BUY'][0][0], ethOrders['SELL'][0][0]]) * ethPrice
    if btcMarketPrice > ethMarketPrice:
        highMarket = "OMX-BTC"
        lowMarket = "OMX-ETH"
        highOrders = btcOrders
        lowOrders = ethOrders
        highBid, highAsk, lowBid, lowAsk = btcBid, btcAsk, ethBid, ethAsk
    else:
        highMarket = "OMX-ETH"
        lowMarket = "OMX-BTC"
        highOrders = ethOrders
        lowOrders = btcOrders
        highBid, highAsk, lowBid, lowAsk = ethBid, ethAsk, btcBid, btcAsk

    highResp = client.get_active_orders(highMarket)
    lowResp = client.get_active_orders(lowMarket)
    histOrds = client.get_dealt_orders(lowMarket)
    #print("histOrds:", histOrds)

    if highResp['SELL'] == [] and not aOrderP:
        avgHighVol = 2#np.mean([float(order[-1]) for order in highOrders['SELL'][:10]])
        print("client.create_sell_order(", highMarket, highAsk, str(avgHighVol)[:4], ")")
        print(client.create_sell_order(highMarket, highAsk, str(avgHighVol)[:4]))
        aOrderP = True
        if lowResp['BUY'] == [] and not bOrderP:
            avgLowVol = 1000#np.mean([float(order[-1]) for order in lowOrders['BUY'][:10]])
            print("client.create_buy_order(", lowMarket, lowBid, str(avgLowVol)[:4], ")")
            print(client.create_buy_order(lowMarket, lowBid, str(avgLowVol)[:4]))
            bOrderP = True

    else:
        if highResp['SELL'] != [] and highResp['SELL'][-3] > 0:
            print("client.create_buy_order(", lowMarket, lowAsk, highResp['SELL'][-3], ")")
            print(client.create_buy_order(lowMarket, lowAsk, str(highResp['SELL'][-3])[:4]))
            aOrderP = True
        elif highResp['SELL'] == [] and aOrderP:
            avgHighVol = 1000#np.mean([float(order[-1]) for order in highOrders['SELL'][:10]])
            print("client.create_buy_order(", lowMarket, lowAsk, avgHighVol, ")")
            print(client.create_buy_order(lowMarket, lowAsk, str(avgHighVol)[:4]))
            aOrderP = False
        # elif lowResp['BUY'] == [] and bOrderP == False:
        #     avgLowVol = np.mean([float(order[-1]) for order in lowOrders['BUY'][:10])
        #     print("client.create_buy_order(", lowMarket, lowBid, str(avgLowVol)[:4], ")")
        #     print(client.create_buy_order(lowMarket, lowBid, str(avgLowVol)[:4]))
        #     bOrderP = True

    print("Active High Market Orders:", client.get_active_orders(highMarket), "Active Low Market Orders:", client.get_active_orders(lowMarket))

    time.sleep(10)
