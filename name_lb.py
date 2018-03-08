#! /usr/bin/env python3

"""

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as mp
from sklearn.linear_model import LinearRegression
import argparse

def main():
    args = parse_args()

    name = args.name.split()
    first_name = name[0]

    df = pd.read_csv("Results_{}_{}_Post18-2.csv".format(args.div, args.reg))
    df = df.drop_duplicates('competitorId', keep='last')
    df = df[df["firstName"].str.contains(first_name)]
    df = df[["competitorName", "overallRank"]]
    df.sort_values("overallRank", inplace=True) # Min score is highest rank
    df.loc[:, 'name_rank'] = df['overallRank'].rank(method='min')
    df.sort_values("name_rank", inplace=True)
    df.reset_index(inplace=True)
    print(df[df['competitorName'] == args.name])
    df.to_csv('{}_LB.csv'.format(first_name))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--div', default="M", help="Division")
    parser.add_argument('-r', '--reg', default="WorldWide", help="Region")
    parser.add_argument('-n', '--name', default="Dax Garner", help="Name to create leaderboard")
    #parser.add_argument('', '', help="")
    return parser.parse_args()

if __name__ == '__main__':
    main()
