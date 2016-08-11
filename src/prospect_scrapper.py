from bs4 import BeautifulSoup
import requests
import pandas as pd
from collections import defaultdict

def scrapper():
    team_nums = range(2, 33)
    url = 'http://www.thebaseballcube.com/prospects/byTeam.asp?T=%s'
    for num in team_nums:
        print url % str(num)
        response = requests.get(url % str(num)).content
        soup = BeautifulSoup(response, 'html.parser')
        year = soup.select('tr.sectionRow')[0].text.split()[0]  # year
        team_name = ' '.join([soup.select('tr.sectionRow')[0].text.split()[1],
                              soup.select('tr.sectionRow')[0].text.split()[2]])
        col_name = (soup.select('tr.headerRow')[0].text).strip().split('\n')
        make_table(soup, col_name, team_name)


def make_table(soup, col_name, team_name):
    col_name.insert(0, 'Year')
    col_name.insert(0, 'Team')
    ix_lst = []
    for i in range(0, 11):
        ix_lst.append(range(3+(12*i), 13+(12*i)))
    yearly = defaultdict(list)
    for ix, x in enumerate(ix_lst):
        for lst_ix, y in enumerate(x):
            yearly[2016-ix].append([
                i.text for i in soup.select('tr')[y].select('td')])
            yearly[2016-ix][lst_ix].insert(0, 2016-ix)
            yearly[2016-ix][lst_ix].insert(0, team_name)
    rows = []
    for key in yearly.keys()[::-1]:
        rows.extend(yearly[key])
    df = pd.DataFrame(rows)
    df.columns = col_name
    df.to_csv('%s.csv' % team_name)
    return team_name + ', done'

if __name__ == '__main__':
    scrapper()
