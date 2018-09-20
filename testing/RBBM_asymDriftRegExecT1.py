import ccxt
import sklearn as sk
import requests, pandas as pan
from sklearn.preprocessing import MinMaxScaler
from sklearn import svm, linear_model
from sklearn.metrics import mean_squared_error
import numpy as np

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

currency_pairs, currencies = ['LTCU18'], ['ltc']
errs = []

#print(exchange.create_order(currency_pairs[0], ))
#orders = exchange.fetch_ohlcv(symbol=currency_pairs[0], timeframe='1m')
orders = load_bitmex_data(currency_pairs[0], "hourly", n_periods=500)
#print(orders)
#ps = [order[-2] for order in orders if isFloat(order[-2])]
ps = orders.ix[:, 'close']
print(ps)
X, Y = create_dataset(ps, 10)

trainX, trainY, testX, testY = X[:int(np.floor(len(X)/1.2))], Y[:int(np.floor(len(X)/1.2))], X[int(np.floor(len(X)/1.2)):], Y[int(np.floor(len(X)/1.2)):]

''' VVV 1H / 10 WINDOW / LTCU18 CLOSE PRICES / REG API VVV '''
# model = linear_model.BayesianRidge() # Mean % Error: 0.02025354214895091
# model = linear_model.Ridge() # Mean % Error: 0.050484925340484356
# model = linear_model.HuberRegressor() # Mean % Error: 0.014063285819013012
# model = linear_model.Lars() # Mean % Error: 0.010000416749448777
# model = linear_model.Lasso() # Mean % Error: 0.05048526961697335
# model = linear_model.LinearRegression() # Mean % Error: 0.010073936285900685
# model = linear_model.ARDRegression() # Mean % Error: 0.01382198958869686
# model = linear_model.RANSACRegressor() # Mean % Error: 0.008092937591752074

''' VVV 1H / 10 WINDOW / LTCU18 CLOSE PRICES / RB API (500) VVV '''
# model = linear_model.LinearRegression() # Mean % Error: 0.005631468683177288
model = linear_model.BayesianRidge() # Mean % Error: 0.005703020058904807
# model = linear_model.Ridge() # Mean % Error: 0.053695055696198084
# model = linear_model.HuberRegressor() # Mean % Error: 0.006980393898696223
# model = linear_model.Lars() # Mean % Error: 0.0055651230021880665
# model = linear_model.Lasso() # Mean % Error: 0.05370095606086554
# model = linear_model.ARDRegression() # Mean % Error: 0.005545638051673693
# model = linear_model.RANSACRegressor() # Mean % Error: 0.00553197478063615

#model = linear_model.Ridge()
model.fit(trainX, trainY)

for i in range(len(testX)):
    sTXi = np.reshape(testX[i], [1, -1])
    pY, rY = model.predict(sTXi), testY[i]
    errP = abs(pY - rY) / rY
    errs.append(errP)
    print("sTXi:", sTXi)
    print("pY:", pY, "rY:", rY, "err %:", errP)

print("\n\nMean % Error:", np.mean(errs))