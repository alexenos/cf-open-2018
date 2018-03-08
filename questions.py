#! /usr/bin/env python3

"""

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as mp
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression
from scipy.interpolate import griddata

import athlete as ath

div = 'M'
reg = 'WorldWide'
team = 5071
athl = "Dax"


def main():
    df = pd.read_csv("Results_{}_{}_Post18-2.csv".format(div, reg))
    #print(df)

    #df = df[df["affiliateId"] == team]
    #df = df[df["firstName"] == ath]
    #df.plot.scatter('scoreDisplay_E1', 'rank_E1')
    #df.plot.scatter('age', 'scoreDisplay_E1')
    #df.plot.scatter('height', 'scoreDisplay_E1')
    #df.plot.scatter('weight', 'scoreDisplay_E1')

    #age(df)
    #cj(df)
    sweet_spot(df)

    mp.show()
    return 0

def sweet_spot(df):
    # Drop scaled scores
    df = df[df['scaled_E2'] == 0]
    df = df[df['scaled_E3'] == 0]
    # Get and clean relevant data
    df = df[['competitorName', 'time_E2', 'breakdown_E3', 'rank_E2', 'rank_E3']].dropna()
    df['time_E2'] = df['time_E2'].apply(pd.to_numeric, errors='coerce')
    df['breakdown_E3'] = df['breakdown_E3'].apply(lambda r: convert(r))
    df['score_E2E3'] = df[['rank_E2', 'rank_E3']].sum(axis=1)
    # Rank 18.2[a] together
    df.sort_values("score_E2E3", inplace=True) # Min score is highest rank
    df.loc[:, 'rank_E2E3'] = df['score_E2E3'].rank(method='min')
    df.sort_values("rank_E2E3", inplace=True)
    df.reset_index(inplace=True)
    df = df.iloc[0:360]
    top = df[df['rank_E2E3'] == 1]
    #print(df.head())
    print(top)

    #df.plot.scatter('time_E2', 'rank_E2E3')
    #df.plot.scatter('breakdown_E3', 'rank_E2E3')

    x1 = np.linspace(df['breakdown_E3'].min(),df['breakdown_E3'].max(), df['breakdown_E3'].max()-df['breakdown_E3'].min())
    y1 = np.linspace(df['time_E2'].min(),df['time_E2'].max(), df['time_E2'].max()-df['time_E2'].min())
    x2, y2 = np.meshgrid(x1, y1)
    z2 = griddata((df['breakdown_E3'], df['time_E2']), df['rank_E2E3'], (x2, y2), method='cubic')
    f = mp.figure()
    ax = f.gca()#projection='3d')
    #surf = ax.plot_surface(x2, y2 ,z2, cmap=cm.coolwarm, antialiased=False)
    #surf = ax.contourf(x2, y2 ,z2, cmap=cm.coolwarm, antialiased=False, vmin=0)
    surf = ax.pcolor(x2, y2 ,z2, cmap=cm.rainbow, antialiased=False, vmin=0)
    mp.plot(top['breakdown_E3'], top['time_E2'],  'k*')
    cb = f.colorbar(surf, aspect=5)
    cb.set_label('Combined Rank for 18.2 and 18.2a')
    ax.set_xlabel('18.2a Weight (lbs)')
    ax.set_ylabel('18.2 Time (s)')
    mp.title("Crossfit Open 18.2/2a Sweet Spot: Men Rx World Wide")

    return

def convert(r):
    cm2in = 0.393701
    kg2lb = 2.20462
    #print(r)
    v = r.split()
    if len(v) == 2:
        if v[1] in ['in', 'lb', 'lb.']:
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

def cj(df):
    df = df[df["affiliateId"] == team]
    #print(df.head())
    df = ath.scrape_all_stats(df)
    print(df.head())

def age(df):
    # Drop scaled scores
    df = df[df['scaled_E1'] == 0]
    # Get relevant data
    df = df[['age', 'scoreDisplay_E1']].dropna()
    age_groups = df.groupby('age')#['scoreDisplay_E1'].median()
    medians = age_groups['scoreDisplay_E1'].median()
    #print(medians)
    #print(medians.values)
    #print(medians.index[14:].values)
    y = medians[14:].values.reshape(-1, 1)
    x = medians.index[14:].values.reshape(-1, 1)
    lr = LinearRegression().fit(x, y)
    print(lr.coef_)

    ag_top = df.groupby(['age'])['scoreDisplay_E1'].nlargest(20)
    #ag_top = df.groupby(["age"]).apply(lambda x: x.sort_values(['scoreDisplay_E1'],ascending=False)).reset_index(drop=True)
    df_top = pd.DataFrame(ag_top)
    print(ag_top)

    #ax = df.boxplot(column='scoreDisplay_E1', by='age', showfliers=False, whis=[5, 95])
    ax = df_top.boxplot(column='scoreDisplay_E1', by='age', showfliers=True, whis=[5, 95])
    ax.grid(axis='x')
    mp.title('Crossfit Open 18.1 Performance vs Age: Top 20 Women Rx')
    mp.suptitle("")
    mp.xlabel('Age')
    mp.ylabel('Score')

if __name__ == '__main__':
    main()
