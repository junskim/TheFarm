
import pandas as pd
import numpy as np


def split_data(path):
    df = pd.read_csv(path + '/cleaned_data_ver2.csv')
    df = df.drop('Unnamed: 0', axis=1)

    df.ERA = df['ERA'].apply(lambda x: 999.99 if x == np.inf else x)
    df.RAvg = df.RAvg.apply(lambda x: 999.99 if x == np.inf else x)

    for i, v in enumerate(list(df.columns)):
        if v == 'Age_batting':
            print 'batting starts at: ' + str(i)
            bat_start = i
        if v == 'Lev':
            print 'pitching stats at: ' + str(i)
            bat_start_2 = i
        if v == 'Age_pitching':
            print 'pitching stats at: ' + str(i)
            pit_start = i
        if v == 'Fielding_position':
            print 'fielding starts at: ' + str(i)
            fiel_start = i

    pit_columns = df.columns - df.columns[bat_start:bat_start_2]\
        - df.columns[bat_start_2+1:pit_start]
    bat_columns = df.columns - df.columns[pit_start:fiel_start]

    pit = df[df['Pitcher'] == 1][pit_columns]
    bat = df[df['Pitcher'] == 0][bat_columns]

    bat.to_csv(path + '/batters_cleaned.csv')
    pit.to_csv(path + '/pitchers_cleaned.csv')
