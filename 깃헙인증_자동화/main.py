'''

'''
import json

from DBUpdater import DBUpdater
from crawler import Crawler

def getBaekjoonData(crawler):
    crawler.login_solved()
    df = crawler.read_solved()
    
    return df

def updateDBBaekjoon(dbupdater, df):
    dbupdater.replace_into_db(df)

if __name__=='__main__':

    with open('info.json', 'r') as file:
        data = json.load(file)
        db_pw = data['db_info']['pw']

        id = data['user_info']['id']
        pw = data['user_info']['pw']
    
    # if 데이터베이스를 생성하고 데이터를 채운다면 아래를 실행하게 만들어야함. 
    # dbupdater = DBUpdater(db_pw)
    # crawler = Crawler(id, pw)

    # df = getBaekjoonData(crawler)
    # updateDBBaekjoon(dbupdater, df)

