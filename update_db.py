from event_scrapper import get_events_table
from datetime import datetime, timedelta
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    from_days = -30  # parse events from (relative to now)
    to_days = 180 #  parse events until (relative to now)
    today = datetime.now().strftime('%d/%m/%Y')
    date_from = (datetime.now() + timedelta(days=from_days)).strftime('%d/%m/%Y')
    date_to = (datetime.now() + timedelta(days=to_days)).strftime('%d/%m/%Y')

    # Get events between date_from and date_to
    events = get_events_table(date_from, date_to)
    
    # Save new events table on event database
    date_from = datetime.strptime(date_from, '%d/%m/%Y').strftime('%Y-%m-%d')
    prev_events = pd.read_csv(os.path.join(ROOT_DIR, 'history/events.csv'))
    prev_events = prev_events[prev_events['eventDate'] < date_from]
    new_events = events.append(prev_events, ignore_index=True).reset_index(drop=True)
    new_events = new_events.sort_values(by=['eventDate', 'coin', 'votes'], ascending=[True, True, False])
    new_events.to_csv(os.path.join(ROOT_DIR, 'history/events.csv'), index=False)
