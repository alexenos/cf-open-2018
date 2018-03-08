#! /usr/bin/env python3

"""
Scrapes lots of data directly from the 2018 Crossfit Open leaderboard
"""

import re
import requests
import pandas as pd
import numpy as np
import argparse

import athlete as ath

# Getting raw Crossfit Leaderboard data
def get_url(division=1, region=0, page=1):
    return "https://games.crossfit.com/competitions/api/v1/competitions/open/2018/leaderboards" +\
           "?competition=1&year=2018&division={}&region={}&scaled=0&sort=0&page={}"\
           .format(division, region, page)

dmap = {"M": 1,
        "W": 2}
rmap = {"WorldWide": 0,
        "SouthCentral": 14}

#div = "W"
#reg = "WorldWide"

def main():
    """ Top-level """
    args = parse_args()
    df = scrape(args.div, args.reg)
    df = clean(df)
    if args.ben:
        print("Scraping individual athlete benchmark stats... this takes a long time...")
        df = ath.scrape_all_stats(df)
    #print(df.head())
    print("Output to csv...")
    df.to_csv("Results_{}_{}.csv".format(args.div, args.reg))
    return 0

def clean(df):
    """ Expands columns and removes extraneous data """
    print("Start cleaning data...")

    # Drop two top-level columns
    df = df.drop(['ui', 'nextStage'], axis=1)

    # Expand entrant column
    #print(df['entrant'].apply(pd.Series).head())
    df = pd.concat([df.drop(['entrant'], axis=1), df['entrant'].apply(pd.Series)], axis=1)
    # Drop entrant columns that aren't useful
    df = df.drop(['bibId', 'profilePicS3key'], axis=1)
    # Convert to numeric
    to_num = ['competitorId', 'regionalCode', 'regionId', 'divisionId', 'profession', 'affiliateId', 'age']
    df[to_num] = df[to_num].apply(pd.to_numeric, errors='coerce', axis=1)
    # Height and Weight
    df['height'] = df['height'].apply(lambda r: convert(r))
    df['weight'] = df['weight'].apply(lambda r: convert(r))

    # Expand scores column
    print("Cleaning score data...")
    num_ev = len(df['scores'].iloc[0])
    evs = df['scores'].apply(pd.Series)
    for i in range(num_ev):
        ev = evs[i].apply(pd.Series)
        # Drop some columns
        ev = ev.drop(['mobileScoreDisplay', 'scoreIdentifier', 'heat', 'lane'], axis=1)
        # Remove extras
        ev['scoreDisplay'] = ev['scoreDisplay'].apply(lambda r: re.sub('[^0-9]','', r))
        # Convert to numeric
        to_num = ['ordinal', 'rank', 'score', 'scoreDisplay']
        ev[to_num] = ev[to_num].apply(pd.to_numeric, errors='coerce', axis=1)
        # Make columns unique
        ev = ev.add_suffix('_E{}'.format(i+1))
        df = pd.concat([df, ev], axis=1)
    df = df.drop(['scores'], axis=1)

    # Drop duplicates
    df = df.drop_duplicates('competitorId', keep='last')

    #print(df.head())
    return df

def convert(r):
    cm2in = 0.393701
    kg2lb = 2.20462
    #print(r)
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

def scrape(div, reg, mp=0):
    """ Very raw scrape of the leaderboard """
    raw_lb = requests.get(get_url(dmap[div], rmap[reg]))
    #print("Top-level keys: {}".format(raw_lb.json().keys()))

    # Need to get all pages
    tp = raw_lb.json()["pagination"]['totalPages']
    mp = tp if (mp == 0 or mp > tp) else mp
    print("Number of pages: {}".format(mp))

    # Last place
    raw_lb = requests.get(get_url(dmap[div], rmap[reg], mp))
    page = pd.DataFrame(raw_lb.json()['leaderboardRows'])
    lp = page["overallRank"].iloc[0]
    print("Last place is currently: {}".format(lp))

    # Create big dataframe from all pages
    df = pd.DataFrame()
    no_ath = []
    for i in range(1, mp + 1):
        raw_lb = requests.get(get_url(dmap[div], rmap[reg], i))
        try:
            page = pd.DataFrame(raw_lb.json()['leaderboardRows'])
        except:
            print("Attempted page {}".format(i))
            #print("Top-level keys: {}".format(raw_lb.json().keys()))
        #print("Total Number of Athletes on page {}: {}".format(i, len(page.index)))
        # Only append if there is data on page and
        # only continue until reach last place
        if len(page.index) > 0:
            #print(page["overallRank"].iloc[0], page["overallRank"].iloc[-1])
            df = df.append(page)
            if page["overallRank"].iloc[0] == lp:
                print("Last page processed due to last place: {}".format(i))
                break
        else:
            no_ath.append(i)
        if i % 100 == 0:
            print("Processed {} pages...".format(i))
    #print("Number of pages have no data: {}".format(len(no_ath)))
    print("Total Number of Athletes: {}".format(len(df.index)))
    return df

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--div', default="M", help="Division")
    parser.add_argument('-r', '--reg', default="WorldWide", help="Region")
    parser.add_argument('-n', '--num', default=0, type=int, help="Number of pages, each page has 50 athletes")
    parser.add_argument('-b', '--ben', default=False, action="store_true", help="Scrape athlete benchmark stats")
    #parser.add_argument('', '', help="")
    return parser.parse_args()

if __name__ == "__main__":
    main()
