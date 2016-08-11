"""This file takes MongoDB data consisting of raw html and turn into tables."""

import pandas as pd
from pymongo import MongoClient
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import numpy as np
from sqlalchemy import create_engine
from itertools import izip


def get_tables(player_id, player):
    """Calls get_bio, get_batting, get_pitching, and get_fielding functions.

    INPUT
    ------
    player_id : int, unique id assigned to each player

    player : html string, raw html of a player stats page

    OUTPUT
    ------
    data : dict, containing id, bio, batting, pitching, and fielding
           list arrays
    """
    data = defaultdict(list)
    profiles = BeautifulSoup(player['html'], 'html.parser')
    name = profiles.select(
        'div#page_content #info_box div span#player_name')[0].text

    print player_id, name
    # texts in the bio section
    table_stuffs = re.split(', |\n', '\n'.join([
        s.text for s in profiles.select('div#info_box p')]))
    data['id'].append([player_id, name])
    data['bio'].append(get_bio(table_stuffs, player_id))
    data['batting'].extend(get_batting(profiles, player_id))
    data['pitching'].extend(get_pitching(profiles, player_id))
    data['fielding'].extend(get_fielding(profiles, player_id))

    return data


def get_bio(table_stuffs, player_id):
    '''
    INPUT
    ------
    table_stuffs : list array, consisting of texts in info table

    player_id : int, unique id assigned to each player

    OUTPUT
    ------
    bio : list array, containing the player's basic info
        - Position : player's position
        - Bats : bats right? left? both?
        - Throws : throws right? left? or even both?
        - Born : birth year
        - Height : height in feet and inches
        - Weight : weight in lbs
        - Drafted : which round was the player drafted
    '''
    for ix, i in enumerate(table_stuffs):
        if 'Position' in i:
            Position = re.split(', | and | ', i)[1:]
        if 'Bats' in i:
            Bats = re.split(', | and | ', i)[1:]
        if 'Throws' in i:
            Throws = re.split(', | and | ', i)[1:]
        if 'Born' in i:
            Birth_year = re.split(', | and | ', table_stuffs[ix+1])[0]
        if i.split(': ')[0] == 'Height':
            Height = i.split(': ')[1]
        if 'Weight' in i:
            Weight = i.split()[1]
        if 'Weight' in i:
            Weight = i.split()[1]
        if 'round' in i:
            Drafted = re.split('the | round', i)[2]
            Drafted = re.search(r'\d+', Drafted).group()  # takes only int
    if 'Drafted' in locals():
        pass
    else:
        Drafted = 0
    result = ['player_id', 'Position', 'Birth_year', 'Height',
              'Weight', 'Bats', 'Throws', 'Drafted']
    for ix, item in enumerate(result):
        if item not in locals():
            return [player_id, np.nan, np.nan, np.nan,
                    np.nan, np.nan, np.nan, np.nan]
    bio = [player_id, Position, Birth_year, Height, Weight, Bats, Throws,
           Drafted]
    return bio


def get_pitching(profiles, player_id):
    '''
    INPUT
    ------
    profiles : bs4 soup object, containing player page html

    player_id : int, unique id assigned to each player

    OUTPUT
    ------
    pitching_stats : list array, containing player's pitching stats if exists
    '''
    # stats under pitching table! filtered out the empty line (grey line)
    pitching_stats = [row.text.split('\n')[1:-1] for row in profiles.select(
                      'table#standard_pitching tbody tr')
                      if len(row.text.strip('\n')) != 0]
    for row in pitching_stats:
        row.insert(0, player_id)
    return pitching_stats


def get_batting(profiles, player_id):
    '''
    INPUT
    ------
    profiles : bs4 soup object, containing player page html

    player_id : int, unique id assigned to each player

    OUTPUT
    ------
    batting_stats : list array, containing player's batting stats if exists
    '''
    # stats under batting table! filtered out the empty line (grey line)
    batting_stats = [row.text.split('\n')[1:-1] for row in profiles.select(
                     'table#standard_batting tbody tr')
                     if len(row.text.strip('\n')) != 0]
    for row in batting_stats:
        row.insert(0, player_id)
    return batting_stats


def get_fielding(profiles, player_id):
    '''
    INPUT
    ------
    profiles : bs4 soup object, containing player page html

    player_id : int, unique id assigned to each player

    OUTPUT
    ------
    fielding_stats : list array, containing player's fielding stats
                     if exists
    '''
    # stats under fielding table! filtered out the empty line (grey line)
    fielding_stats = [row.text.split('\n')[1:-1] for row in profiles.select(
                      'table#standard_fielding tbody tr')
                      if len(row.text.strip('\n')) != 0]
    for row in fielding_stats:
        row.insert(0, player_id)
    return fielding_stats


def get_column_names(profiles):
    '''
    INPUT
    ------
    profiles : bs4 soup object, containing player page html

    OUTPUT
    ------
    lists, each containing column names for player stat tables
    '''
    pitching_columns = profiles.select(
        'table#standard_pitching tr')[0].text.strip('\n').split('\n')
    batting_columns = profiles.select(
        'table#standard_batting tr')[0].text.strip('\n').split('\n')
    fielding_columns = profiles.select(
        'table#standard_fielding tr')[0].text.strip('\n').split('\n')
    # inserting a column for player_id
    pitching_columns.insert(0, 'player_id')
    batting_columns.insert(0, 'player_id')
    fielding_columns.insert(0, 'player_id')
    id_columns = ['player_id', 'Name']
    bio_columns = ['player_id', 'Position', 'Birth_year',
                   'Height', 'Weight', 'Bats', 'Throws', 'Drafted']
    # replacing '%' with '_perc' to prevent error during sql table conversion
    fielding_columns = map(lambda x: x.replace('%', '_perc'), fielding_columns)
    pitching_columns = map(lambda x: x.replace('%', '_perc'), pitching_columns)
    fielding_columns = map(lambda x: 'Something' if len(x) == 0
                           else x, fielding_columns)

    return pitching_columns, batting_columns,\
        fielding_columns, id_columns, bio_columns


def put_into_DataFrame(data, pitching_columns, batting_columns,
                       fielding_columns, id_columns, bio_columns):
    '''
    INPUT
    ------
    data : dict, containing list arrays for each stat tables

    ***_columns : list, containing column names for each stat table

    OUTPUT
    ------
    Pandas DataFrames of each stat table
    '''
    df_id = pd.DataFrame(data['id'])
    df_id.columns = id_columns

    df_bio = pd.DataFrame(data['bio'])
    df_bio.columns = bio_columns

    if len(data['batting']) != 0:
        df_batting = pd.DataFrame(data['batting'])
        df_batting.columns = batting_columns
    else:
        df_batting = 'None'

    if len(data['pitching']) != 0:
        df_pitching = pd.DataFrame(data['pitching'])
        df_pitching.columns = pitching_columns
    else:
        df_pitching = 'None'

    if len(data['fielding']) != 0:
        df_fielding = pd.DataFrame(data['fielding'])
        df_fielding.columns = fielding_columns
    else:
        df_fielding = 'None'

    return df_id, df_bio, df_batting, df_pitching, df_fielding



def convert_to_sql(df_list, names, engine):
    '''
    INPUT
    ------
    df_list : list, Pandas DataFrames
    names: list, SQL table names (string)
    engine: sqlalchemy engine

    OUTPUT
    ------
    PostgreSQL tables
    '''
    for df, name in izip(df_list, names):
        if type(df) != str:
            df.to_sql(name, engine, if_exists='append')
        else:
            pass


def run():
    """
    run function; runs the whole script.
    Need Mdb_name, col_name, SQLuser, SQLpwd, and SQLdb_name before running
    """
    Mdb_name = raw_input('Please specify MongoDB db name where\
                        your raw html data is stored : ')
    col_name = raw_input('Please specify MongoDB collection name where\
                         your raw html data is stored : ')
    SQLuser = raw_input('What is your postgreSQL id? : ')
    SQLpwd = raw_input('What is password? : ')
    SQLdb_name = raw_input('Please type name of desired postgreSQL db where\
                      the tables will be stored')
    cli = MongoClient()
    db = cli[Mdb_name]
    players = db[col_name]
    engine = create_engine(
        'postgresql://{user}:{pwd}@localhost:5432/{db}'.format(
            user=SQLuser, pwd=SQLpwd, db=SQLdb_name))
    for player_id, player in enumerate(players):
        data = get_tables(player_id, player)

        pitching_columns, batting_columns,\
            fielding_columns, id_columns, bio_columns = get_column_names()

        df_id, df_bio, df_batting, df_pitching, df_fielding =\
            put_into_DataFrame(data, pitching_columns, batting_columns,
                               fielding_columns, id_columns, bio_columns)

        convert_to_sql([df_id, df_bio, df_batting, df_pitching, df_fielding],
                       ['id', 'bio', 'batting', 'pitching', 'fielding'], engine)
if __name__ == '__main__':
    run()
