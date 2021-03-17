import requests
import os
import configparser
import pandas as pd
from datetime import date
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# https://www.alphavantage.co/documentation/

config = configparser.ConfigParser()
config.read('api_keys.ini')
av_key = config.get('AlphaVantage', 'key')
base_url = 'https://www.alphavantage.co/query'
date_stamp = date.today().strftime('%Y-%m-%d')
results_folder = os.path.join(os.getcwd(), 'Alpha Vantage')
if not os.path.exists(results_folder):
    os.mkdir(results_folder)


def ipo_calendar(save_source_data: bool = False):
    parameters = {'function': 'IPO_CALENDAR',
                  'apikey': av_key}
    r = requests.get(base_url, params=parameters, verify=False)
    if save_source_data:
        with open(os.path.join(results_folder, f"IPO Calendar {date_stamp}.csv"), 'w', newline='') as f:
            f.write(r.text)
    cal = [[cell.replace('\r', '') for cell in row.split(',')] for row in r.text.split('\n')]
    df = pd.DataFrame(cal)
    df.columns = df.loc[0]
    df = df.drop(0).reset_index(drop=True)
    df = df.dropna()
    df.loc[df['name'].str.contains(r' Warrant'), 'assetType'] = 'Warrants'
    df.loc[df['name'].str.contains(r' Right'), 'assetType'] = 'Rights'
    df.loc[df['name'].str.contains(r' Unit'), 'assetType'] = 'Units'
    df.loc[df['assetType'].isna(), 'assetType'] = 'Shares'
    df.to_csv(os.path.join(results_folder, f"IPO Calendar {date_stamp}.csv"), index=False)
    return df


def listings(save_source_data: bool = False):
    parameters = {'function': 'LISTING_STATUS',
                  'apikey': av_key}
    r = requests.get(base_url, params=parameters, verify=False)
    if save_source_data:
        with open(os.path.join(results_folder, f"IPO Calendar {date_stamp}.csv"), 'w', newline='') as f:
            f.write(r.text)
    all_listings = [[cell.replace('\r', '') for cell in row.split(',')] for row in r.text.split('\n')]
    df = pd.DataFrame(all_listings)
    df.columns = df.loc[0]
    df = df.drop(0).reset_index(drop=True)
    df.dropna(inplace=True)
    df.sort_values(by='ipoDate', inplace=True, ascending=False)
    df.reset_index(drop=True, inplace=True)
    df.loc[(df['assetType'] == 'Stock') & (df['name'].str.contains(r' Warrant')), 'assetType'] = 'Warrants'
    df.loc[(df['assetType'] == 'Stock') & (df['name'].str.contains(r' - Unit')), 'assetType'] = 'Units'
    df['securityDescription'] = df['name'].str.extract(r'\s-\s([\w\W]*)$')
    df['companyName'] = df['name'].str.extract(r'^([\w\W]*)\s-\s')
    df.loc[df['companyName'].isna(), 'companyName'] = df['name']
    df['details'] = df['securityDescription'].str.extract(r'\((.*)\)')
    df.loc[df['assetType'] == 'Units', 'unitConstituents'] = df['details']
    df.loc[df['assetType'] == 'Warrants', 'warrantExpiration'] = df['details']
    df['warrantExpiration'] = pd.to_datetime(df['warrantExpiration'], errors='coerce').dt.date
    df.rename(columns={'ipoDate': 'listingDate'}, inplace=True)
    cols = ['name', 'companyName', 'exchange', 'symbol', 'assetType', 'securityDescription', 'unitConstituents',
            'warrantExpiration', 'listingDate', 'delistingDate', 'status']
    df = df[cols]
    df.to_csv(os.path.join(results_folder, f"All Listings {date_stamp}.csv"), index=False)
    return df


if __name__ == '__main__':
    df_ipo = ipo_calendar()
    df_listings = listings()
