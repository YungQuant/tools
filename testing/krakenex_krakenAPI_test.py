import krakenex

import pprint

k = krakenex.API("Xj/xDlIJp3W51mdffa5LkEzExjODDJGPNFTPwVulmAFAjOUBVu52zYn6", "OmuePNOYgdWBT1HNlPyymNUV/K+v4B4iHod21rxxMc4UeyYl1fB9dOUT2IETd0sar322VKxiSgC37qgc4UbpEQ==")

##########################

# response = k.query_public('Depth', {'pair': 'XXBTZUSD', 'count': '10'})
# #pprint.pprint(response)
# print(response)

##########################

# k.load_key('kraken.key')
#
# k.query_private('AddOrder',
#                 {'pair': 'XXBTZEUR',
#                  'type': 'buy',
#                  'ordertype': 'limit',
#                  'price': '1',
#                  'volume': '1',
#                  # only `ordertype`, `price` and `price2` are valid
#                  'close[ordertype]': 'limit',
#                  'close[price]': '9001',
#                  # these will be ignored!
#                  'close[pair]': 'XXBTZEUR',
#                  'close[type]': 'sell',
#                  'close[volume]': '1'})

#########################

# k.load_key('kraken-monitor.key')
#
# balance = k.query_private('Balance')
# orders = k.query_private('OpenOrders')
#
# balance = balance['result']
# orders = orders['result']
#
# newbalance = dict()
# for currency in balance:
#     # remove first symbol ('Z' or 'X'), but not for GNO
#     newname = currency[1:] if len(currency) == 4 else currency
#     newbalance[newname] = D(balance[currency]) # type(balance[currency]) == str
# balance = newbalance
#
# for _, o in orders['open'].items():
#     # remaining volume in base currency
#     volume = D(o['vol']) - D(o['vol_exec'])
#
#     # extract for less typing
#     descr = o['descr']
#
#     # order price
#     price = D(descr['price'])
#
#     pair = descr['pair']
#     base = pair[:3]
#     quote = pair[3:]
#
#     type_ = descr['type']
#     if type_ == 'buy':
#         # buying for quote - reduce quote balance
#         balance[quote] -= volume * price
#     elif type_ == 'sell':
#         # selling base - reduce base balance
#         balance[base] -= volume
#
# for k, v in balance.items():
#     # convert to string for printing
#     if v == D('0'):
#         s = '0'
#     else:
#         s = str(v)
#     # remove trailing zeros (remnant of being decimal)
#     s = s.rstrip('0').rstrip('.') if '.' in s else s
#     #
#     print(k, s)

#############################

# k.load_key('kraken.key')
#
# print(k.query_private('Balance'))

#############################

# # Saves trade history to CSV file.
# #
# # WARNING: submits a lot of queries in rapid succession!
#
# # Maintainer: Austin.Deric@gmail.com (@AustinDeric on github)
#
# import pandas as pd
# import krakenex
#
# import datetime
# import calendar
# import time
#
# # takes date and returns nix time
# def date_nix(str_date):
#     return calendar.timegm(str_date.timetuple())
#
# # takes nix time and returns date
# def date_str(nix_time):
#     return datetime.datetime.fromtimestamp(nix_time).strftime('%m, %d, %Y')
#
# # return formatted TradesHistory request data
# def data(start, end, ofs):
#     req_data = {'type': 'all',
#                 'trades': 'true',
#                 'start': str(date_nix(start)),
#                 'end': str(date_nix(end)),
#                 'ofs': str(ofs)
#                 }
#     return req_data
#
# k = krakenex.API()
# k.load_key('kraken.key')
#
# data = []
# count = 0
# for i in range(1,11):
#     start_date = datetime.datetime(2016, i+1, 1)
#     end_date = datetime.datetime(2016, i+2, 29)
#     th = k.query_private('TradesHistory', data(start_date, end_date, 1))
#     time.sleep(.25)
#     print(th)
#     th_error = th['error']
#     if int(th['result']['count'])>0:
#         count += th['result']['count']
#         data.append(pd.DataFrame.from_dict(th['result']['trades']).transpose())
#
# trades = pd.DataFrame
# trades = pd.concat(data, axis = 0)
# trades = trades.sort(columns='time', ascending=True)
# trades.to_csv('data.csv')

###########################

