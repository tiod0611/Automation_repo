import json
import pymysql

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

import pandas as pd


# 크롬 드라이버 설정
global driver
driver = webdriver.Chrome()
global wait
wait = WebDriverWait(driver, 10)

# User-Agent 설정
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument('user-agent=' + user_agent)





class DBUpdater:

    def __init__(self, db_pw, id, pw):
        """
        생성자 : mysql 연결 
        최초 실행시 테이블을 생성한다.
        """

        # 재사용하지 않는 이 변수를 여기에 두는 게 올바른지 모르겠네.. 다음에 누군가에게 질문 한번 해보자.
        self.id = id
        self.pw = pw

        self.conn = pymysql.connect(host='127.0.0.1', user='root', password=db_pw, db='autoGitCheck', charset='utf8')

        with self.conn.cursor() as curs:
            sql='''
            CREATE TABLE IF NOT EXISTS baekjoon_info(
                number INT,
                title VARCHAR(20),
                isSolved BOOLEAN,
                level INT,
                PRIMARY KEY (number)
            ) DEFAULT CHARSET=utf8;
            
            '''
            curs.execute(sql)

        self.conn.commit()

        # 
        self.conn.close()
        
    def __del__(self):
        '''
        소멸자: MySql 연결 해제
        '''
        self.conn.close()

    def login_solved(self):
        '''
        solved 웹사이트에 접속해서 계정으로 로그인한다.
        '''
        login_url = "https://www.acmicpc.net/login?next=%2Fsso%3Fsso%3Dbm9uY2U9YTM5YWVhYTk4MWNhYjU1YWEwZDRlZDQ4Nzc3NzEzOGM%253D%26sig%3D1ca260b9abbbe4df2b002254dd94a7f31b373ff0270b243408963284f8fcd7a1%26redirect%3Dhttps%253A%252F%252Fsolved.ac%252Fapi%252Fv3%252Fauth%252Fsso%253Fprev%253D%25252F"
        driver.get(login_url)

        # 로그인 페이지에서 계정 정보를 입력하고 클릭한다.
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="login_form"]/div[2]/input'))
        )

        user_id = driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/input')
        user_pw = driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/input')

        user_id.send_keys(self.id)
        user_pw.send_keys(self.pw)

        login_bt = driver.find_element(By.XPATH, '//*[@id="submit_button"]')
        login_bt.click()  

        # 백준 계정으로 솔브드에 로그인할지 묻는 화면. 수락을 클릭함
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="login_form"]/div[4]/div[2]/a'))
        )

        login_bt_2 = driver.find_element(By.XPATH, '//*[@id="login_form"]/div[4]/div[2]/a')
        login_bt_2.click()

        # 문제 없이 진행되었다면 로그인이 잘 되었을 것이다. 

    def read_solved(self):
        '''
        솔브드 레벨을 순회하며 문제 정보를 스크래핑한다.


        ### 에러 발생
        로그인을 driver로 했기 때문에 계속 selenium을 사용해야 한다. requests대신 driver.pasge_source로 파싱하자.
        '''

        max_level = 15

        for level in range(1, max_level+1):
            # 각 레벨의 1페이지에 접속하고 html 텍스트 정보를 파싱함
            url = f'https://solved.ac/problems/level/{level}'
            driver.get(url)
            html = BeautifulSoup(driver.page_source, 'lxml')

            # 마지막 페이지 번호 추출
            last_page = int(html.find_all('a', {'class':'css-1yjorof'})[-1].text)

            # 1페이지의 데이터를 수집함.
            df = pd.DataFrame(columns=['number', 'title','isSolved', 'level'])

            rows = html.find_all('tr', {'class':'css-1ojb0xa'})
            
            for row in range(1, len(rows)):
                info = rows[row].find_all('a', {'class':'css-q9j30p'})
                number = info[0].find('span').text
                title = info[1].find('span', {'class':'__Latex__'}).text
                isSolved = True if rows[row].find_all('span', {'class':'ac'}) else False

                # 데이터 삽입
                df.loc[len(df)] = [number, title, isSolved, level]


            # 2페이지부터 순회하며 데이터 수집
            for page in range(2, last_page + 1):
                pg_url = f'?page={page}'
                driver.get(url+pg_url)
                html = BeautifulSoup(driver.page_source, 'lxml')

                rows = html.find_all('tr', {'class':'css-1ojb0xa'})

                for row in range(1, len(rows)):
                    info = rows[row].find_all('a', {'class':'css-q9j30p'})
                    number = info[0].find('span').text
                    title = info[1].find('span', {'class':'__Latex__'}).text
                    isSolved = True if rows[row].find_all('span', {'class':'ac'}) else False
                    

                    # 데이터 삽입
                    df.loc[len(df)] = [number, title, isSolved, level]
                    
        return df



if __name__ == '__main__':
    with open('info.json', 'r') as file:
        data = json.load(file)
        db_pw = data['db_info']['pw']

        id = data['user_info']['id']
        pw = data['user_info']['pw']

    dbupdater = DBUpdater(db_pw, id, pw)
    dbupdater.login_solved()
    dbupdater.read_solved()
