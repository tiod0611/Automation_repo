'''

'''
import json
import pandas as pd


from DBUpdater import DBUpdater
from crawler import Crawler

def getBaekjoonData():
    crawler.login_solved()
    df = crawler.read_solved()
    
    return df

def updateDBBaekjoon(df):
    dbupdater.replace_into_db(df)

if __name__=='__main__':

    with open('info.json', 'r') as file:
        data = json.load(file)
        db_pw = data['db_info']['pw']

        id = data['user_info']['id']
        pw = data['user_info']['pw']
    global dbupdater
    dbupdater = DBUpdater(db_pw)
    global crawler
    crawler = Crawler(id, pw)

    getBaekjoonData()

