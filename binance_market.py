from binance.client import Client
from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm


def date_to_timestamp(date, client):
    # convert date into timestamp using the client server time
    server_time = client.get_server_time()['serverTime'] # in ms
    offset = server_time - int(datetime.now().timestamp() * 1000)
    ts = int(date.timestamp() * 1000 + offset)
    return ts


def get_open_avg_price_change_percent(klines_today, klines_yesterday):
    # average on open value of tickers
    try:
        avg_today = sum(float(x[1]) for x in klines_today) / len(klines_today)
        avg_yesterday = sum(float(x[1]) for x in klines_yesterday) / len(klines_yesterday)
        avg_price_change_percent = (avg_today / avg_yesterday - 1.0) * 100
    except ZeroDivisionError:
        # if ZeroDivisionError, it means the coin is not listed anymore
        avg_price_change_percent = None
    return avg_price_change_percent


def get_avg_price_change(df, client, resolution):
    today = date_to_timestamp(datetime.now(), client)
    yesterday = today - 86_400_000 # -1 day in ms
    bfr_yesterday = yesterday - 86_400_000 # -1 day in ms
    avg_price_change_map = {}
    for symbol in tqdm(df['symbol']):
        if symbol not in avg_price_change_map.keys():
            today_klines = client.get_historical_klines(
                symbol, resolution, yesterday, today)
            yesterday_klines = client.get_historical_klines(
                symbol, resolution, bfr_yesterday, yesterday)
            avg_price_change_map[symbol] = get_open_avg_price_change_percent(today_klines, yesterday_klines)
    df['avgPriceChangePercent'] = np.round(df['symbol'].map(avg_price_change_map), 2)
    return df


def get_avg_24h_price(events, client, market='BTC', resolution='30m'):
    tickers = client.get_ticker()
    df = pd.DataFrame(tickers)
    events['symbol'] = events['coin'].apply(lambda x: x + market)
    df = pd.merge(df, events, how='inner', on='symbol')
    df['priceChangePercent'] = np.round(df['priceChangePercent'].astype(float), 2)
    df = get_avg_price_change(df, client, resolution)
    return df