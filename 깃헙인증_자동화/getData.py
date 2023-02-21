'''
솔브드에서 내가 풀지 않은 문제 정보를 모두 가져오는 코드입니다.

진행 과정은 다음과 같음.

1. solved에 접속해서 로그인을 진행함.
2. 검색할 레벨 url로 이동
3. 전체 문제에서 제목과 url, 문제 번호를 가져옴.
4. 풀이한 문제 정보를 가져옴.
5. 3에서 4를 제거함
6. 결과를 반환함.

'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json


# url = 'https://solved.ac/problems/level/2'

# 크롬 드라이버 실행
global driver
driver = webdriver.Chrome()
global wait
wait = WebDriverWait(driver, 10)


# User-Agent 설정
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument('user-agent=' + user_agent)

# # URL 접속
# driver.get(url)
# # time.sleep(1)
# driver.refresh()

# # span 태그의 'class'가 'css-1raije9'인 element 찾기
# span_elems = driver.find_elements(By.CLASS_NAME, 'span.css-1raije9')

# result = []

# # a 태그의 href 속성값 가져오기
# for elem in span_elems:
#     a_elem = elem.find_element(By.CSS_SELECTOR, 'a')
#     href_val = a_elem.get_attribute('href')

#     result.append(href_val)
#     print(href_val)


# # 크롬 드라이버 종료
# driver.quit()



class AutoCommitWithChatGPT:
    '''
    ChatGPT를 응용해서 알고리즘 문제풀이 솔루션을 받고 자동으로 커밋하는 코드를 작성한다.
    '''

    def __init__(self, id, pw):
        self.id = id
        self.pw = pw
        
    def loginSolved(self):
        login_url = "https://www.acmicpc.net/login?next=%2Fsso%3Fsso%3Dbm9uY2U9YTM5YWVhYTk4MWNhYjU1YWEwZDRlZDQ4Nzc3NzEzOGM%253D%26sig%3D1ca260b9abbbe4df2b002254dd94a7f31b373ff0270b243408963284f8fcd7a1%26redirect%3Dhttps%253A%252F%252Fsolved.ac%252Fapi%252Fv3%252Fauth%252Fsso%253Fprev%253D%25252F"
        driver.get(login_url)

        
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="login_form"]/div[2]/input'))
        )


        user_id = driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/input')
        user_pw = driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/input')

        user_id.send_keys(self.id)
        user_pw.send_keys(self.pw)

        login_bt = driver.find_element(By.XPATH, '//*[@id="submit_button"]')
        login_bt.click()  

        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="login_form"]/div[4]/div[2]/a'))
        )

        login_bt_2 = driver.find_element(By.XPATH, '//*[@id="login_form"]/div[4]/div[2]/a')
        login_bt_2.click()

        
    def getSolvedData():
        '''
        솔브드에 접근한 뒤 해결하지 않은 문제 정보를 가져옴
        '''
        solved_url = 'https://solved.ac/problems/level/2'
        driver.get(solved_url)

        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1raije9'))
        )

        numbers = driver.find_elements(By.CLASS_NAME, 'css-1raije9')
        names = driver.find_elements(By.CLASS_NAME, '__Latex__')
        
        # 이미 해결한 문제 idx 찾기

        SolvedIndex = [idx for idx, x in enumerate(numbers) if 'ac' in x.get_attribute('class')]

        # numbers와 names에서 해결한 문제를 제거.



if __name__ == '__main__':

    with open('info.json', 'r') as json:
        data = json.load()
        id = data['id']
        pw = data['pw']

    acwc = AutoCommitWithChatGPT(id, pw)

