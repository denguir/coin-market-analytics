from binance.client import Client as BinanceClient
from slackclient import SlackClient
from binance_market import get_top_24hr_coins
from event_scrapper import get_events_table
from datetime import datetime, timedelta
import pandas as pd


def get_positive_events(events, top_coins):
    df = events.merge(top_coins, how='inner', on='coin')
    df = df[df['priceChangePercent'] > 0.0]
    df = df.sort_values(by='eventDate', ascending=True)
    df = df[['eventDate', 'coin', 'priceChangePercent', 'eventTitle']]
    return df

    
if __name__ == '__main__':

    n_days = 30 # parse events in the upcoming 30 days
    date_from = datetime.now().strftime('%d/%m/%Y')
    date_to = (datetime.now() + timedelta(days=n_days)).strftime('%d/%m/%Y')

    client = BinanceClient(None, None)
    slack_client = SlackClient("xoxp-248224849815-246491106496-1529355217619-69af0440dd3b43c1f9baa293aea1ad14")

    events = get_events_table(date_from, date_to)
    top_coins = get_top_24hr_coins(client, market='BTC')

    positive_events = get_positive_events(events, top_coins).reset_index(drop=True)

    slack_client.api_call(
                    "chat.postMessage",
                    channel="#crypto-events",
                    text='\n' + 20 * '#' + '\n' + 4 * '\t' + f'CRYPTO EVENTS UPDATE DU {date_from}\n' + 20 * '#' + '\n'
                    )
    slack_client.api_call(
                    "chat.postMessage",
                    channel="#crypto-events",
                    text=positive_events.to_string()
                    )
    
    


