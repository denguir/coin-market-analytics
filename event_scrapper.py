import requests
import re
import dateparser
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from fake_useragent import UserAgent


def get_events(date_from, date_to):
    '''extracts parts of the HTML page containing main information about events
        between <date_from> and <date_to>
    '''
    events = []
    page = 1
    ua = UserAgent()
    while True:
        url = f"https://coinmarketcal.com/en/?form%5Bdate_range%5D={date_from}%20-%20{date_to}&form%5B\
                keyword%5D=&form%5Bsort_by%5D=&form%5Bsubmit%5D=&form%5Bshow_reset%5D=&page={page}"
        headers = {'User-Agent': ua.random}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        articles = soup.find_all('article')
        if articles:
            events.extend([article.find_all(lambda tag: tag.name == 'h5' and tag.get('class')[0].startswith('card'))
                    for article in articles])
            page += 1
        else:
            break
    return events


def decode_event(event):
    '''decodes a specific event extracted by get_events
    each event is supposed to have 3 elements:
     - a coin (card__coins)
     - a date (card__date)
     - a title (card__title)

     output: json event with
     - coin
     - eventDate
     - eventTitle 
    '''

    coin_text = event[0].text
    date_text = event[1].text
    title_text = event[2].text

    coin_symb = re.search(r"\(([A-Za-z0-9_/]+)\)", coin_text).group(1).strip('\n').strip()
    coin_date = dateparser.parse(
                    date_text.split('(')[0].strip('\n').strip(),
                    date_formats=['%d %B %Y'])
    event_title = title_text.strip('\n').strip()
    event = {'coin': coin_symb, 'eventDate': coin_date, 'eventTitle': event_title}
    return event


def get_events_table(date_from, date_to):
    events = get_events(date_from, date_to)
    struct_events = []
    for event in events:
        try:
            struct_events.append(decode_event(event))
            #print(f'{event[0].text}\n{event[1].text}\n{event[2].text}\n')
        except Exception as e:
            print(e)
            print(f"Decoding error on following event:\n\
                {event[0].text}\n{event[1].text}\n{event[2].text}\n")

    df = pd.DataFrame(struct_events)
    return df


if __name__ == '__main__':

    n_days = 30 # parse events in the upcoming 30 days
    date_from = datetime.now().strftime('%d/%m/%Y')
    date_to = (datetime.now() + timedelta(days=n_days)).strftime('%d/%m/%Y')

    events = get_events_table(date_from, date_to)
    print(events)
