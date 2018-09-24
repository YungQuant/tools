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

def create_binary_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)):
        if i > look_back:
            dataX.append(dataset[i-look_back:i])
            if dataset[i] > dataset[i-1]:
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

currency_pairs, currencies = ["XBTUSD", "ETHUSD", "XRPU18", "TRXU18", "LTCU18", "EOSU18", "ADAU18", "BCHU18", "XRPU18"], ['ltc', 'xbt']
errs, passes, fails = [], 0, 0

#print(exchange.create_order(currency_pairs[0], ))
#orders = exchange.fetch_ohlcv(symbol=currency_pairs[0], timeframe='1m')
orders = load_bitmex_data(currency_pairs[0], "hourly", n_periods=666)
#print(orders)
#ps = [order[-2] for order in orders if isFloat(order[-2])]
ps = orders.ix[:, 'close']
print("order0:\n", orders.ix[0, :])
print("len(ps):", len(ps))
X, Y = create_binary_dataset(ps, 10)

trainX, trainY, testX, testY = X[:int(np.floor(len(X)/2))], Y[:int(np.floor(len(X)/2))], X[int(np.floor(len(X)/2)):], Y[int(np.floor(len(X)/2)):]

''' !!HIGHLIGHTS!!'''


''' VVV 1H / 10 WINDOW / LTCU18 CLOSE PRICES / REG API VVV '''
# model = linear_model.RANSACRegressor() # Mean % Error: 0.008092937591752074
''' VVV 1H / 10 WINDOW / LTCU18 CLOSE PRICES / RB API (500) VVV '''
# model = linear_model.RANSACRegressor() # Mean % Error: 0.00553197478063615
''' VVV 1D / 10 WINDOW / XBTUSD CLOSE PRICES / RB API (666) / BINARY VVV '''
# model = svm.LinearSVC() # Mean % Error: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = svm.NuSVC() # Mean % Error: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = svm.SVC() # Mean % Error: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = linear_model.ARDRegression() # Mean % Error: 0.4951603400387173 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137


'''^^HIGHLIGHTS^^'''

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
# model = linear_model.BayesianRidge() # Mean % Error: 0.005703020058904807
# model = linear_model.Ridge() # Mean % Error: 0.053695055696198084
# model = linear_model.HuberRegressor() # Mean % Error: 0.006980393898696223
# model = linear_model.Lars() # Mean % Error: 0.0055651230021880665
# model = linear_model.Lasso() # Mean % Error: 0.05370095606086554
# model = linear_model.ARDRegression() # Mean % Error: 0.005545638051673693
# model = linear_model.RANSACRegressor() # Mean % Error: 0.00553197478063615

''' VVV 1D / 10 WINDOW / XBTUSD CLOSE PRICES / RB API (666) / BINARY VVV '''
# model = linear_model.Perceptron() # Mean % Error: 0.4801223241590214 Aggregate Binary Accuracy: 170 / 327 ABA%: 0.5198776758409785
# model = linear_model.HuberRegressor() # Mean % Error: 0.5135653468961192 Aggregate Binary Accuracy: 107 / 244 ABA%: 0.4385245901639344
# model = linear_model.Ridge() # Mean % Error: 0.5579634378173305 Aggregate Binary Accuracy: 155 / 327 ABA%: 0.4740061162079511
# model = linear_model.LinearRegression() # Mean % Error: 0.5579634613326042 Aggregate Binary Accuracy: 155 / 327 ABA%: 0.4740061162079511
# model = linear_model.Lars() # Mean % Error: 0.5579634613325997 Aggregate Binary Accuracy: 155 / 327 ABA%: 0.4740061162079511
# model = linear_model.Lasso() # Mean % Error: 0.538326051695379 Aggregate Binary Accuracy: 154 / 327 ABA%: 0.4709480122324159
# model = linear_model.ARDRegression() # Mean % Error: 0.4951603400387173 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = linear_model.PassiveAggressiveRegressor() # Mean % Error: 0.6520641656414019 Aggregate Binary Accuracy: 152 / 327 ABA%: 0.4648318042813456
# model = linear_model.BayesianRidge() # Mean % Error: 0.5447277967128082 Aggregate Binary Accuracy: 156 / 327 ABA%: 0.47706422018348627
# model = linear_model.ElasticNet() # Mean % Error: 0.5470797206607867 Aggregate Binary Accuracy: 153 / 327 ABA%: 0.46788990825688076
# model = linear_model.LassoLarsIC() # Mean % Error: 0.5021317552162353 Aggregate Binary Accuracy: 156 / 327 ABA%: 0.47706422018348627
# model = linear_model.PassiveAggressiveClassifier() # Mean % Error: 0.5229357798165137 Aggregate Binary Accuracy: 156 / 327 ABA%: 0.47706422018348627
# model = linear_model.TheilSenRegressor() # Mean % Error: 0.7684008455130197 Aggregate Binary Accuracy: 144 / 327 ABA%: 0.44036697247706424
# model = linear_model.SGDClassifier() # Mean % Error: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = linear_model.OrthogonalMatchingPursuitCV() # Mean % Error: 0.5063444775502011 Aggregate Binary Accuracy: 156 / 327 ABA%: 0.47706422018348627

# model = svm.LinearSVC() # Mean % Error: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = svm.NuSVC() # Mean % Error: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = svm.SVC() # Mean % Error: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137

''' VVV 1H / 10 WINDOW / XBTUSD CLOSE PRICES / RB API (666) / BINARY VVV '''
# model = linear_model.Perceptron() # Mean Error Margin: 0.5229357798165137 Aggregate Binary Accuracy: 156 / 327 ABA%: 0.47706422018348627
# model = linear_model.HuberRegressor() # Mean Error Margin: 0.5046235528234105 Aggregate Binary Accuracy: 144 / 327 ABA%: 0.44036697247706424
# model = linear_model.Ridge() # Mean Error Margin: 0.4964938076498626 Aggregate Binary Accuracy: 159 / 327 ABA%: 0.48623853211009177
# model = linear_model.LinearRegression() # Mean Error Margin: 0.49649382667826353 Aggregate Binary Accuracy: 159 / 327 ABA%: 0.48623853211009177
# model = linear_model.Lars() # Mean Error Margin: 0.4967295526693805 Aggregate Binary Accuracy: 155 / 327 ABA%: 0.4740061162079511
# model = linear_model.Lasso() # Mean Error Margin: 0.5003288553958611 Aggregate Binary Accuracy: 134 / 327 ABA%: 0.40978593272171254
# model = linear_model.ARDRegression() # Mean Error Margin: 0.4989479000084168 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = linear_model.PassiveAggressiveRegressor() # Mean Error Margin: 0.5182991974582454 Aggregate Binary Accuracy: 156 / 327 ABA%: 0.47706422018348627
# model = linear_model.BayesianRidge() # Mean Error Margin: 0.4971011183349104 Aggregate Binary Accuracy: 145 / 327 ABA%: 0.4434250764525994
# model = linear_model.ElasticNet() # Mean Error Margin: 0.4978288993402717 Aggregate Binary Accuracy: 144 / 327 ABA%: 0.44036697247706424
# model = linear_model.LassoLarsIC() # Mean Error Margin: 0.4960142358454866 Aggregate Binary Accuracy: 155 / 327 ABA%: 0.4740061162079511
# model = linear_model.PassiveAggressiveClassifier() # Mean Error Margin: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = linear_model.TheilSenRegressor() # Mean Error Margin: 0.4907877075391554 Aggregate Binary Accuracy: 161 / 327 ABA%: 0.4923547400611621
# model = linear_model.SGDClassifier() # Mean Error Margin: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
# model = linear_model.OrthogonalMatchingPursuitCV() # Mean Error Margin: 0.4997037142955298 Aggregate Binary Accuracy: 25 / 327 ABA%: 0.0764525993883792

# model = svm.LinearSVC() # Mean Error Margin: 0.5229357798165137 Aggregate Binary Accuracy: 156 / 327 ABA%: 0.47706422018348627
# model = svm.NuSVC() # Mean Error Margin: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
model = svm.SVC() # Mean Error Margin: 0.47706422018348627 Aggregate Binary Accuracy: 171 / 327 ABA%: 0.5229357798165137
model.fit(trainX, trainY)

for i in range(len(testX)):
    sTXi = np.reshape(testX[i], [1, -1])
    pY, rY = model.predict(sTXi), testY[i]
    errM = abs(pY - rY)
    if errM < 0.49999:
        passes += 1
    else:
        fails += 1
    errs.append(errM)
    print("sTXi:", sTXi)
    print("pY:", pY, "rY:", rY, "err %:", errM)

print("\n\nMean Error Margin:", np.mean(errs), "Aggregate Binary Accuracy:", passes, "/", len(testX), "ABA%:", passes / len(testX))