import os
import numpy as np
import re

#tickers = ["BTC_ETH", "BTC_XMR", "BTC_DASH", "BTC_XRP", "BTC_FCT", "BTC_MAID", "BTC_ZEC", "BTC_LTC"]
outputs = []
fileCuml = []
best = {}; kurt = []; bests = []
env = "output/"


# 1. load all the logs in output
log_file_names = os.listdir('output')

def get_num(str):
    tmp = ""
    for i, l in enumerate(str):
        if l.isnumeric() or l == ".":
            tmp.append(l)
    return tmp

# line number parser
num_regex = r"[-+]?\d*\.\d+|\d+"
def parse_line(line):
    return float(re.findall(num_regex, line)[0])

# where starting line number, filename, and properties are collected
anals = []


for fi, filename in enumerate(log_file_names):
    # print("fi: ", fi)
    # print("file: ", filename)

    fp = open("output/" + filename)

    anal = {}
    for li, line in enumerate(fp):
        if line.find("K") == 0:
            anal['filename'] = filename
            anal['line_number'] = li
            anal['k'] = parse_line(line)
        if line.find("D") == 0:
            anal['d'] = parse_line(line)
        if line.find("mdd") == 0:
            anal['mdd'] = parse_line(line)
        if line.find("bitchCunt") == 0:
            anal['bc'] = parse_line(line)
        if line.find("Cumulative") > 5:
            anal['cuml'] = parse_line(line)
            if anal['cuml'] > 1.3:
                anals.append(anal)
            anal = {}


    fp.close()

def similar(a, b):
    diff = abs(b - a)
    tolerance = a * 0.0 # TODO: tune this percentage in
    return diff <= tolerance


# we want to find instances where K, D, and bitchCunt are similar accross different timeframes/fidelities and currencies
# compare every entry with every other entry for similarities

#print("anals: ", anals)
similar_anals = []
for i, anal in enumerate(anals):
    for k, anal2 in enumerate(anals[i + 1:]):
        simk = similar(anal['k'], anal2['k'])
        simd = similar(anal['d'], anal2['d'])
        simbc = similar(anal['bc'], anal2['bc'])
        if simk and simd and simbc:
            similar_anals.append([anal, anal2])

for i in range(len(similar_anals)):
    print("\nsimilar_anal: ", similar_anals[i])
