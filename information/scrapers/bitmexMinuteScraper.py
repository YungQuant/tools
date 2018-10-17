import requests
import os
import time

# note to self: ccxt gets proper responses n such
# but throws error: ccxt.base.errors.ExchangeError: bitmex No market symbol
# bs n lies

# get all the active markets
instruments = requests.get("https://www.bitmex.com/api/v1/instrument/active").json()
symbols = [i["symbol"] for i in instruments]


url = "https://www.bitmex.com/api/v1/orderBook/L2"


def write_that_shit(filename, orderbook):
    print("Writing: " + orderbook[0]['symbol'])
    if os.path.isfile(filename):
        th = 'a'
    else:
        th = 'w'
    file = open(filename, th)
    file.write("Symbol: " + orderbook[0]['symbol'] + "\n")
    file.write(orderbook[0]['side'] + ": " + '%f' % orderbook[0]['price'] + "\n")
    file.write(orderbook[1]['side'] + ": " + '%f' % orderbook[1]['price'] + "\n")
    file.write("Timestamp: " + str(time.time()) + "\n")
    file.write("\n")
    file.close()


while True:
    print("scraping minute data for: ", symbols)
    for s in symbols:
        json = requests.get(url, params={"symbol": s, "depth": 1}).json()
        write_that_shit("output/bitmex_" + s + "_1min.txt", json)
    time.sleep(60)
