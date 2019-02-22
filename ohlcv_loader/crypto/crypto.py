# coding: utf-8
import ccxt
import pandas as pd
import json
import os
import time


def main():
    timeframe_dic = {'5m': 5, '1m': 1, '1h': 60, '1d': 1440}
    exchange_dic = {'bitmex': ccxt.bitmex(), 'binance': ccxt.binance(),
                    'bittrex': ccxt.bittrex()}
    cwd = os.getcwd()
    with open(cwd + '/params/crypto.json') as f:
        params = json.loads(f.read())

    exchange_name = params['exchange']
    exchange = exchange_dic[exchange_name]
    beg = exchange.parse8601(params['date_begin'])
    end = exchange.parse8601(params['date_end'])
    limit = 750
    step = timeframe_dic[params['timeframe']] * 60 * 1000 * \
        (limit - 1)  # get 749 candles from fetch_ohlcv
    data, df = pd.DataFrame(), pd.DataFrame()

    while beg < end:
        print(beg)
        try:
            df = pd.DataFrame(exchange.fetch_ohlcv(
                params['symbol'], params['timeframe'], since=beg, limit=limit))
        except Exception:
            print("Exception")
            time.sleep(1)
            continue
        beg += step
        if data.empty:
            data = df.copy()
        else:
            data = (data.append(df)).reset_index(drop=True)

    data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    data['date'] = data['date'].apply(lambda x: exchange.iso8601(x))

    symbol = params['symbol'].replace('/', '_')
    if not os.path.exists(cwd + "/data/" + exchange_name):
        os.mkdir(cwd + "/data/" + exchange_name)
    path = cwd + "/data/" + exchange_name + '/' + symbol + '/'
    if not os.path.exists(path):
        os.mkdir(path)
    date_str = data['date'][0].split(
        'T')[0] + '_' + data['date'][len(data) - 1].split('T')[0]
    data.to_csv(path + exchange_name + '_' + symbol +
                '_' + date_str + '.csv', index=False)


if __name__ == "__main__":
    main()
