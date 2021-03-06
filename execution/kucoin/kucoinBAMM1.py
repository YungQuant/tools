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

ticker, quantity, window, cooldown, bb, account = args[1], float(args[2]), int(args[3]), int(args[4]), float(args[5]), args[6]

if account == "personal":
    client = Client(
        api_key='5b7dfd773232924f8607f128',
        api_secret='5e399779-df87-4980-b392-36130d2be4ee')
else:
    client = Client(
        api_key='5b648d9908d8b114d114636f',
        api_secret='7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0')

#ticker, quantity, aggression, window, ovAgg = "OMX-ETH", 1, 1, 60, 10
mtu = 0.00000001
if ticker[-3:] == "ETH":
    mtu = 0.0000001
elif ticker[-3:] == "BTC":
    mtu = 0.00000001

sQuantity = quantity
sBals = filterBalances(client.get_all_balances())
midpoints, spreads = [], []
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

while(1):
    try:
        print("Kucoin BAMM Version 1 -yungquant")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "Quantity:", quantity, "window:", window, "cooldown:", cooldown, "bb:", bb, "mtu:", mtu, "account:", account)
        timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        print("starttime:", starttime, "time:", timeStr)
        orders = client.get_order_book(ticker, limit=200)
        print("sBals:", sBals, "bals:", filterBalances(client.get_all_balances()))
        bid, ask = float(orders['BUY'][0][0]), float(orders['SELL'][0][0])
        midpoint = np.mean([bid, ask])
        bNatVol, aNatVol = float(orders['BUY'][0][1]), float(orders['SELL'][0][1])
        bVol, aVol = float(orders['BUY'][0][2]), float(orders['SELL'][0][2])
        spread = ask - bid
        spreads.append(spread)

        if timeCnt > window:
            spreadT = mtu * 2
            print("midpoint:", midpoint, "mean spread:", np.mean(spreads), "spread:", spread, "spreadT:", spreadT)
            print("bid:", bid, "ask:", ask, "bvol:", bVol, "aVol:", aVol)
            active = client.get_active_orders(ticker)
            aBV, aAV = sum([order[3] for order in active['BUY']]) * midpoint, sum([order[3] for order in active['SELL']]) * midpoint
            for i in range(len(active['BUY'])):
                print("active bid:", active['BUY'][i])
            for i in range(len(active['SELL'])):
                print("active ask:", active['SELL'][i])
            print("aBV", aBV, "aAV:", aAV)
            if spread > spreadT:
                print("$$$SPREAD>SPREADT$$$")

            if bb == -1:
                if spread > spreadT and aBV == 0 and aAV == 0:
                    print("client.create_buy_order(", ticker, bid + mtu, quantity / 2, ")")
                    print(client.create_buy_order(ticker, str(bid + mtu), str((quantity / 2) / bid)[:7]))

                    print("client.create_sell_order(", ticker, ask - mtu, quantity / 2, ")")
                    print(client.create_sell_order(ticker, str(ask-mtu), str((quantity / 2) / ask)[:7]))

                elif aBV + aAV < quantity:
                    if aBV < quantity / 2:
                        print("client.create_buy_order(", ticker, bid, (quantity / 2) - aAV, ")")
                        print(client.create_buy_order(ticker, str(bid), str(((quantity / 2) - aBV) / bid)[:7]))

                    if aAV < quantity / 2:
                        print("client.create_sell_order(", ticker, ask, (quantity / 2) - aAV, ")")
                        print(client.create_sell_order(ticker, str(ask), str(((quantity / 2) - aAV) / ask)[:7]))

                elif spread > spreadT and aBV == 0 or aAV == 0:
                    if aBV == 0:
                        print("client.create_buy_order(", ticker, bid + mtu, (quantity / 2) - aAV, ")")
                        print(client.create_buy_order(ticker, str(bid + mtu), str((quantity / 2) / bid)[:7]))

                    if aAV == 0:
                        print("client.create_sell_order(", ticker, ask - mtu, (quantity / 2) - aBV, ")")
                        print(client.create_sell_order(ticker, str(ask - mtu), str((quantity / 2) / ask)[:7]))

                else:
                    if spread < spreadT:
                        print("shes toooo tight homie! maybe try her asshole")

            if bb == 0:
                if spread > spreadT and aBV == 0 and aAV == 0:
                    print("DEBUG: spread > spreadT and aBV == 0 and aAV == 0")
                    print("client.create_buy_order(", ticker, bid + mtu, quantity / 2, ")")
                    print(client.create_buy_order(ticker, str(bid + mtu), str((quantity / 2) / bid)[:7]))

                    print("client.create_sell_order(", ticker, ask - mtu, quantity / 2, ")")
                    print(client.create_sell_order(ticker, str(ask-mtu), str((quantity / 2) / ask)[:7]))

                elif aBV > 0 and aAV > 0 and (aBV + aAV <= quantity) and aBV < quantity / 2 or aAV < quantity / 2:
                    print("DEBUG: aBV > 0 and aAV > 0 and aBV + aAV < quantity")
                    if aBV < quantity / 2:
                        print("client.create_sell_order(", ticker, ask, (quantity / 2) - aBV, ")")
                        print(client.create_sell_order(ticker, str(ask), str(((quantity / 2) - aBV) / ask)[:7]))

                    if aAV < quantity / 2:
                        print("client.create_buy_order(", ticker, bid, (quantity / 2) - aAV, ")")
                        print(client.create_buy_order(ticker, str(bid), str(((quantity / 2) - aAV) / bid)[:7]))

                # elif spread > spreadT and (aBV == 0 or aAV == 0):
                #     print("DEBUG: spread > spreadT and aBV == 0 or aAV == 0")
                #     if aBV == 0:
                #         print("client.create_sell_order(", ticker, ask - mtu, (quantity / 2) - aBV, ")")
                #         print(client.create_sell_order(ticker, str(ask - mtu), str(((quantity / 2) - aBV) / ask)[:7]))
                #
                #     if aAV == 0:
                #         print("client.create_buy_order(", ticker, bid + mtu, (quantity / 2) - aAV, ")")
                #         print(client.create_buy_order(ticker, str(bid + mtu), str(((quantity / 2) - aAV) / bid)[:7]))

                else:
                    if spread < spreadT:
                        print("shes toooo tight homie! maybe try her asshole")

            #ALL BB > 0 NEED ABOVE LOGIC ^^^^

            if bb >= 1:
                if spread > spreadT and aBV == 0 and aAV == 0:
                    print("client.create_buy_order(", ticker, bid + mtu, quantity * bb, ")")
                    #print(client.create_buy_order())

                    print("client.create_sell_order(", ticker, ask - mtu, quantity / 2, ")")
                    # print(client.create_sell_order())

                elif spread > spreadT and aBV < quantity / 2 or aAV < quantity / 2:
                    if aBV < quantity / 2:
                        print("client.create_sell_order(", ticker, ask - mtu, (quantity / 2) - aBV, ")")
                        # print(client.create_sell_order())

                    if aAV < quantity / 2:
                        print("client.create_buy_order(", ticker, bid + mtu, (quantity / 2) - aAV, ")")
                        #print(client.create_buy_order())

                else:
                    if spread < spreadT:
                        print("shes toooo tight homie! maybe try her asshole")

            if aAV + aAV > quantity:
                print(f"!!!!!!!!!!!!!!!!!!{aAV + aAV} > {quantity}!!!!!!!!!!!!!!!!!!!!!")
                if aAV + aAV > quantity * 1.25:
                    for i in range(5):
                        print(f"!!!!!!!!!!!!!!!!!!{aAV + aAV} > {quantity}*1.25!!!!!!!!!!!!!!!!!!!!!")
                    exit(code=0)
        timeCnt += 1
        print("timeCnt:", timeCnt, "\n")
        time.sleep(cooldown)
    except :
        time.sleep(cooldown)
        print("FUUUUUUUUUUCK", sys.exc_info(), "\n")

