import ccxt, numpy as np

exchange = ccxt.bitmex()
exchange.apiKey = 'XisZrCcq4qDmLhs2T53MpFMJ'
exchange.secret = 'ApEVapMkwqiEhV3FGr7NPjZHPG7P8xPAbtHxrbEs5RxA8NDz'


currency_pairs, currencies = ['LTCZ18'], ['ltc']
book = exchange.fetch_order_book(currency_pairs[0], limit=666)

def get_stealth_pos_size(currency_pair, desSize, position=1):
    ''' position 1 or -1, long or short
        desSize: desired size (total size of execution)'''
    book = exchange.fetch_order_book(currency_pairs, limit=666)
    bids, asks = book['bids'], book['asks']
    bidV, askV = 0, 0

    for i in range(10):
        bidV += bids[i][1]
        askV += asks[i][1]

    sBid, sAsk = bidV / 10, askV / 10
    if position == 1:
        if sBid < desSize:
            return sBid
        else:
            return desSize
    else:
        if sAsk < desSize:
            return sAsk
        else:
            return desSize
