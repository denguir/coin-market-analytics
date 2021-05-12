from slackclient import SlackClient
from event_scrapper import get_events_table
from datetime import datetime, timedelta
import pandas as pd
import strategies
import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    from_days = 0  # parse events from (relative to now)
    to_days = 180 #  parse events until (relative to now)
    to_days_slack = 32 # display events until (relative to now)
    today = datetime.now().strftime('%d/%m/%Y')
    date_from = (datetime.now() + timedelta(days=from_days)).strftime('%d/%m/%Y')
    date_to = (datetime.now() + timedelta(days=to_days)).strftime('%d/%m/%Y')

    # Get events between date_from and date_to
    events = get_events_table(date_from, date_to)
    
    # Apply your strategy to keep only interesting events on Slack
    slack_client = SlackClient(os.environ['SLACK_CRYPTO_EVENTS'])
    date_to_slack = (datetime.now() + timedelta(days=to_days_slack)).strftime('%Y-%m-%d')
    strat_df = events[events['eventDate'] < date_to_slack]
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

    # Save new events table on event database
    date_from = datetime.strptime(date_from, '%d/%m/%Y').strftime('%Y-%m-%d')
    prev_events = pd.read_csv(os.path.join(ROOT_DIR, 'history/events.csv'))
    prev_events = prev_events[prev_events['eventDate'] < date_from]
    new_events = events.append(prev_events, ignore_index=True).reset_index(drop=True)
    new_events = new_events.sort_values(by=['eventDate', 'coin', 'votes'], ascending=[True, True, False])
    new_events.to_csv(os.path.join(ROOT_DIR, 'history/events.csv'), index=False)
