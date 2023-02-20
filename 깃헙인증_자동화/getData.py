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

import pandas as pd


url = 'https://solved.ac/problems/level/2'

# 크롬 드라이버 실행
driver = webdriver.Chrome()

# User-Agent 설정
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument('user-agent=' + user_agent)

# URL 접속
driver.get(url)
# time.sleep(1)
driver.refresh()

# span 태그의 'class'가 'css-1raije9'인 element 찾기
span_elems = driver.find_elements(By.CLASS_NAME, 'span.css-1raije9')

result = []

# a 태그의 href 속성값 가져오기
for elem in span_elems:
    a_elem = elem.find_element(By.CSS_SELECTOR, 'a')
    href_val = a_elem.get_attribute('href')

    result.append(href_val)
    print(href_val)


# 크롬 드라이버 종료
driver.quit()