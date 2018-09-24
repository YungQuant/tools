import os
import numpy as np
import re

#tickers = ["BTC_ETH", "BTC_XMR", "BTC_DASH", "BTC_XRP", "BTC_FCT", "BTC_MAID", "BTC_ZEC", "BTC_LTC"]
outputs = []
fileCuml = []
best = {}; kurt = []; bests = []
env, env1 = "seg_output/bbBreak/eos/", "seg_output/bbBreak/eos/"


# 1. load all the logs in output

log_file_names = os.listdir(env1)

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

    fp = open(env + filename)

    anal = {}
    for li, line in enumerate(fp):
        if line.find("K") == 0:
            anal['filename'] = filename
            anal['line_number'] = li
            anal['k'] = parse_line(line)
        if line.find("D") == 0:
            anal['d'] = parse_line(line)
        if line.find("Len") == 0:
            anal['len'] = parse_line(line)
        if line.find("MDD") == 0:
            anal['mdd'] = parse_line(line)
        if line.find("bitchCunt") == 0:
            anal['bc'] = parse_line(line)
        if line.find("Cumulative") > 5:
            anal['cuml'] = parse_line(line)
            if anal['cuml'] > 1.01 and anal['cuml'] < 1.5 and anal['len'] > 3 and anal['len'] < 300 and (anal['cuml'] - 1) > anal['mdd']:
                anals.append(anal)
            anal = {}


    fp.close()

def similar(a, b):
    diff = abs(b - a)
    tolerance = a * 0.0 # TODO: tune this percentage in
    return diff <= tolerance


# we want to find instances where K, D, and bitchCunt are similar accross different timeframes/fidelities and currencies
# compare every entry with every other entry for similarities

similar_anals = []
for i, anal in enumerate(anals):
    for k, anal2 in enumerate(anals[i + 1:]):
        if anal['filename'] == anal2['filename']: # don't compare stuff in same file
            continue
        simk = similar(anal['k'], anal2['k'])
        simd = similar(anal['d'], anal2['d'])
        simbc = similar(anal['bc'], anal2['bc'])
        if anal['filename'] != anal2['filename']:
            if simk and simd and simbc:
                similar_anals.append([anal, anal2])


similar_anals = sorted(similar_anals, key=lambda k: k[0]['cuml'])

for i in range(len(similar_anals)):
    print("\nsimilar_anal: ", similar_anals[i])
