from slackclient import SlackClient
from event_scrapper import get_events_table
from datetime import datetime, timedelta
import pandas as pd
import strategies
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    from_days = 0 
    to_days = 32 # display events until (relative to now)
    today = datetime.now().strftime('%d/%m/%Y')
    date_from = (datetime.now() + timedelta(days=from_days)).strftime('%d/%m/%Y')
    date_to = (datetime.now() + timedelta(days=to_days)).strftime('%d/%m/%Y')

    # Get events between date_from and date_to
    events = get_events_table(date_from, date_to)
    
    # Apply your strategy to keep only interesting events on Slack
    slack_client = SlackClient(os.environ.get('SLACK_CRYPTO_EVENTS'))
    strat_df = events[events['eventDate'].between(date_from, date_to)]
    strat_df = strategies.get_positive_events(strat_df).reset_index(drop=True)

    slack_client.api_call(
                    "chat.postMessage",
                    channel="#crypto-events",
                    text=f'*CRYPTO EVENTS UPDATE OF {today}*'
                    )
    slack_client.api_call(
                    "chat.postMessage",
                    channel="#crypto-events",
                    text=strat_df.to_string()
                    )
