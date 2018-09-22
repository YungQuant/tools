Jake, [22.08.18 16:09]
from kucoin.client import Client
api_key="5b648d9908d8b114d114636f"
api_secret="7a0c3a0e-1fc8-4f24-9611-e227bde6e6e0"
client = Client(api_key, api_secret)
import pandas as pd
import random, time
import numpy as np
from decimal import *
ff = lambda x: (format((x),'.7f'))
ask = lambda px,qty: client.create_sell_order('OMX-ETH',px,qty)
bid = lambda px,qty: client.create_buy_order('OMX-ETH',px,qty)
cancelsells = lambda: client.cancel_all_orders('OMX-ETH', 'SELL')
cancelbuys = lambda: client.cancel_all_orders('OMX-ETH', 'BUY')
mtu,mtu2 = float(0.0000001),float(0.0000002)
osize = round(random.uniform(12000,1500),4)
def bal():
    omxbal = client.get_coin_balance('OMX')
    btcbal = client.get_coin_balance('BTC')
    ethbal = client.get_coin_balance('ETH')
    print("OMX",omxbal['balance'],omxbal['freezeBalance'])
    print("BTC",btcbal['balance'],btcbal['freezeBalance'])
    print("ETH",ethbal['balance'],ethbal['freezeBalance'])

# skew = 0
# mult = 1
ex = 0
initqty = 1000.4000
running = 0
list = [[str(initqty/2),str(initqty/2)]]

while ex == 1:
    try:
        tt = time.time()
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

        print("RUNNING",running)

        if running == 1:
            ee = client.get_active_orders('OMX-ETH')
            buys,sells = ee['BUY'],ee['SELL']
            a,b = [(i[3]) for i in sells],[(i[3]) for i in buys]
            openbid,openask = sum(a),sum(b)
            print(openbid,openask)
            print(tt)
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
            print("bqc",bqc)
            print("aqc",aqc)

            tpos = (bidsumqty+asksumqty)
            print("tpos",tpos)
            print("top bid",top_bid)
            print("top bid",bot_ask)
            bal()

            if ((float(bidq[-1]) < float(bidq[-2])) and (tpos <= initqty)):
                print("bid changed, post ask")
                print("new",ask(ff(bot_ask),abs(bqc)))

            if ((float(askq[-1]) < float(askq[-2])) and (tpos <= initqty)):
                print("ask changed, post bid")
                print("new",bid(ff(top_bid),abs(aqc)))

            print("")
            time.sleep(0.4)
    except:
            print("hold on !")
