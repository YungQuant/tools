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

from coinbene import create_buy_order, create_sell_order, balances


args = sys.argv

ticker, type, vol, price = args[1], args[2], float(args[3]), float(args[4])
#ticker, type, vol, price = "OMX-BTC", "SELL", .25, 0.00000100
# timeCnt = 0
# starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

print("balances: ", balances())

# print("Kucoin Manual Version 1 -yungquant")
# timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
# orders = client.get_order_book(ticker, limit=99999)
# midpoint = np.mean([orders['BUY'][0][0], orders['SELL'][0][0]])

if type == "SELL":
    print("create_sell_order(", ticker, price, vol, ")")
    print(create_sell_order(ticker, price, vol))
elif type == "BUY":
    print("create_buy_order(", ticker, price, vol, ")")
    print(create_buy_order(ticker, price, vol))


