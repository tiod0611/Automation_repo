'''

to do
글로벌 유저들의 맞춘횟수 정보를 입력받아야함.
'''


import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

import time


# User-Agent 설정
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument('user-agent=' + user_agent)

class Crawler:
    def __init__(self, id, pw):
        '''
        백준 아이디와 비밀번호를 초기화
        '''
        self.id = id
        self.pw = pw

        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30)

    def login_solved(self):
        '''
        solved 웹사이트에 접속해서 계정으로 로그인한다.
        '''
        login_url = "https://www.acmicpc.net/login?next=%2Fsso%3Fsso%3Dbm9uY2U9YTM5YWVhYTk4MWNhYjU1YWEwZDRlZDQ4Nzc3NzEzOGM%253D%26sig%3D1ca260b9abbbe4df2b002254dd94a7f31b373ff0270b243408963284f8fcd7a1%26redirect%3Dhttps%253A%252F%252Fsolved.ac%252Fapi%252Fv3%252Fauth%252Fsso%253Fprev%253D%25252F"
        self.driver.get(login_url)

        # 로그인 페이지에서 계정 정보를 입력하고 클릭한다.
        self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="login_form"]/div[2]/input'))
        )

        user_id = self.driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/input')
        user_pw = self.driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/input')

        user_id.send_keys(self.id)
        user_pw.send_keys(self.pw)

        login_bt = self.driver.find_element(By.XPATH, '//*[@id="submit_button"]')
        login_bt.click()  

        # 백준 계정으로 솔브드에 로그인할지 묻는 화면. 수락을 클릭함
        self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="login_form"]/div[4]/div[2]/a'))
        )

        login_bt_2 = self.driver.find_element(By.XPATH, '//*[@id="login_form"]/div[4]/div[2]/a')
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

        df = pd.DataFrame(columns=['number', 'title','isSolved', 'level', 'attempt'])
        
        max_level = 15 # 골드 1

        for level in range(1, max_level+1):
            # 각 레벨의 1페이지에 접속하고 html 텍스트 정보를 파싱함
            url = f'https://solved.ac/problems/level/{level}'
            self.driver.get(url)
            html = BeautifulSoup(self.driver.page_source, 'lxml')

            # 마지막 페이지 번호 추출
            last_page = int(html.find_all('a', {'class':'css-1yjorof'})[-1].text)

            # 1페이지의 데이터를 수집함.

            rows = html.find_all('tr', {'class':'css-1ojb0xa'})
            
            for row in range(1, len(rows)):
                info = rows[row].find_all('a', {'class':'css-q9j30p'})
                number = int(info[0].find('span').text)
                title = info[1].find('span', {'class':'__Latex__'}).text
                
                #한국어로 된 문제가 아니라면 저장하지 않고 패스한다.          
                korean = has_korean(title)
                if korean == False: 
                    continue

                attempt = rows[row].find('div', {'class':'css-1ujcjo0'}).text
                attempt = int(attempt.replace(",", ''))
                isSolved = True if rows[row].find_all('span', {'class':'ac'}) else False
                title = re.sub("'", "''", title) # 따옴표를 ''로 변경함.

                #데이터 삽입
                df.loc[len(df)] = [number, title, isSolved, level, attempt]

            # 2페이지부터 순회하며 데이터 수집
            for page in range(2, last_page + 1):
                pg_url = f'?page={page}'
                self.driver.get(url+pg_url)
                html = BeautifulSoup(self.driver.page_source, 'lxml')

                rows = html.find_all('tr', {'class':'css-1ojb0xa'})

                for row in range(1, len(rows)):
                    info = rows[row].find_all('a', {'class':'css-q9j30p'})
                    number = int(info[0].find('span').text)
                    title = info[1].find('span', {'class':'__Latex__'}).text
                    
                    #한국어로 된 문제가 아니라면 저장하지 않고 패스한다.          
                    korean = has_korean(title)
                    if korean == False: 
                        continue
                    
                    attempt = rows[row].find('div', {'class':'css-1ujcjo0'}).text
                    attempt = int(attempt.replace(",", ''))
                    isSolved = True if rows[row].find_all('span', {'class':'ac'}) else False
                    title = re.sub("'", "''", title) # 따옴표를 ''로 변경함.

                    #데이터 삽입
                    df.loc[len(df)] = [number, title, isSolved, level, attempt]
        print("백준 문제 크롤링 완료. 총 문제 수 : ", len(df))      
        self.driver.quit()      
        return df


    def summit_solution(self, number, solution):
        '''
        백준 문제에 접근하여 문제를 제출함
        '''
        solution_lines = solution.split('\n')


        summit_url = f'https://www.acmicpc.net/submit/{number}'

        self.driver.get(summit_url) # 문제 제출 페이지에 접근

        self.driver.find_element(By.XPATH, '//*[@id="submit_form"]/div[2]/div/div[3]/label').click()

        # 코드 작성
        self.driver.find_element(By.XPATH, '//*[@id="submit_form"]/div[3]/div/div/div[6]').click()
        textarea = self.driver.find_element(By.XPATH, '//*[@id="submit_form"]/div[3]/div/div/div[1]/textarea') 
        
        times = 1 # 들여쓰기 발생 횟수를 기록
        flag = False # 들여쓰기가 최초 발생했다면 True
        for line in solution_lines:
            textarea.send_keys(line+'\n')
            # if flag:
            #     for i in range(4):
            #         textarea.send_keys(Keys.BACK_SPACE)

            if re.search(':', line) or flag:
                for i in range(4 * times):
                    textarea.send_keys(Keys.BACKSPACE)
                times += 1
                flag = True
                
            
        time.sleep(30)


        
        ### 문제 발생 ###
        # 백준 사이트는 들여쓰기 이후 줄바꿈을 하면 문장의 시작이 들여쓰기 한 부분에서 되도록했다.
        # 이 때문에 send_keys()로 제출하면 들여쓰기가 엉망이된다. 이 부분을 해결해야 한다.

        # # 코드 제출
        # self.driver.find_element(By.XPATH, '//*[@id="submit_button"]').click()
        
        # # 제출 결과 확인
        ## IDEA : tr[1]/td[4]/span의 text를 확인하고 "채점 중" 이란 단어가 있으면 기다린다
        ## 해당 단어가 사라지고 정답 표시가 있으면 정답을 그 외의 문제가 있으면 오답으로 처리하자. 

        # result = self.driver.find_element(By.XPATH, '//*[@id="status-table"]/tbody/tr[1]/td[4]/span').text
        # print(result)