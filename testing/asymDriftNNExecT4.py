import ccxt, os
import sklearn as sk
import requests, pandas as pan
from sklearn.preprocessing import MinMaxScaler
from sklearn import svm, linear_model
from sklearn.metrics import mean_squared_error
import keras
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.layers import Dense, Flatten, BatchNormalization, LeakyReLU, PReLU
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

def tokyoDrift(currency="XBTUSD", dump="01"):
    path = f'../../tokyoScpDump/output/dump{dump}/bitmex_{currency}_1min.txt'
    data = []
    if os.path.isfile(path) == False:
        print(f'could not source {path} data')
    else:
        fileP = open(path, "r")
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

def create_binary_h2d_ohlcv_dataset(dataset, look_back, ohlcv=-1):
    look_back *= 24
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        datum = []
        if i > look_back:
            for k in range(len(dataset[i-look_back:i])):
                for j in range(len(dataset[i-look_back:i][k])):
                    datum.append(dataset[i-look_back:i][k][j])
            dataX.append(datum)
            # if dataset[i+1][-1] > dataset[i][-1]:
            if np.mean([d[ohlcv] for d in dataset[i+1:i+25]]) > dataset[i][ohlcv]:
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

def create_agg_ohlcv_dataset(dataset, look_back, curr=0):
    dataX, dataY, finX = dataset, [], []
    for z in range(len(dataset)-1):
        for i in range(len(dataset[z])-1):
            # datum = []
            # if i > look_back:
            #     for k in range(len(dataset[z][i-look_back:i])):
            #         for j in range(len(dataset[z][i-look_back:i][k])):
            #             datum.append(dataset[z][i-look_back:i][k][j])
            #dataX.append(datum)

            if z == curr: dataY.append(dataset[z][i+1][-1])

    dataX, dataY = np.array(dataX), np.array(dataY)
    print(f'preprocessing shapes: dataX {dataX.shape} dataY {dataY.shape}')
    for t in range(len(dataX[0]) -1):
        if len(dataX[0][t][:]) == 4 and len(dataX[1][t][:]) == 4 and len(dataX[2][t][:]) == 4 and len(dataX[3][t][:]) == 4 and len(dataX[4][t][:]) == 4 and len(dataX[5][t][:]) == 4 and len(dataX[6][t][:]) == 4 and len(dataX[7][t][:]) == 4 and len(dataX[8][t][:]) == 4:
            datum1 = np.concatenate([dataX[0][t][:], dataX[1][t][:], dataX[2][t][:], dataX[3][t][:], dataX[4][t][:], dataX[5][t][:], dataX[6][t][:], dataX[7][t][:], dataX[8][t][:]])
            finX.append(datum1)
            #print(datum1, finX)
    print(f'postprocessing shapes: dataX {np.array(finX).shape} dataY {dataY.shape}')
    dataX = []
    for x in range(len(finX)):
        datum2 = []
        if x > look_back:
            for k in range(len(finX[x-look_back:x])):
                for j in range(len(finX[x-look_back:x][k])):
                    datum2.append(finX[x-look_back:x][k][j])
            dataX.append(datum2)
    print(f'post-postprocessing shapes: dataX {np.array(dataX).shape} dataY {dataY.shape}')
    return np.array(dataX), np.array(dataY)

def create_nerfed_agg_ohlcv_dataset(dataset, look_back, curr=0, ohlcv=-1):
    dataX, dataY, finX = dataset, [], []
    for z in range(len(dataset)-1):
        for i in range(len(dataset[z])-1):
            # datum = []
            # if i > look_back:
            #     for k in range(len(dataset[z][i-look_back:i])):
            #         for j in range(len(dataset[z][i-look_back:i][k])):
            #             datum.append(dataset[z][i-look_back:i][k][j])
            #dataX.append(datum)

            if z == curr: dataY.append(dataset[z][i+1][ohlcv])

    dataX, dataY = np.array(dataX), np.array(dataY)
    print(f'preprocessing shapes: dataX {dataX.shape} dataY {dataY.shape}')
    for t in range(min([len(x) for x in dataX]) -1):
        if len(dataX[0][t][:]) == 4 and len(dataX[1][t][:]) == 4 and len(dataX[2][t][:]) == 4 and len(dataX[3][t][:]) == 4 and len(dataX[4][t][:]) == 4:
            datum1 = np.concatenate([dataX[0][t][:], dataX[1][t][:], dataX[2][t][:], dataX[3][t][:], dataX[4][t][:]])
            finX.append(datum1)
            #print(datum1, finX)
    print(f'postprocessing shapes: dataX {np.array(finX).shape} dataY {dataY.shape}')
    dataX = []
    for x in range(len(finX)):
        datum2 = []
        if x > look_back:
            for k in range(len(finX[x-look_back:x])):
                for j in range(len(finX[x-look_back:x][k])):
                    datum2.append(finX[x-look_back:x][k][j])
            dataX.append(datum2)
    print(f'post-postprocessing shapes: dataX {np.array(dataX).shape} dataY {dataY.shape}')
    return np.array(dataX), np.array(dataY)

def create_nerfed_agg_full_ohlcv_dataset(dataset, look_back, curr=0):
    dataX, dataY, finX = dataset, [], []
    for z in range(len(dataset)-1):
        for i in range(len(dataset[z])-1):
            # datum = []
            # if i > look_back:
            #     for k in range(len(dataset[z][i-look_back:i])):
            #         for j in range(len(dataset[z][i-look_back:i][k])):
            #             datum.append(dataset[z][i-look_back:i][k][j])
            #dataX.append(datum)

            if z == curr: dataY.append(dataset[z][i+1])

    dataX, dataY = np.array(dataX), np.array(dataY)
    print(f'preprocessing shapes: dataX {dataX.shape} dataY {dataY.shape}')
    for t in range(min([len(x) for x in dataX]) -1):
        if len(dataX[0][t][:]) == 4 and len(dataX[1][t][:]) == 4 and len(dataX[2][t][:]) == 4 and len(dataX[3][t][:]) == 4 and len(dataX[4][t][:]) == 4:
            datum1 = np.concatenate([dataX[0][t][:], dataX[1][t][:], dataX[2][t][:], dataX[3][t][:], dataX[4][t][:]])
            finX.append(datum1)
            #print(datum1, finX)
    print(f'postprocessing shapes: dataX {np.array(finX).shape} dataY {dataY.shape}')
    dataX = []
    for x in range(len(finX)):
        datum2 = []
        if x > look_back:
            for k in range(len(finX[x-look_back:x])):
                for j in range(len(finX[x-look_back:x][k])):
                    datum2.append(finX[x-look_back:x][k][j])
            dataX.append(datum2)
    print(f'post-postprocessing shapes: dataX {np.array(dataX).shape} dataY {dataY.shape}')
    return np.array(dataX), np.array(dataY)

def create_ohlcv_dataset1(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)-1):
        datum = []
        if i > look_back:
            for k in range(len(dataset[i-look_back:i])):
                datum.append(dataset[i-look_back:i][k])
            dataX.append(datum)

            dataY.append(dataset[i+1][-1])
    return np.array(dataX), np.array(dataY)

def disectPanda(panda):
    bodyParts = []
    for i in range(len(panda.ix[:, 'close'])):
        bodyParts.append([panda.ix[i, 'open'], panda.ix[i, 'high'], panda.ix[i, 'low'], panda.ix[i, 'close']])
    return bodyParts

def get_agg_bitmex_data(currency_pairs):
    data = []
    for i in range(len(currency_pairs)):
        datum = disectPanda(load_bitmex_data(currency_pairs[i], "hourly", n_periods=666))
        data.append(datum)
    return data

def get_agg_cdd_data(currency_pairs):
    data = []
    for i in range(len(currency_pairs)):
        orders = get_CDD_data(currency_pairs[i])
        ps = [[float(order[0]), float(order[1]), float(order[2]), float(order[3])] for order in orders]
        data.append(ps)
    return np.array(data)


# currency_pairs, currencies = ["XBTUSD", "ETHUSD", "XRPU18", "TRXU18", "LTCU18", "EOSU18", "ADAU18", "BCHU18"], ["BTCUSD", "ADABTC", "ETHUSD", "LTCBTC", "XRPBTC"]
currency_pairs, currencies = ["XBTUSD", "ETHUSD", "XRPU18", "LTCU18", "BCHU18"], ["BTCUSD", "ADABTC", "ETHUSD", "LTCBTC", "XRPBTC"]
errs, passes, fails = [], 0, 0

#print(exchange.create_order(currency_pairs[0], ))
#orders = exchange.fetch_ohlcv(symbol=currency_pairs[0], timeframe='1m')
# orders1 =
ps1 = np.array(get_agg_bitmex_data(currency_pairs))
# orders1 = load_bitmex_data(currency_pairs[0], "hourly", n_periods=666)
ps = np.array(get_agg_cdd_data(currencies))
#print(orders)
#ps = [order[-2] for order in orders if isFloat(order[-2])]

print("order0:\n", ps[0])
print("shape(ps):", ps.shape)
print("order1[0]:\n", ps1[0])
print("shape(ps1):", ps1.shape)
Din = 30
X, Y = create_nerfed_agg_full_ohlcv_dataset(ps, Din, curr=0)
print("X0:\n", X[0])
print("shape(X):", X.shape)
X1, Y1 = create_nerfed_agg_full_ohlcv_dataset(ps1, Din, curr=0)
print("X10:\n", X1[0])
print("shape(X1):", X1.shape)
trainX, trainY, testX, testY = X[:int(np.floor(len(X)/1.01))], Y[:int(np.floor(len(X)/1.01))], X[int(np.floor(len(X)/1.01)):], Y[int(np.floor(len(X)/1.01)):]
trainX1, trainY1, testX1, testY1 = X1[:int(np.floor(len(X1)/99))], Y1[:int(np.floor(len(X1)/99))], X1[int(np.floor(len(X1)/99)):], Y1[int(np.floor(len(X1)/99)):]
print(testX[0], testY[0])
print("\n", testX1[0], testY1[0])

# scaler = MinMaxScaler(feature_range=(-1, 1))
# trainX = scaler.fit_transform(trainX)
trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
#testX1 = np.reshape(testX1, (testX1.shape[0], 1, testX1.shape[1]))
# print("scaled training x[-1], y[-1]", trainX[-1], trainY[-1])
# print("trainX shape", trainX.shape)

reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.9, patience=5, min_lr=0.000001)
opt = keras.optimizers.Adam(lr=0.0009, epsilon=42, decay=0.001, amsgrad=False)

model = Sequential()
model.add(Dense(Din*4*5, input_shape=(1, Din*4*5), activation='selu'))
model.add(Dense(Din*4*5, activation='relu'))
model.add(LSTM(Din*4*5, activation='selu', return_sequences=False))
model.add(Dropout(0.005))
#model.add(Flatten())
model.add(Dense(4, activation='linear'))
model.compile(loss="mse", optimizer=opt, metrics=['accuracy'])
model.fit(trainX, trainY, nb_epoch=1000, batch_size=100, verbose=1, callbacks=[reduce_lr])

for i in range(len(testX1)):
    #sTXi = np.reshape(testX1[i], [1, -1])
    sTXi = np.reshape(testX1[i], (1, 1, testX1[i].shape[0]))
    # sTXi = testX1[i]
    pY, rY = model.predict(sTXi)[0], testY1[i]
    print(pY, rY)
    pO, pH, pL, pC = pY[0], pY[1], pY[2], pY[3]
    rO, rH, rL, rC = rY[0], rY[1], rY[2], rY[3]
    eO, eH, eL, eC = abs(pO - rO) / rO, abs(pH - rH) / rH, abs(pL - rL) / rL, abs(pC - rC) / rC
    errM = [eO, eH, eL, eC]
    if rC > testY1[i-1][-1] and pC > testY1[i-1][-1] or rC < testY1[i-1][-1] and pC < testY1[i-1][-1]:
        passes += 1
    else:
        fails += 1
    errs.append(errM)
    print("sTXi:", sTXi)
    print("pY:", pY, "rY:", rY, "err %:", errM)

print("\n\nMean Open Error %:", np.mean(errs[:][0]), "Mean High Error %:", np.mean(errs[:][1]), "Mean Low Error %:", np.mean(errs[:][2]), "Mean Close Error %:", np.mean(errs[:][3]),"Aggregate Binary Accuracy:", passes, "/", len(testY1), "ABA%:", passes / len(testY1))