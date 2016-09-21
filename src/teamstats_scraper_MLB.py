"""MLB_teamstats_scraper scipt

This script is for scraping MLB team stats for future use
"""

import requests
from bs4 import BeautifulSoup
import datetime
from collections import defaultdict
import pandas as pd

def scrap_team_stats(url_lst, start_year=2000, stop_year=2015):
    '''
    INPUT: list of url of team batting/pitching stats, start_year, stop_year
    stop_year should not exceed current year - 1 (should exclude current year)
    OUTPUT: return dicts of column names and raw html of tables per year
    '''
    if start_year > stop_year:
        raise ValueError('stop_year must be equal or larger than start_year')
    elif stop_year == datetime.datetime.now().year:
        raise ValueError('maximum value of stop_year is current_year - 1')
    else:
        year_range = range(start_year, stop_year + 1)
    tables = defaultdict(list)
    col_name = defaultdict(list)
    for year in year_range:
        for url in url_lst:
            response = requests.get(url % ('/year/'+str(year)))
            soup = BeautifulSoup(response.content, 'html.parser')
            print url % ('/year/'+str(year))
            #print soup.select('tr.colhead')
            col_name[year].append([
                col.text for col in soup.select('tr.colhead')[0].select('td')])
            tables[year].append(soup.select('tr'))
    return col_name, tables


def aggregate_col_name(col_name):
    for key in col_name.keys():
        col_val = col_name[key]
        for i in range(1, len(col_val)):
            col_val[0].extend(col_val[i][2:])
        #print col_val[0]
        col_name[key] = col_val[0]
    return col_name


def convert_into_df(col_name, table, year):
    t = []
    for i in range(2, 32):
        content = []
        for row in table:
            content.append([html.text for html in row[i].select('td')])
        for i in range(1, len(content)):
            content[0].extend(content[i][2:])
        t.append(content[0])
    df = pd.DataFrame(t)
    df.columns = col_name
    data_type = table[0][0].text.split()[1]  # ['batting', 'pitching', 'fielding']
    df.to_csv('~/Galvanize/projects/Data/%s.csv' %
              (data_type + '_' + str(year)))
    return df

if __name__ == '__main__':
    bat_url = ['http://espn.go.com/mlb/stats/team/_/stat/batting%s',
               'http://espn.go.com/mlb/stats/team/_/stat/batting%s/type/expanded',
               'http://espn.go.com/mlb/stats/team/_/stat/batting%s/type/expanded-2'
               ]
    pit_url = ['http://espn.go.com/mlb/stats/team/_/stat/pitching%s',
               'http://espn.go.com/mlb/stats/team/_/stat/pitching%s/type/expanded',
               'http://espn.go.com/mlb/stats/team/_/stat/pitching%s/type/expanded-2'
               ]
    fie_url = ['http://espn.go.com/mlb/stats/team/_/stat/fielding%s',
               'http://espn.go.com/mlb/stats/team/_/stat/fielding%s/type/expanded',
               'http://espn.go.com/mlb/stats/team/_/stat/fielding%s/type/expanded-2'
               ]

    for lst in [bat_url, pit_url, fie_url]:
        col_name, tables =\
            scrap_team_stats(lst, start_year=2015, stop_year=2015)
        col_name = aggregate_col_name(col_name)
        for year in col_name.keys():
            convert_into_df(col_name[year], tables[year], year)
