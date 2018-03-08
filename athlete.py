#! /usr/bin/env python3

"""

"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import timedelta

def get_url(athlete):
    "Athlete profile URL"
    return "https://games.crossfit.com/athlete/{}".format(athlete)

ath = 703699

def main():
    df = scrape_stats(ath)

def scrape_all_stats(df):
    df['bench'] = df.apply(lambda r: scrape_ath_stats(r['competitorId']), axis=1)
    df = pd.concat([df.drop(['bench'], axis=1), df['bench'].apply(pd.Series)], axis=1)
    df = df.replace('--', np.nan)
    tonum = ['Max Pull-ups', 'Fight Gone Bad']
    totime = ['Fran', 'Grace', 'Helen', 'Filthy 50', 'Sprint 400m', 'Run 5k']
    tolbs = ['Back Squat', 'Clean and Jerk', 'Snatch', 'Deadlift']
    df[tonum] = df[tonum].apply(pd.to_numeric, errors='coerce', axis=1)
    df[totime] = df[totime].apply(pd.to_datetime, box=False, format='%M:%S', errors='coerce', axis=1)
    #df[totime] = df[totime].apply(pd.to_timedelta, errors='coerce', axis=1)
    #for c in totime:
    #    df[c] = df[c].apply(lambda r: to_secs(r))
    for c in tolbs:
        df[c] = df[c].apply(lambda r: convert(r))
    return df

def to_secs(t):
    print(type(t))
    if np.isnat(t):
        return t
    d = timedelta(minutes=t.minute, seconds=t.second)
    return d.total_seconds()

def convert(r):
    cm2in = 0.393701
    kg2lb = 2.20462
    #print(r)
    if type(r) == float:
        return r
    v = r.split()
    if len(v) == 2:
        if v[1] in ['in', 'lb']:
            return float(v[0])
        elif v[1] == 'cm':
            return float(v[0])*cm2in
        elif v[1] == 'kg':
            return float(v[0])*kg2lb
        else:
            print('Unknown unit: {}'.format(v[1]))
            return np.nan
    else:
        return np.nan

def scrape_ath_stats(athlete):
    response = requests.get(get_url(athlete))
    soup = BeautifulSoup(response.text, 'lxml')
    return parse_stats(soup.find_all('table')[-4:])

def parse_stats(tables):
    #print(tables)
    dct = {}
    for t in tables:
        for r in t.find_all('tr'):
            #print(r)
            for c, d in zip(r.find_all('th'), r.find_all('td')):
                #print(c)
                #print(d)
                dct[c.get_text().strip()] = d.get_text().strip()
    #print(dct)
    return dct


def parse_prev(table):
    pass

if __name__ == '__main__':
    main()
