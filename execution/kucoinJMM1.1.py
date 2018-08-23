from kucoin.client import Client
# api_key="5b648d9908d8b114d114636f"
# api_secret="7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0"
# client = Client(api_key, api_secret)
client = Client(
        api_key='5b7dfd773232924f8607f128',
        api_secret='5e399779-df87-4980-b392-36130d2be4ee')
import pandas as pd
import sys
import random, time
import datetime
import numpy as np
from decimal import *
ff = lambda x: (format((x),'.7f'))
ask = lambda px,qty: client.create_sell_order('OMX-ETH',px,qty)
bid = lambda px,qty: client.create_buy_order('OMX-ETH',px,qty)
cancelsells = lambda: client.cancel_all_orders('OMX-ETH', 'SELL')
cancelbuys = lambda: client.cancel_all_orders('OMX-ETH', 'BUY')


def bal():
    omxbal = client.get_coin_balance('OMX')
    btcbal = client.get_coin_balance('BTC')
    ethbal = client.get_coin_balance('ETH')
    print("OMX",omxbal['balance'],omxbal['freezeBalance'])
    print("BTC",btcbal['balance'],btcbal['freezeBalance'])
    print("ETH",ethbal['balance'],ethbal['freezeBalance'])

def filterBalances(balances):
    retBals = {}
    for i in range(len(balances)):
        if balances[i]['balance'] != 0:
            retBals[balances[i]['coinType']] = balances[i]['balance']
    return retBals

ticker, initqty, skew, mult, s, ex = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])

if ticker[-3:] == "BTC":
    mtu = 0.00000001
    mtu2 = 0.00000002
elif ticker[-3:] == "ETH":
    mtu = 0.0000001
    mtu2 = 0.0000002


# skew = 0
# mult = 1

# initqty = 1000.4000
# mtu,mtu2 = float(0.0000001),float(0.0000002)
# osize = round(random.uniform(12000,1500),4)

sQuantity = initqty
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
sBals = filterBalances(client.get_all_balances())
orders = client.get_order_book(ticker, limit=10)
bidI, askI = float(orders['BUY'][0][0]), float(orders['SELL'][0][0])
sPrice = np.mean([bidI, askI])

running = 0
list = [[str(initqty/2),str(initqty/2)]]

while ex == 1:
    try:
        print("Kucoin JMM Version 1.1 -jakedigital & yungquant")
        print("Ticker:", ticker, "sQuantity:", sQuantity, "skew:", skew, "mult:", mult, "ex:", ex)
        print("sBals:", sBals, "bals:", filterBalances(client.get_all_balances()))
        print("starttime:", starttime, "time:", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"))

        depth = client.get_order_book('OMX-ETH', limit=50)
        sz,bz = [(format((i[0]),'.7f')) for i in depth['SELL']],[(format((i[0]),'.7f')) for i in depth['BUY']]
        top_bid,bot_ask = float(bz[0]),float(sz[0])
        ee = client.get_active_orders('OMX-ETH')
        buys,sells = ee['BUY'],ee['SELL']
        ss,bb = [(i[0],i[1],ff(i[2]),i[3]) for i in sells],[(i[0],i[1],ff(i[2]),i[3]) for i in buys]

        print( ((top_bid+mtu2) < bot_ask) and (running == 0) )
        if( ((top_bid+mtu2) < bot_ask) and (running == 0) ):
            bid(ff(top_bid+mtu),(initqty/2))
            ask(ff(bot_ask-mtu),(initqty/2))
            running = 1
            time.sleep(0.4)
        else:
            print("waiting for spread to open")

        print("RUNNING:", running)

        if running == 1:
            ee = client.get_active_orders('OMX-ETH')
            buys,sells = ee['BUY'],ee['SELL']
            a,b = [(i[3]) for i in sells],[(i[3]) for i in buys]
            openbid,openask = sum(a),sum(b)
            print("openbid:", openbid, "openask:", openask)
            print("open sells", a)
            print("open buys", b)
            bidsumqty,asksumqty = sum(b),sum(a)
            list.append([float(bidsumqty),float(asksumqty)])
            df = pd.DataFrame(list, columns=['bidqty','askqty'])
            bidq,askq = [(i) for i in (df['bidqty'])],[(i) for i in (df['askqty'])]
            lastbidq,lastaskq = bidq[-1],askq[-1]
            # print("SUM QTY BID/SUM",bidsumqty,asksumqty)
            print(df)

            bqc,aqc = (float(bidq[-2])-float(bidq[-1])),(float(askq[-2])-float(askq[-1]))
            print("BID QTY CHANGE",bqc)
            print("ASK QTY CHANGE",aqc)
            # print("bqc",bqc)
            # print("aqc",aqc)

            tpos = (bidsumqty+asksumqty)
            print("tpos",tpos)
            print("top bid",top_bid)
            print("top bid",bot_ask)

            if s == 0:
                if ((float(bidq[-1]) < float(bidq[-2])) and (tpos <= initqty)):
                    print("bid changed, post ask")
                    print("new", ask(ff(bot_ask), abs(bqc)))

                if ((float(askq[-1]) < float(askq[-2])) and (tpos <= initqty)):
                    print("ask changed, post bid")
                    print("new", bid(ff(top_bid), abs(aqc)))

            if s == 1:
                if ((float(bidq[-1]) < float(bidq[-2])) and (tpos <= initqty)):
                    print("bid changed, post ask")
                    t_ap = bot_ask - mtu + skew
                    if t_ap > top_bid:
                        print("new",ask(ff(t_ap),abs(bqc) * mult))
                    else:
                        print("new", ask(ff(top_bid + mtu), abs(bqc) * mult))

                if ((float(askq[-1]) < float(askq[-2])) and (tpos <= initqty)):
                    print("ask changed, post bid")
                    t_bp = top_bid + mtu + skew
                    if t_bp < bot_ask:
                        print("new",bid(ff(t_bp),abs(aqc) * mult))
                    else:
                        print("new", bid(ff(bot_ask - mtu), abs(aqc) * mult))

            print("\n")
            time.sleep(0.4)
    except:
            print("hold on !", sys.exc_info())
