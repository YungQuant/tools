import os.path
import numpy as np
import re

#tickers = ["BTC_ETH", "BTC_XMR", "BTC_DASH", "BTC_XRP", "BTC_FCT", "BTC_MAID", "BTC_ZEC", "BTC_LTC"]
tickers = ["BTC_ETH"]
outputs = []
fileCuml = []
best = {}; kurt = []; bests = []
env = "output/"
run = "bbBreak_1mEOSU18_9.21.18_output.txt"

for i, tik in enumerate(tickers):
    outputs.append("" + env + run)  # + tik + "_output.txt")

def  getNum(str):
    tmp = ""
    for i, l in enumerate(str):
        if l.isnumeric() or l == ".":
            tmp.append(l)
    return tmp

for fi, file in enumerate(outputs):
    i = 0
    Ks, Ds, MDDs, bCs = [], [], [], []
    with open(file) as fp:
        fd = fp.readlines()
        for li, line in enumerate(fd[int(len(fd) * 0.0001):int(len(fd) * 0.99)]):
            best = {}
            if line.find("K") > 1:
                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)  #line[int(np.floor(len(line) - 25)):])
                num = float(tmp[0])
                best['k'] = num
            if line.find("D") > 1:
                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)  #line[int(np.floor(len(line) - 25)):])
                num = float(tmp[0])
                best['d'] = num
            if line.find("mdd") > 1:
                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)  #line[int(np.floor(len(line) - 25)):])
                num = float(tmp[0])
                best['mdd'] = num
            if line.find("bitchCunt") > 5:
                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)  #line[int(np.floor(len(line) - 25)):])
                num = float(tmp[0])
                best['bc'] = num
            if line.find("Cumulative") > 5:
                tmp = re.findall(r"[-+]?\d*\.\d+|\d+", line)  #line[int(np.floor(len(line) - 25)):])
                num = float(tmp[0])
                best['cuml'] = num
                bests.append(best)



    fp.close()


newlist = sorted(bests, key=lambda k: k['cuml'])
for i in range(len(newlist)):
    print(newlist[i])