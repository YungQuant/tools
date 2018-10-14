import ccxt
import requests
import numpy as np
import time
import pandas as pan, matplotlib.pyplot as plt
import sklearn as sk

exchange = ccxt.bitmex()
'''TESTNET'''
# exchange.apiKey = 'XisZrCcq4qDmLhs2T53MpFMJ'
# exchange.secret = 'ApEVapMkwqiEhV3FGr7NPjZHPG7P8xPAbtHxrbEs5RxA8NDz'
'''PERSONAL'''
exchange.apiKey = '9pMckp2ljCdRtJa6WLo3UFh6'
exchange.secret = '4XIIaC7zHyMafFXU6j2uK-ur-hQds5r-xDbWvO4qErtAU5iw'


def load_bitmex_data(symbol, time_frequency, n_periods=666, baseURI='https://www.bitmex.com/api/v1'):
    '''
    request = requests.get('https://www.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol=xbt&count=500&reverse=true')

    '''
    endpoint = '/trade/bucketed/'
    if time_frequency == 'half_hour':
        bin_size = '5m'
    elif time_frequency == '1m':
        bin_size = '1m'
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


def plot(a):
    y = np.arange(len(a))
    plt.plot(y, a, 'g')
    plt.ylabel('Y')
    plt.xlabel('X')
    plt.title("Title")
    plt.show()

def var(arr, conf=0.99):
    return arr[int(np.floor(len(arr) * (1-conf)))]

def isRiskManaged(currency_pair, EET=120):
    ''' Estimated Execution Time '''
    trades = exchange.fetch_trades(currency_pair)
    trades = [obj['info'] for obj in trades]
    positions, position = [], 0

    for i in range(len(trades)):
        if trades[i]['side'] == "Sell":
            position -= trades[i]['size'] * trades[i]['price']
        elif trades[i]['side'] == "Buy":
            position += trades[i]['size'] * trades[i]['price']
        positions.append(abs(position))
        #print(trades[i], "\n", position)

    posMean, posMin, posMax = np.mean(positions), min(positions), max(positions)
    posInit, posEnd = positions[0], positions[-1]

    if posEnd < posMax * 0.8:
        time.sleep(EET)

        trades = exchange.fetch_trades(currency_pair)
        trades = [obj['info'] for obj in trades]
        buys, sells, positions, position = [], [], [], 0

        for i in range(len(trades)):
            if trades[i]['side'] == "Sell":
                position -= trades[i]['size'] * trades[i]['price']
            elif trades[i]['side'] == "Buy":
                position += trades[i]['size'] * trades[i]['price']
            positions.append(abs(position))
            #print(trades[i], "\n", position)

        posMean, posMin, posMax = np.mean(positions), min(positions), max(positions)
        posInit, posEnd = positions[0], positions[-1]

        if posEnd < posMax * 0.8:
            return False
        else:
            return True
    else:
        return True

def isRiskManagedTwo(currency_pair, rt=0.8, conf=0.99):
    ''' rt = risk tolerance, 1 - max tolerated loss % (ie; rt=0.8 == 20% max tolerated loss '''
    trades = exchange.fetch_trades(currency_pair)
    ps = load_bitmex_data(currency_pair, "daily", n_periods=666)
    ps = [float(p) for p in ps.ix[:, 'close']]
    trades = [obj['info'] for obj in trades]
    positions, f_pos, buys, sells, accv, accva, rets, idxRets = [], trades[0]['side'], [], [], 1, [], [], []

    for i in range(len(trades)):
        if trades[i]['side'] == "Buy":
            buys.append(trades[i]['price'])
            if len(sells) > 0:
                positions.append(np.mean(sells))
                sells = []
        elif trades[i]['side'] == 'Sell':
            sells.append(trades[i]['price'])
            if len(buys) > 0:
                positions.append(np.mean(buys))
                buys = []

    if f_pos == "Buy":
        for i in range(len(positions)-1):
            if i % 2 == 0:
                rets.append((positions[i+1] - positions[i]) / positions[i])
                accv *= 1 + rets[-1]
            else:
                rets.append((positions[i] - positions[i + 1]) / positions[i])
                accv *= 1 + rets[-1]
            accva.append(accv)

    else:
        for i in range(len(positions)-1):
            if i % 2 == 0:
                rets.append((positions[i] - positions[i + 1]) / positions[i])
                accv *= 1 + rets[-1]
            else:
                rets.append((positions[i + 1] - positions[i]) / positions[i])
                accv *= 1 + rets[-1]
            accva.append(accv)

    for i in range(1, len(ps)):
        idxRets.append((ps[i] - ps[i-1]) / ps[i-1])

    algoVar = var(sorted(rets), conf=conf)
    idxVar = var(sorted(idxRets), conf=conf)
    print(f'Risk Assessed @ {conf}% Confidence: Algorithm VAR = {algoVar}% Asset VAR = {idxVar}%')
    if algoVar < idxVar:
        print("WARNING: Algorithm Performance Destabilized")
    return accv > (max(accva) * rt)




print(isRiskManagedTwo('ETHZ18'))