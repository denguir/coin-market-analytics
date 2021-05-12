import pandas as pd
from binance.client import Client
from binance_market import get_avg_24h_price

__client__ = Client(None, None)


def get_positive_events(events, market='BTC'):
    df = get_avg_24h_price(events, __client__, market=market)
    df = df[df['avgPriceChangePercent'] > 0.0]
    df = df[['eventDate', 'coin', 'avgPriceChangePercent', 'eventTitle', 'postDate']]
    df = df.sort_values(['eventDate', 'coin', 'avgPriceChangePercent'], ascending=[True, True, False])
    return df
