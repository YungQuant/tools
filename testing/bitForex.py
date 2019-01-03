from twilio.rest import Client
# Your Account Sid and Auth Token from twilio.com/user/account
# account_sid = "ACb54732f8bd8ffd4caaf48cbfff37347b"
# auth_token = "889e5c18913cffddd0121491171130dd"
account_sid = "ACa7f1da527d86f3a9c911cd2cfd0d69f5"
auth_token = "c8385705cb649f118734bf05f4b4b156"
client = Client(account_sid, auth_token)
import numpy as np
import sys
import time
sys.path.insert(0, "../../../pyexchange")
import exchange
from exchange import CurrencyPair
from exchange import ExchangeAPI

def alert_duncan(message):
    m = client.messages.create(
        to= "+12026316400",
        body=message,
        from_="+13014175078")

    print(m.body)

def alert_bryan(message):
    m = client.messages.create(
        to= "+15167120987",
        body=message,
        from_="+17345777574")

    print(m.body)

path = "market_currency: ETH, currency: ZPR"
test, test1 = [0], [0, 1, 2]
alerts = 0

while 1:
    if alerts < 5:
        try:
            pairs, tickers, vals = [], [], []
            bitforex = ExchangeAPI().create_exchange('Bitforex')
            for pair in bitforex.get_currency_pairs():
                pairs.append(pair)
            tickers.append(str(bitforex.get_ticker(CurrencyPair('BTC', 'PATH'))))
            tickers.append(str(bitforex.get_ticker(CurrencyPair('ETH', 'PATH'))))
            # ticker3 = bitforex.get_ticker(CurrencyPair('USDT', 'PATH'))
            # ticker = bitforex.get_ticker(CurrencyPair('USDT', 'BTC'))
            book0 = bitforex.get_orderbook(CurrencyPair('BTC', 'PATH'))
            book1 = bitforex.get_orderbook(CurrencyPair('ETH', 'PATH'))

            # for i in range(len(pairs)):
            #     print(pairs[i])

            for i in range(len(tickers)):
                print(tickers[i])
                vals.append(float(tickers[i][60:64]))

            print(sum(vals))
            print(book0)
            print(book1)

            # if sum(vals) > 0:
            #     alert_bryan(str(tickers[0]) + str(tickers[1]))
            #     alerts += 1

            time.sleep(60)
        except:
            print("failed..")
            time.sleep(10)
    else:
        exit(0)