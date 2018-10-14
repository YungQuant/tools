import ccxt
import requests
import pandas as pan
import sklearn as sk

exchange = ccxt.bitmex()
exchange.apiKey = 'XisZrCcq4qDmLhs2T53MpFMJ'
exchange.secret = 'ApEVapMkwqiEhV3FGr7NPjZHPG7P8xPAbtHxrbEs5RxA8NDz'


def load_bitmex_data(symbol, time_frequency, n_periods=500, baseURI='https://www.bitmex.com/api/v1'):
    '''
    request = requests.get('https://www.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol=xbt&count=500&reverse=true')

    '''
    endpoint = '/trade/bucketed/'
    if time_frequency == 'half_hour':
        bin_size = '5m'
    elif time_frequency == 'bi_hourly' or time_frequency == 'hourly':
        bin_size = '1h'
    elif time_frequency == 'daily':
        bin_size = '1d'

    request = requests.get(baseURI + endpoint, params={'symbol': symbol,
                                                       'binSize': bin_size,
                                                       'count': n_periods,
                                                       'reverse': False})

    raw_data, keys = request.json(), request.json()[0].keys()
    reformatted_data = pan.DataFrame()

    for i in range(0, len(request.json())):
        appended_data = pan.DataFrame([raw_data[i][key] for key in keys]).T
        reformatted_data = pan.concat([reformatted_data, appended_data])

    reformatted_data = reformatted_data.reset_index(drop='index')
    reformatted_data.columns = keys
    if time_frequency == 'half_hour':
        acceptable_units = ['30', '00']
        index = [i for i in range(0, len(reformatted_data)) if
                 reformatted_data['timestamp'][i][14:16] in acceptable_units]
        reformatted_data = reformatted_data.ix[index, :]

    elif time_frequency == 'bi_hourly':
        acceptable_units = ['02', '04', '06', '08', '10', '12', '14', '16', '18', '20']
        index = [i for i in range(0, len(reformatted_data)) if reformatted_data['date'][i][11:13] in acceptable_units]
        reformatted_data = reformatted_data.ix[index, :]

    return reformatted_data[::-1].reset_index(drop='index')

currency_pairs, currencies = ['LTCZ18'], ['ltc']

#print(exchange.create_order(currency_pairs[0], ))
# orders = exchange.fetch_ohlcv(symbol=currency_pairs[0], timeframe='1h')
# ps = [order[-2] for order in orders]
#print(load_bitmex_data("LTCU18", 'hourly').ix[0, :])
print(exchange.fetch_order_book(currency_pairs[0], limit=666)['bids'])