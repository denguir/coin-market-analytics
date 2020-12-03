from binance.client import Client as BinanceClient
import pandas as pd


def get_top_24hr_coins(client, market='BTC'):
    tickers = client.get_ticker()
    df = pd.DataFrame(tickers)
    df['priceChangePercent'] = df['priceChangePercent'].astype(float)
    df = df[df['symbol'].apply(lambda  x: x.endswith(market))]
    df['coin'] = df['symbol'].apply(lambda x: x.replace(market, ''))
    df = df.sort_values(by='priceChangePercent', ascending=False)
    return df

if __name__ == '__main__':
    client = BinanceClient(None, None)
    top_coins = get_top_24hr_coins(client, market='BTC')
    print(top_coins)