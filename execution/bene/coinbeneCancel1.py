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


from coinbene import create_buy_order, cancel_all_orders
#ticker = args[1]
ticker = "OMXETH"
timeCnt = 0
starttime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")


print("Coinbene Cancel Version 1 -hugo")
print("Ticker:", ticker)
# balances = filterBalances(client.get_all_balances())
# print("balances:", balances)
# timeStr = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
# orders = client.get_order_book(ticker, limit=99999)
# midpoint = np.mean([orders['BUY'][0][0], orders['SELL'][0][0]])
# print("starttime:", starttime, "time:", timeStr, "midpoint", midpoint)
print("client.cancel_all_orders(", ticker, ")")
print(cancel_all_orders(ticker))


