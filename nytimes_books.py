import configparser
import requests
import json
import os
import pandas as pd
from datetime import date
from time import sleep

config = configparser.ConfigParser()
config.read('api_keys.ini')

base_url = 'https://api.nytimes.com/svc/books/v3'


def book_lists():
    lists = '/lists/names.json'
    nyt_response = requests.get(base_url + lists, params={'api-key': config.get('NYTimes', 'key')})
    nyt_data = json.loads(nyt_response.text)
    with open('NYTimes Book Categories.txt', 'w') as f:
        for category in [ln['list_name'] for ln in nyt_data['results']]:
            f.write(category + '\n')


def bestseller_list(book_list: str, as_of_date: str = 'current'):
    url = base_url + f"/lists/{as_of_date}/{book_list}.json"
    nyt_response = requests.get(url, params={'api-key': config.get('NYTimes', 'key')})
    nyt_data = json.loads(nyt_response.text)
    with open(os.path.join('Book Data', f"{book_list}.json"), 'w') as f:
        json.dump(nyt_data, f)
    try:
        df = pd.json_normalize(nyt_data['results']['books'])
        df.to_csv(os.path.join('Book Data', f"{book_list}.csv"))
    except Exception as e:
        print(e)
        print(nyt_data.get('fault').get('faultstring'))
    # API rate limit is 10 requests per minute
    sleep(6)


def main():
    book_lists()
    with open('NYTimes Book Categories.txt') as f:
        book_categories = f.read().split('\n')
    for bl in book_categories:
        bestseller_list(bl)


if __name__ == '__main__':
    main()
