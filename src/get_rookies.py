from selenium import webdriver
import numpy as np
import time
import pandas as pd
from sys import argv


def get_rookies(path_to_driver):
    # /home/jun/Downloads/chromedriver
    browser = webdriver.Chrome(path_to_driver)
    browser.get('http://www.baseball-reference.com')
    # You need to log in first
    raw_input('Press Enter after you log in into Baseball-Reference')

    url = 'http://www.baseball-reference.com/play-index/season_finder.cgi?\
           type=b&#gotresults&as=result_batter&offset=%s&sum=0&min_year_season\
           =2000&max_year_season=2016&min_season=1&max_season=1&min_age=0&\
           max_age=99&is_rookie=&lg_ID=lgAny&lgAL_team=tmAny&lgNL_team=\
           tmAny&lgFL_team=tmAny&lgAA_team=tmAny&lgPL_team=tmAny&lgUA_team\
           =tmAny&lgNA_team=tmAny&isActive=either&isHOF=either&isAllstar\
           =either&bats=any&throws=any&exactness=anypos&pos_1=1&pos_2=1&pos_3\
           =1&pos_4=1&pos_5=1&pos_6=1&pos_7=1&pos_8=1&pos_9=1&pos_10=1&pos_11\
           =1&games_min_max=min&games_prop=50&games_tot=&qualifiersSeason=nomin\
           &minpasValS=502&mingamesValS=100&qualifiersCareer=nomin&minpasValC\
           =3000&mingamesValC=1000&number_matched=1&orderby=Name&c1gtlt=\
           eq&c1val=0&c2gtlt=eq&c2val=0&c3gtlt=eq&c3val=0&c4gtlt=eq&c4val\
           =0&c5gtlt=eq&c5val=1.0&location=pob&locationMatch=is&pob=&pod\
           =&pcanada=&pusa=&ajax=1&submitter=1&&z=1'
    for page in np.arange(0, 3800, 200):
        time.sleep(1)
        browser.get(url % str(page))
        time.sleep(5)
        browser.get(url % str(page))
        time.sleep(5)
        # downloads csv file of the page
        browser.find_element_by_xpath(
            ".//span[contains(@onclick, 'sr_download_data')]").click()

    browser.close()
    print "Download complete. Please check your computer's Downloads directory"

def combine(file_dir, num_files):
    '''
    INTPUT
    ------
    file_dir : str, directory of the rookie files stored

    num_files : int, number of the rookie files to be combined

    OUTPUT
    ------
    rookies.csv : csv file, combined rookies data
    '''
    raw_input('Please make sure all files downloaded have been moved\
              to one directory')
    path = file_dir + '/play-index_season_finder.cgi_ajax_result_table %s.csv'

    df = pd.read_csv(file_dir +
                     '/play-index_season_finder.cgi_ajax_result_table.csv'
                     )

    for num in range(1, num_files+1):
        df1 = pd.read_csv(path % ('('+str(num)+')'))
        df = df.append(df1, ignore_index=True)

    df.to_csv('rookies.csv')
