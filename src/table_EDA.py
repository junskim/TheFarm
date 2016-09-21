"""table_EDA script imported from a Jupyter Notebook

This script imports batting/picthing/fielding/bio/id tables
prepared from prepare_table.py, does basic cleaning of each table,
then merge the tables together.

"""

import pandas as pd
import numpy as np
import string
from itertools import izip
printable = set(string.printable)

class clean_data(object):
    """
    INPUT
    ------
    path: path to separate stat tables

    (clean_batting, clean_pitching, clean_fielding) -
    """
    def __init__(self, path):
        self.path = path
        self.players_batting = pd.read_csv(path + '/batting.csv')
        self.players_pitching = pd.read_csv(path + '/pitching.csv')
        self.players_fielding = pd.read_csv(path + '/fielding.csv')
        self.players_bio = pd.read_csv(path + '/bio.csv')
        self.players_id = pd.read_csv(path + '/id.csv')
        self.players_bio = self.players_bio.drop('index', axis=1)
        self.players_id = self.players_id.drop('index', axis=1)
        self.rookies = pd.read_csv(path + '/rookies.csv')
        self.players = None

        # making a list of players who have '--' as their age
        drop_id = set()
        for df in [self.players_fielding, self.players_batting,
                   self.players_pitching]:
            for id in df[df.Age == '--'].player_id.unique():
                drop_id.add(id)
        self.drop_id_lst = list(drop_id)

    def clean_batting(self):
        """
        Does basic cleaning of batting table
        """
        players_batting = self.players_batting.drop('index', axis=1)
        players_batting = players_batting[players_batting['OPS'] != 'OPS']
        players_batting.Tm = players_batting.Tm.apply(
            lambda x: filter(lambda y: y in printable, x))
        # dropping rows that has 'Teams' in Teams column
        players_batting.Tm = players_batting['Tm'].apply(
            lambda x: 'toss_away' if 'Teams' in x else x)
        players_batting = players_batting[players_batting.Tm != 'toss_away']

        # fill missing Aff with N/A
        players_batting.Aff = players_batting.Aff.fillna('N/A')
        # dropping rows with missing AgeDif
        players_batting = players_batting[players_batting.AgeDif.notnull()]
        # fill the rest of missing values with 0
        players_batting = players_batting.fillna(0)

        # dropping players whose age is '--'
        for id in self.drop_id_lst:
            players_batting = players_batting[players_batting['player_id'] != id]

        players_batting[['Age', 'AgeDif']] =\
            players_batting[['Age', 'AgeDif']].apply(lambda x: pd.to_numeric(x))
        players_batting[players_batting.columns[8:]] =\
            players_batting[players_batting.columns[8:]].apply(
                lambda x: pd.to_numeric(x))


    def clean_pitching(self):
        """
        Does basic cleaning of picthing table
        """
        players_pitching = self.players_pitching.drop('index', axis=1)
        players_pitching = players_pitching[players_pitching.HR != 'HR']
        players_pitching.Tm = players_pitching.Tm.apply(
            lambda x: filter(lambda y: y in printable, x))
        # dropping rows that has 'Teams' in Teams column
        players_pitching.Tm = players_pitching['Tm'].apply(
            lambda x: 'toss_away' if 'Teams' in x else x)
        players_pitching = players_pitching[players_pitching.Tm != 'toss_away']

        # dropping W-L perc as it is largely correlated
        players_pitching = players_pitching.drop('W-L_perc', axis=1)
        # fill missing Aff with N/A
        players_pitching.Aff = players_pitching.Aff.fillna('N/A')
        # dropping rows with missing AgeDif
        players_pitching = players_pitching[players_pitching.AgeDif.notnull()]
        # fill the rest of missing values with 0
        players_pitching = players_pitching.fillna(0)

        # dropping players whose age is '--'
        for id in self.drop_id_lst:
            players_pitching = players_pitching[players_pitching[
                'player_id'] != id]

        players_pitching[['Age', 'AgeDif']] = players_pitching[
            ['Age', 'AgeDif']].apply(lambda x: pd.to_numeric(x))
        players_pitching[players_pitching.columns[8:]] =\
            players_pitching[players_pitching.columns[8:]].apply(
                lambda x: pd.to_numeric(x))

    def clean_fielding(self):
        players_fielding = self.players_fielding.drop('index', axis=1)
        players_fielding = players_fielding[players_fielding['DP'] != 'DP']
        players_fielding.Tm = players_fielding.Tm.apply(
            lambda x: filter(lambda y: y in printable, x))
        players_fielding.Tm = players_fielding['Tm'].apply(
            lambda x: 'toss_away' if 'Teams' in x else x)
        players_fielding = players_fielding[players_fielding.Tm != 'toss_away']

        # foreign / ind leagues have no aff. fill with N/A
        players_fielding.Aff = players_fielding.Aff.fillna('N/A')
        # dropping 'CG' which has nothing in
        players_fielding = players_fielding.drop(
            ['CG', 'WP', 'PO', 'lgCS_perc', 'PB', 'GS', 'Inn', 'RF/9'], axis=1)

        # Had to drop GS, Inn, and RF/9 because a lot of lower leagues
        # have them blank. I have to rely on fielding% and RF/G, G, and Ch.

        # fill the rest of missing values with 0
        players_fielding = players_fielding.fillna(0)
        players_fielding.Something = players_fielding.Something.apply(
            lambda x: 'N/A' if x == 0 else x)
        players_fielding.Something = players_fielding.Something.apply(
            lambda x: 'C' if x == 'c' else x)
        players_fielding.CS_perc = players_fielding.CS_perc.apply(
            lambda x: str(x))
        players_fielding.CS_perc = players_fielding.CS_perc.apply(
            lambda x: x.replace('%', ''))
        players_fielding = players_fielding.rename(
            columns={'Something': 'Fielding_position'})
        players_fielding[players_fielding.columns[8:]] =\
            players_fielding[players_fielding.columns[8:]].apply(
                lambda x: pd.to_numeric(x))

        # this person has '--' as age
        for id in self.drop_id_lst:
            players_fielding =\
                players_fielding[players_fielding['player_id'] != id]
        players_fielding['Age'] = players_fielding['Age'].apply(
            lambda x: pd.to_numeric(x))

        # duplicated ones
        players_fielding[players_fielding.duplicated([
            'player_id', 'Year', 'Lev'], keep=False) == True].ix[267264:267268]

        dup_index_sets = players_fielding[players_fielding.duplicated(
            ['player_id', 'Year', 'Tm', 'Lev'], keep=False) == True].groupby(
                ['player_id', 'Year', 'Lev']).groups.values()

        # The function below will clean the fielding data
        for ix_set in xrange(len(dup_index_sets)):
            try:
                dup_position = players_fielding.ix[dup_index_sets[ix_set]][
                    'Fielding_position']

                if 'OF' in list(dup_position):
                    filtered_dup_ix = dup_position[(
                        dup_position != 'LF') & (dup_position != 'RF') & (
                            dup_position != 'CF') & (dup_position != 'DH') & (
                                dup_position != 'P')].index
                else:
                    filtered_dup_ix = dup_position[(dup_position != 'DH')].index

                summed_field = list(players_fielding.ix[filtered_dup_ix][[
                        'G', 'Ch', 'A', 'E', 'DP', 'SB', 'CS']].sum())
                avg_field = list(players_fielding.ix[filtered_dup_ix][[
                    'Fld_perc', 'RF/G', 'CS_perc']].mean())
                concat_position = list(
                    players_fielding.ix[filtered_dup_ix].Fielding_position)
                players_fielding = players_fielding.set_value(
                    dup_index_sets[ix_set][0], [
                        'G', 'Ch', 'A', 'E', 'DP', 'SB', 'CS'], summed_field)
                players_fielding = players_fielding.set_value(
                    dup_index_sets[ix_set][0], [
                        'Fld_perc', 'RF/G', 'CS_perc'], avg_field)
                players_fielding = players_fielding.set_value(
                    dup_index_sets[
                        ix_set][0], 'Fielding_position', concat_position)

            except IndexError:
                print ix_set

        players_fielding = players_fielding.drop_duplicates(
            ['player_id', 'Year', 'Tm', 'Lev'])

    def merge_id_bio(self):
        players = pd.merge(self.players_id, self.players_bio, how='inner',
                           left_on='player_id', right_on='player_id',
                           suffixes=('_id', '_bio'))
        # Making dummy variables for players bio
        players.Drafted = players.Drafted.apply(
            lambda x: 0 if x == 'N/A' else x)
        players.Position = players.Position.apply(lambda x: x.replace('{', ''))
        players.Position = players.Position.apply(lambda x: x.replace('}', ''))
        players.Position = players.Position.apply(
            lambda x: x.replace(',Baseman', ''))
        players.Position = players.Position.apply(lambda x: x.split(','))
        df_dummies = pd.DataFrame(list(players['Position'].apply(
            self._list_to_dict).values)).fillna(0)
        players = players.join(df_dummies)

        players = players.drop('Position', axis=1)

        players = players.drop('Birth_year', axis=1)

        players.Bats.unique()

        players['Bats'] = players['Bats'].apply(lambda x: x.replace('{', ''))
        players['Bats'] = players['Bats'].apply(lambda x: x.replace('}', ''))
        players['Throws'] = players['Throws'].apply(lambda x: x.replace('{', ''))
        players['Throws'] = players['Throws'].apply(lambda x: x.replace('}', ''))

        players['Bats'] = players['Bats'].apply(
            lambda x: 'Unknown' if x == 'N/A' else x)
        players['Throws'] = players['Throws'].apply(
            lambda x: 'Unknown' if x == 'N/A' else x)

        players[['Bats_both', 'Bats_left', 'Bats_Right', 'Bats_unknown']] =\
            pd.get_dummies(players['Bats'])
        players[['Throws_left', 'Throws_right', 'Throws_unknown']] =\
            pd.get_dummies(players['Throws'])
        players = players.drop('Throws', axis=1)
        players = players.drop('Bats', axis=1)
        players = players.drop('Position', axis=1)
        players = players.drop('Birth_year', axis=1)

        # this person has '--' as age
        for id in self.drop_id_lst:
            players = players[players['player_id'] != id]
        self.players = players

    def _list_to_dict(self, category_list):
        n_categories = len(category_list)
        return dict(zip(category_list, [1]*n_categories))

    def merge_(self):
        self.players = pd.merge(self.players, self.players_batting,
                                how='left', on = 'player_id')

        self.players =\
            self.players.drop_duplicates(
                ['player_id', 'Year', 'Name', 'Tm', 'Lev', 'AB'])

        self.players =\
            self.players.merge(self.players_pitching, how='left',
                               on=['player_id', 'Year', 'Tm', 'Lev'],
                               suffixes=['_batting', '_pitching'])

        self.players =\
            self.players.drop_duplicates(
                ['player_id', 'Year', 'Name', 'Tm', 'Lev', 'IP'])

        self.players_fielding2 =\
            self.players_fielding.drop(['Age', 'Lg', 'Aff'], axis=1)

        self.players =\
            self.players.merge(
                self.players_fielding2, how='left',
                on=['player_id', 'Year', 'Tm', 'Lev'],
                suffixes=['_batting', '_fielding'])

        self.players =\
            self.players.drop_duplicates(
                ['player_id', 'Year', 'Name', 'Tm', 'Lev', 'AB'])

        self.players = self.players[self.players['Year'].notnull()]

    def add_label(self):
        rookies = self.rookies.drop('Unnamed: 0', axis=1)
        rookies = rookies.drop('Unnamed: 2', axis=1)
        rookies = rookies.drop('Rk', axis=1)

        self.players.insert(0, 'Rookie?', 0)
        self.players.index = range(self.players.shape[0])
        self.players['Year'][0]
        NameYear = izip(self.players['Name'], self.players['Year'])
        R_nameYear = izip(rookies['Name'], rookies['Year'])
        R_lst = []
        for name, year in R_nameYear:
            R_lst.append([name, year])

        ix = 0
        d = {}
        for name, year in NameYear:
            if [name, str(int(year)+1)] in R_lst:
                d[ix] = [name, year]
            ix += 1

        for val in d.keys():
            self.players.set_value(val, 'Rookie?', 1)

    def export_cleaned_data(self):
        self.players.to_csv(self.path + '/cleaned_data_ver2.csv')

    def split_data(self):
        self.players.ERA = self.players['ERA'].apply(
            lambda x: 999.99 if x == np.inf else x)
        self.players.RAvg = self.players.RAvg.apply(
            lambda x: 999.99 if x == np.inf else x)

        for i, v in enumerate(list(self.players.columns)):
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

        pit_columns = self.players.columns\
            - self.players.columns[bat_start:bat_start_2]\
            - self.players.columns[bat_start_2+1:pit_start]
        bat_columns = self.players.columns\
            - self.players.columns[pit_start:fiel_start]

        pit = self.players[self.players['Pitcher'] == 1][pit_columns]
        bat = self.players[self.players['Pitcher'] == 0][bat_columns]

        bat.to_csv(self.path + '/batters_cleaned.csv')
        pit.to_csv(self.path + '/pitchers_cleaned.csv')
