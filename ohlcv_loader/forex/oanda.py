import os
import json
from oandapyV20 import API
import pandas as pd
from dateutil import parser
import oandapyV20.endpoints.instruments as instruments


def reform_dataset(dataset):
    dataset['close'] = (dataset['close_ask'] + dataset['close_bid']) / 2
    dataset['high'] = (dataset['high_ask'] + dataset['high_bid']) / 2
    dataset['low'] = (dataset['low_ask'] + dataset['low_bid']) / 2
    dataset['open'] = (dataset['open_ask'] + dataset['open_bid']) / 2
    return dataset[['time', 'open', 'high', 'low', 'close', 'volume']]


def get_candles(data, params):
    results = []
    if params['price'] == 'A':
        results = [{"time": x['time'], "open":float(x['ask']['o']), "high":float(x['ask']['h']),
                    "low":float(x['ask']['l']), "close":float(x['ask']['c']), "volume":float(x['volume'])} for x in data['candles']]
    elif params['price'] == 'B':
        results = [{"time": x['time'], "open":float(x['bid']['o']), "high":float(x['bid']['h']),
                    "low":float(x['bid']['l']), "close":float(x['bid']['c']), "volume":float(x['volume'])} for x in data['candles']]
    elif params['price'] == 'AB':
        results = [{"time": x['time'], "open_ask":float(x['ask']['o']), "high_ask":float(x['ask']['h']),
                    "low_ask":float(x['ask']['l']), "close_ask":float(x['ask']['c']),
                    "open_bid":float(x['bid']['o']), "high_bid":float(x['bid']['h']),
                    "low_bid":float(x['bid']['l']), "close_bid":float(x['bid']['c']),
                    "volume":float(x['volume'])
                    } for x in data['candles']]
    else:
        print("Check 'price' in params")
    return results


def get_step(granularity):
    step = 0
    symbol = granularity[0]
    number = int(granularity[1:])
    if symbol == 'S':
        step = 4320 * number
    elif symbol == 'M':
        step = 4320 * number * 60
    elif symbol == 'H':
        step = 4320 * number * 60 * 60
    return step


def main():
    cwd = os.getcwd()
    with open(cwd + '/params/oanda.json') as f:
        params = json.loads(f.read())
    print(params)
    client = API(params['access_token'])
    step = get_step(params['granularity'])
    begin_unix = int(parser.parse(params['begin_date']).strftime('%s'))
    end_unix = int(parser.parse(params['end_date']).strftime('%s'))
    dataset = pd.DataFrame()
    d = {"granularity": params['granularity'], "price": params['price']}
    ####
    i = begin_unix
    print(begin_unix, end_unix, step)

    if step != 0:
        while i <= end_unix:
            d['from'] = str(i)
            i += step
            if i > end_unix:
                i = end_unix
            d['to'] = str(i)
            try:
                r = instruments.InstrumentsCandles(
                    instrument=params['instrument'], params=d)
                data = client.request(r)
            except:
                print("Request to oanda failed")
                break
            results = get_candles(data, params)
            if not results:
                break
            df = pd.DataFrame(results)
            if dataset.empty:
                dataset = df.copy()
            else:
                dataset = dataset.append(df, ignore_index=True)
        if not dataset.empty:
            dataset = dataset.dropna()
            dataset = dataset[dataset['volume'] != 0]
            dataset.reset_index(inplace=True, drop=True)
            if params['price'] == 'AB':
                dataset = reform_dataset(dataset)
            if not os.path.exists(cwd + "/data/"):
                os.mkdir(cwd + "/data/")
            if not os.path.exists(cwd + "/data/oanda/"):
                os.mkdir(cwd + "/data/oanda/")
            dataset.to_csv(cwd + "/data/oanda/" + params['instrument'] + "_" + params['price'] + "_" + params['granularity'] +
                           "_" + dataset['time'][0].split('T')[0] + "_" + dataset['time'][len(dataset) - 1].split('T')[0] + ".csv", index=False)
        else:
            print("Dataset appears to be empty, check params")

    else:
        print("Step equals 0, check 'granularity' in params")


main()
