import ccxt, os
import sklearn as sk
import requests, pandas as pan
from sklearn.preprocessing import MinMaxScaler
from sklearn import svm, linear_model
from sklearn.metrics import mean_squared_error
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM, Dropout
import numpy as np

exchange = ccxt.bitmex()
exchange.apiKey = 'XisZrCcq4qDmLhs2T53MpFMJ'
exchange.secret = 'ApEVapMkwqiEhV3FGr7NPjZHPG7P8xPAbtHxrbEs5RxA8NDz'

def get_CDD_data(currency, interval='1h'):
    filename = f'../../prop/cDDdata/{currency}_{interval}.csv'
    data = []
    if os.path.isfile(filename) == False:
        print(f'could not source ../../prop/cDDdata/{currency}_{interval}.csv data')
    else:
        fileP = open(filename, "r")
        lines = fileP.readlines()
        for i, line in enumerate(lines):
            linex = line.split(",")[2:6]
            data.append(linex)
    return reversed(data[2:])

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

def isFloat(n):
    try:
        n = float(n)
        return True
    except:
        return False


def create_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)):
        if i > look_back:
            dataX.append(dataset[i-look_back:i])
            dataY.append(dataset[i])
    return np.array(dataX), np.array(dataY)

def create_binary_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        if i > look_back:
            #dataX.append(dataset[i-look_back:i])

            datum = []
            nS = dataset[i-look_back:i]
            for k in range(len(nS)):
                for j in range(len(nS[k])):
                    datum.append(nS[k][j])
            dataX.append(datum)

            if dataset[i+1][-1] > dataset[i][-1]:
                dataY.append(1)
            else:
                dataY.append(0)
    return np.array(dataX), np.array(dataY)

def create_bounded_binary_dataset(dataset, look_back, b=0.01):
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        if i > look_back:
            dataX.append(dataset[i-look_back:i])
            if dataset[i] > dataset[i-1] * (1 + b):
                dataY.append(1)
            elif dataset[i] < dataset[i-1] * (1 - b):
                dataY.append(-1)
            else:
                dataY.append(0)
    return np.array(dataX), np.array(dataY)

def create_binary_ohlcv_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        datum = []
        if i > look_back:
            for k in range(len(dataset[i-look_back:i])):
                for j in range(len(dataset[i-look_back:i][k])):
                    datum.append(dataset[i-look_back:i][k][j])
            dataX.append(datum)
            if dataset[i+1][-1] > dataset[i][-1]:
                dataY.append(1)
            else:
                dataY.append(0)
    return np.array(dataX), np.array(dataY)

def create_change_ohlcv_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        datum = []
        if i > look_back:
            for k in range(len(dataset[i-look_back:i])):
                for j in range(len(dataset[i-look_back:i][k])):
                    datum.append(dataset[i-look_back:i][k][j])
            dataX.append(datum)
            dataY.append((dataset[i+1][-1] - dataset[i][-1]) / dataset[i][-1])
    return np.array(dataX), np.array(dataY)

def create_range_ohlcv_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        datum = []
        if i > look_back:
            for k in range(len(dataset[i-look_back:i])):
                for j in range(len(dataset[i-look_back:i][k])):
                    datum.append(dataset[i-look_back:i][k][j])
            dataX.append(datum)
            dataY.append(dataset[i+1][1:3])
    return np.array(dataX), np.array(dataY)

def create_ohlcv_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        datum = []
        if i > look_back:
            for k in range(len(dataset[i-look_back:i])):
                for j in range(len(dataset[i-look_back:i][k])):
                    datum.append(dataset[i-look_back:i][k][j])
            dataX.append(datum)

            dataY.append(dataset[i+1][-1])
    return np.array(dataX), np.array(dataY)

def disectPanda(panda):
    bodyParts = []
    for i in range(len(panda.ix[:, 'close'])):
        bodyParts.append([panda.ix[i, 'open'], panda.ix[i, 'high'], panda.ix[i, 'low'], panda.ix[i, 'close']])
    return bodyParts

currency_pairs, currencies = ["XBTUSD", "ETHUSD", "XRPU18", "TRXU18", "LTCU18", "EOSU18", "ADAU18", "BCHU18", "XRPU18"], ['ltc', 'xbt']
errs, passes, fails = [], 0, 0

#print(exchange.create_order(currency_pairs[0], ))
#orders = exchange.fetch_ohlcv(symbol=currency_pairs[0], timeframe='1m')
orders1 = load_bitmex_data(currency_pairs[0], "hourly", n_periods=666)
orders = get_CDD_data("BTCUSD")
#print(orders)
#ps = [order[-2] for order in orders if isFloat(order[-2])]
ps = [[float(order[0]), float(order[1]), float(order[2]), float(order[3])] for order in orders]
ps1 = disectPanda(orders1)
print("order0:\n", ps[0])
print("len(ps):", len(ps))
print("order1[0]:\n", ps1[0])
print("len(ps1):", len(ps1))
Din = 3
X, Y = create_range_ohlcv_dataset(ps, Din)
X1, Y1 = create_range_ohlcv_dataset(ps1, Din)
trainX, trainY, testX, testY = X[:int(np.floor(len(X)/1.1))], Y[:int(np.floor(len(X)/1.1))], X[int(np.floor(len(X)/1.1)):], Y[int(np.floor(len(X)/1.1)):]
trainX1, trainY1, testX1, testY1 = X1[:int(np.floor(len(X1)/9.9))], Y1[:int(np.floor(len(X1)/9.9))], X1[int(np.floor(len(X1)/9.9)):], Y1[int(np.floor(len(X1)/9.9)):]
print(testX[0], testY[0], "\n", testX1[0], testY1[0])

''' !!HIGHLIGHTS!!'''

scaler = MinMaxScaler(feature_range=(-1, 1))
trainX = scaler.fit_transform(trainX)
trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
# print("scaled training x[-1], y[-1]", trainX[-1], trainY[-1])
# print("trainX shape", trainX.shape)
model = Sequential()
model.add(Dense(Din*5 , input_shape=(1, Din*5), activation='tanh'))
# model.add(Dense(Nin, activation='relu'))
model.add(LSTM(Din*5 , activation='tanh'))
model.add(Dropout(0.05))
model.add(Dense(1 , activation='linear'))
model.compile(loss='mse', optimizer="adam", metrics=['accuracy'])
model.fit(trainX, trainY, nb_epoch=100, batch_size=len(trainX), verbose=0)

for i in range(len(testX1)):
    sTXi = np.reshape(testX1[i], [1, -1])
    pY, rY = model.predict(sTXi), testY1[i]
    errM = abs(pY - rY)
    if errM < 0.49999:
        passes += 1
    else:
        fails += 1
    errs.append(errM)
    print("sTXi:", sTXi)
    print("pY:", pY, "rY:", rY, "err %:", errM)

print("\n\nMean Error Margin:", np.mean(errs), "Aggregate Binary Accuracy:", passes, "/", len(testX), "ABA%:", passes / len(testX1))