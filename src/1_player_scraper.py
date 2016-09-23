"""Player scraper script.

This script will scrap raw html of individual player webpage with stats
which will be further extracted into different tables
for Analytical Base Table

Things to be done to upgrade:
1. Multiprocessing function to be added
2. Incorporate filter_players() with prepare_table.py script
3. Use sklearn's Pipeline
"""
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import string
import sys
import itertools
import re
import multiprocessing
import numpy as np
from functools import partial
import pdb
import pandas as pd

class scraper(object):
    """Scraper for raw html of player stats page.

    order of scraping :
        (click_initial) --> get_soup --> filter_players_by_year --> profiles
                        --> filter_players_by_league

    INPUT
    ------
    db_name : string, name of MongoDB db desired for scraping
    """

    def __init__(self, db_name):
        self.init_list = self._initial_generator()
        self.cli = MongoClient()
        self.db = self.cli[db_name]
        self.html_lst = None
        self.link_set = None
        self.link_coll = None
        self.player_coll = None

    def click_initial(self, link_coll_name, start_init='aa', end_init='zz'):
        """An intial step of scraper.

        INPUT
        ------
        link_coll_name: string, name of MongoDB collection for storing
                        link page html

        start_init : string, two letter initials of players, starting point

        end_init : string, two letter initials of players, end point

        OUTPUT
        ------
        stores html of web page(s) of each two-letter initials, which contains
            links to players whose last name start with those initials.
            e.g. 'gr' ---> Ken Griffey Jr,
        """
        self.link_coll = self.db[link_coll_name]
        # linik for searching by initials
        link = 'http://www.baseball-reference.com/register/player.cgi?initial=%s'
        html_lst = []
        start = np.where(self.init_list == start_init.lower())[0][0]
        end = np.where(self.init_list == end_init.lower())[0][0]
        # link to a certain initial, getting html
        for init in self.init_list[start: end+1]:
            html = requests.get(link % init).content
            soup = BeautifulSoup(html, 'html.parser')
            html_lst.append(soup)
            print 'storing for initials: ' + init
            self.link_coll.insert_one({'links_html': html})

    def get_soup(self, link_coll_name):
        """A second step of scraper.

        INPUT
        ------
        link_coll_name : string, name of MongoDB collection that stores
                         initials link page html

        OUTPUT
        ------
        html_lst : list, soup objects of stored html of initials link page
        """
        html_lst = []
        order = 0
        link_coll = self.db[link_coll_name]
        for data in link_coll.find():
            html = data['links_html']
            soup = BeautifulSoup(html, 'html.parser')
            html_lst.append(soup)
            print order
            order += 1
        self.html_lst = html_lst

    def filter_players_by_year(self, era):
        '''
        INPUT
        -------
        html_lst : list, a list of htmls containing links to player page
                   with stats

        era : first 2 or 3 digits of the timeframe desired to be scrapped

            - if 1990's, then 199
            - if 2000's, then 200
            - if 2010's, then 201
            - if 2000-current, then 20

        OUTPUT
        -------
        link_set : set, url of players whose last played year was in the
                   requested timeframe
        '''
        profile_link = 'http://www.baseball-reference.com/%s'
        link_set = set()
        for i, soup in enumerate(self.html_lst):
            print i
            name = soup.select('div#page_content span a')
            desc = soup.select('div#page_content span.small_text')
            name_desc = itertools.izip(name, [i.text for i in desc])
            # filter the desc by last year played
            # (if it starts with 20- e.g. 2016)
            link_set.update([profile_link % Name['href'] for Name, Desc
                             in name_desc if re.match('^%s' % str(era),
                             re.split('\s|-', Desc)[-1]) != None])
        self.link_set = link_set

    def _initial_generator(self):
        """
        INPUT
        ------
        None

        OUTPUT
        ------
        initials : list, two letter initials for iteration
        """
        initials = []
        for first_l in string.lowercase:
            for second_l in string.lowercase:
                initials.append(first_l + second_l)
        return np.array(initials)

    def profiles(self, player_coll_name):
        """
        INPUT
        ------
        player_coll_name : name of MongoDB collections where raw html
                           will be stored

        OUTPUT
        ------
        Add raw html of each player's link to a MongoDB collection
        """
        self.player_coll = self.db[player_coll_name]
        for link in self.link_set:
            html = requests.get(link).content
            self.player_coll.insert_one({'html': html})
            print link

    def filter_players_by_league(self, filtered_coll_name):
        """
        Filters out players who did NOT play in any of the Minor League system
            (Foreign Rookie, Rookie, A-, A, A+, AA, AAA)


        INPUT
        ------
        filtered_coll_name : string, name of MongoDB collection desired
                             to store the filtered player page raw html

        OUTPUT
        ------
        Store filtered player raw html data to a separate MongoDB collection
        """
        all_players = self.player_coll.find()
        self.filtered_players_coll = self.db[filtered_coll_name]

        for i, player in enumerate(all_players):
            profiles = BeautifulSoup(player['html'], 'html.parser')
            if len(profiles.select(
                   'div#page_content #info_box div span#player_name')) != 0:
                name = profiles.select(
                    'div#page_content #info_box div span#player_name')[0].text
            else:
                continue
            # column names for Teams Played For
            played_teams_columns = profiles.select(
                'table#standard_roster tr')[0].text.strip('\n').split('\n')
            played_teams_columns.extend(['Unknown', 'Date_started', 'Date_ended'])
            # stats under Teams Played For table! filtered out the empty line (grey line)
            played_teams_stats = [row.text.split('\n')[1:-1] for row
                                  in profiles.select('table#standard_roster tbody tr')
                                  if len(row.text.strip('\n')) != 0]
            print i, name

            if len(played_teams_stats) == 0:
                continue
            if len(played_teams_stats[0]) == 0:
                self.db['weird_ones'].insert_one({'html': player['html']})
            else:
                teams_played = pd.DataFrame(played_teams_stats)
                teams_played.columns = played_teams_columns
                filtered = teams_played[(teams_played["Lev"] != 'Fgn') &
                                        (teams_played["Lev"] != 'FgW') &
                                        (teams_played["Lev"] != 'Ind') &
                                        (teams_played["Lg"] != 'Mexican League')]

                if filtered.shape[0] != 0:
                    self.filtered_players_coll.insert_one({'html': player['html']})
