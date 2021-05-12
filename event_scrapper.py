import requests
import re
import dateparser
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm
from fake_useragent import UserAgent


def get_event_coin(article):
    '''Extracts event coin from article'''
    try:
        tag = article.find('h5', {"class": "card__coins"})
        coin = tag.text
        coin_symb = re.search(r"\(([A-Za-z0-9-_./]+)\)", coin).group(1).strip()
    except AttributeError:
        coin_symb = None
    return coin_symb


def get_event_date(article):
    '''Extracts event date from article'''
    tag = article.find('h5', {"class": "card__date"})
    date = tag.text
    event_date = dateparser.parse(
                    date.split('(')[0].strip(),
                    date_formats=['%d %B %Y'])
    return event_date


def get_event_title(article):
    '''Extracts event title from article'''
    tag = article.find('h5', {"class": "card__title"})
    title = tag.text
    event_title = title.strip()
    return event_title


def get_article_date(article):
    '''Extracts the post date of an event'''
    tag = article.find('p', {'class': 'added-date'})
    date = tag.text
    post_date = dateparser.parse(
                    date.split('  ')[1].strip(),
                    date_formats=['%d %B %Y'])
    return post_date


def get_event_votes(article):
    '''Extracts the number of votes for an event'''
    try:
        tag = article.find('div', {"class": "progress__votes"})
        votes = tag.text
        event_votes = int(votes.split(' ')[0])
    except ValueError:
        event_votes = None
    return event_votes


def get_event_confidence(article):
    '''Extracts the percentage of confidence for a given event'''
    try:
        tag = article.find('div', {"class": "progress-bar"})
        event_confidence = round(float(tag.get('aria-valuenow').strip()), 2)
    except ValueError:
        event_confidence = None
    return event_confidence


def get_event_info(article):
    '''Extracts all event info from an article into a list'''
    event = {'coin': get_event_coin(article), 
             'eventDate': get_event_date(article), 
             'eventTitle': get_event_title(article), 
             'postDate': get_article_date(article),
             'votes': get_event_votes(article),
             'confidence': get_event_confidence(article)
            }
    return event


def get_events(date_from, date_to):
    '''Extracts parts of the HTML page containing main information about events
        between <date_from> and <date_to>
    '''
    events = []
    page = 1
    ua = UserAgent()
    pbar = tqdm(total=30) # change to an undefined progress bar
    while True:
        url = f"https://coinmarketcal.com/en/?form%5Bdate_range%5D={date_from}%20-%20{date_to}&form%5B\
                keyword%5D=&form%5Bsort_by%5D=&form%5Bsubmit%5D=&form%5Bshow_reset%5D=&page={page}"
        headers = {'User-Agent': ua.random}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        articles = soup.find_all('article')
        if articles:
            events.extend([get_event_info(article) for article in articles])
            page += 1
            pbar.update(1)
        else:
            pbar.close()
            break
    return events


def get_events_table(date_from, date_to):
    events = get_events(date_from, date_to)
    df = pd.DataFrame(events)
    # create a unique event id per event
    df = df.dropna(subset=['coin', 'eventDate', 'eventTitle', 'postDate'])
    df['eventId'] = df['coin'].map(str) + df['eventDate'].map(str) + df['eventTitle'].map(str) + df['postDate'].map(str)
    df['eventId'] = pd.util.hash_pandas_object(df['eventId'], index=False)
    df = df.drop_duplicates(subset=['eventId'])
    return df


if __name__ == '__main__':

    n_days = 30 # parse events in the upcoming 30 days
    date_from = datetime.now().strftime('%d/%m/%Y')
    date_to = (datetime.now() + timedelta(days=n_days)).strftime('%d/%m/%Y')

    events = get_events_table(date_from, date_to)
    print(events)
