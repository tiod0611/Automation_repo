import json
import pymysql

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import re

import pandas as pd


# 크롬 드라이버 설정
global driver
driver = webdriver.Chrome()
global wait
wait = WebDriverWait(driver, 20)

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

        self.conn = pymysql.connect(host='127.0.0.1', user='root', password=db_pw, db='baekjoon', charset='utf8')

        with self.conn.cursor() as curs:
            sql="""
            CREATE TABLE IF NOT EXISTS problem_info(
                number INT,
                title VARCHAR(40),
                isSolved BOOLEAN,
                level INT,
                korean BOOLEAN,
                PRIMARY KEY (number)
            );
            
            """
            curs.execute(sql)

        self.conn.commit()
        
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
        '''
        

        def has_korean(text):
            '''
            텍스트에 한글을 포함하고 있는지 확인하는 코드
            '''
            # 한글 유니코드 범위: AC00-D7AF
            korean_regex = re.compile("[\uac00-\ud7af]+")
            return bool(korean_regex.search(text))


        max_level = 2

        for level in range(2, max_level+1):
            # 각 레벨의 1페이지에 접속하고 html 텍스트 정보를 파싱함
            url = f'https://solved.ac/problems/level/{level}'
            driver.get(url)
            html = BeautifulSoup(driver.page_source, 'lxml')

            # 마지막 페이지 번호 추출
            last_page = int(html.find_all('a', {'class':'css-1yjorof'})[-1].text)

            # 1페이지의 데이터를 수집함.
            df = pd.DataFrame(columns=['number', 'title','isSolved', 'level', 'korean'])

            rows = html.find_all('tr', {'class':'css-1ojb0xa'})
            
            for row in range(1, len(rows)):
                info = rows[row].find_all('a', {'class':'css-q9j30p'})
                number = int(info[0].find('span').text)
                title = info[1].find('span', {'class':'__Latex__'}).text
                isSolved = True if rows[row].find_all('span', {'class':'ac'}) else False
                korean = has_korean(title)

                # 데이터 삽입
                df.loc[len(df)] = [number, title, isSolved, level, korean]


            # 2페이지부터 순회하며 데이터 수집
            for page in range(2, last_page + 1):
                pg_url = f'?page={page}'
                driver.get(url+pg_url)
                html = BeautifulSoup(driver.page_source, 'lxml')

                rows = html.find_all('tr', {'class':'css-1ojb0xa'})

                for row in range(1, len(rows)):
                    info = rows[row].find_all('a', {'class':'css-q9j30p'})
                    number = int(info[0].find('span').text)
                    title = info[1].find('span', {'class':'__Latex__'}).text
                    isSolved = True if rows[row].find_all('span', {'class':'ac'}) else False
                    korean = has_korean(title)

                    # 데이터 삽입
                    df.loc[len(df)] = [number, title, isSolved, level, korean]
        print("백준 문제 크롤링 완료")            
        return df

    # def replace_into_db(self, df):
    #     '''
    #     테이블에 데이터를 저장하고 변경하는 함수
    #     mysql에서 REPLACE INTO는 INSERT보다 강력한 기능을 가지고 있다. 
    #     이미 데이터가 있어도 오류가 발생하지 않고 변경된다는 점이다.

    #     이 함수는 DB 칼럼명을 가변적으로 받는다. 이유는 2가지 케이스를 처리하기 위함이다.
    #     case 1: DB에 새로운 데이터를 입력할 때는 전체 column에 대해서 데이터가 들어온다.
    #     case 2: 문제를 해결하고 나면 isSolved column의 값을 바꿔줘야 하는데, 이때는 해당 column의 값만 들어온다. 

    #     case별로 함수를 분리하여 만들 수도 있었지만 그냥 하나로 처리하는 방법으로 짜보기로 했다.

    #     근데 안하는 게 낫겠다. 분리하는 게 훨씬 깔끔하다.
    #     '''

    #     # db의 column을 명시하기 위해 column 명을 만들어줌
    #     columns = df.columns.to_list()
    #     db_columns = [f"('{column}')" for column in columns]
    #     db_columns = ', '.join(columns) # ('col1'), ('col2'), ('col3') 형식으로 나옴

    #     with self.conn.cursor() as curs:
    #         for data in df.itertuples(index=False):

    def insert_int_db(self, df):
        '''
        데이터베이스의 데이터를 입력한다.
        '''
        with self.conn.cursor() as curs:
            for r in df.itertuples(index=False):
                print(r)
                sql=f"INSERT INTO problem_info VALUES ({r.number}, {r.title}, {r.isSolved}, {r.level}, {r.korean});"
                curs.execute(sql)
            
            self.conn.commit()
            print(f"[{len(df)}]개의 데이터 DB 저장 완료")

    def update_isSolved(self, number):
        '''
        해결한 문제의 isSolved 값을 변경한다.
        '''
        with self.conn.cursor() as curs:
            sql=f"""
            UPDATE problem_info
            SET isSolved = True
            WHERE number = {number};
            """
            curs.execute(sql)
        
        self.conn.commit()
        print("f{number} 문제를 해결했습니다.")
                

if __name__ == '__main__':
    with open('info.json', 'r') as file:
        data = json.load(file)
        db_pw = data['db_info']['pw']

        id = data['user_info']['id']
        pw = data['user_info']['pw']

    dbupdater = DBUpdater(db_pw, id, pw)
    dbupdater.login_solved()
    df = dbupdater.read_solved()
    print(df)
    dbupdater.insert_int_db(df)
