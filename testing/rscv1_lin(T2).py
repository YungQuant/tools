import ccxt, os
import sklearn as sk, scipy.stats as spst
import requests, pandas as pan
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn import svm, linear_model
from sklearn.metrics import mean_squared_error, classification_report
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
            dataX.append(dataset[i-look_back:i])
            if dataset[i+1] > dataset[i]:
                dataY.append(1)
            else:
                dataY.append(0)
    return np.array(dataX), np.array(dataY)

currency_pairs, currencies = ["XBTUSD", "ETHUSD", "XRPU18", "TRXU18", "LTCU18", "EOSU18", "ADAU18", "BCHU18", "XRPU18"], ['ltc', 'xbt']
errs, passes, fails = [], 0, 0

#print(exchange.create_order(currency_pairs[0], ))
#orders = exchange.fetch_ohlcv(symbol=currency_pairs[0], timeframe='1m')
#orders = load_bitmex_data(currency_pairs[1], "hourly", n_periods=666)
orders = get_CDD_data("BTCUSD")
#print(orders)
ps = [float(order[3]) for order in orders]
#ps = orders.ix[:, 'close']
print("len(ps):", len(ps))
X, Y = create_dataset(ps, 10)

trainX, trainY, testX, testY = X[:int(np.floor(len(X)/1.2))], Y[:int(np.floor(len(X)/1.2))], X[int(np.floor(len(X)/1.2)):], Y[int(np.floor(len(X)/1.2)):]

# model = linear_model.LinearRegression()
# model.fit(trainX, trainY)
#
# for i in range(len(testX)):
#     sTXi = np.reshape(testX[i], [1, -1])
#     pY, rY = model.predict(sTXi), testY[i]
#     errP = abs(pY - rY) / rY
#     if (rY > testY[i-1] and pY > testY[i-1]) or (rY < testY[i-1] and pY < testY[i-1]):
#         passes += 1
#     else:
#         fails += 1
#     errs.append(errP)
#     print("sTXi:", sTXi)
#     print("pY:", pY, "rY:", rY, "err %:", errP)
#
# print("\n\nMean % Error:", np.mean(errs), "Aggregate Binary Accuracy:", passes, "/", len(testX), "ABA%:", passes / len(testX))

def test_RandomizedSearchCV():

    '''
    Use RandomizedSearchCV and LogisticRegression, to improve C, multi_class.
    :return:  None
    '''
    aa = np.arange(0, 30, 0.01)
    tuned_parameters ={'alpha': aa}
    clf = RandomizedSearchCV(linear_model.ElasticNet(),
                        tuned_parameters, n_iter=3000)
    clf.fit(trainX, trainY)
    print("Best parameters set found:", clf.best_params_)
    # print("Randomized Grid scores:")
    # for params, mean_score, scores in clf.grid_scores_:
    #          print("\t%0.3f (+/-%0.03f) for %s" % (mean_score, scores.std() * 2, params))

    print("Optimized Score:", clf.score(testX, testY))
    print("Detailed classification report:")
    y_true, y_pred = testY, clf.predict(testX)
    print(classification_report(y_true, y_pred))

test_RandomizedSearchCV()
#print(spst.expon(scale=100).pdf)