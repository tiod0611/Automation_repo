'''
수강신청 실패를 만회하기 위해 제작하였습니다.
제작자: 박결
최종 업데이트: 2023-02-06

기능 1. 수강바구니에 담긴 과목들을 자동으로 새로고침하며 수강신청을 시도합니다.
기능 2. (선택) 수강신청이 성공할 경우 슬랙봇을 통해 사실을 알려줍니다.
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import requests

import time
import json
import os

from user_agent import generate_user_agent


userAgent = generate_user_agent(os='win', device_type="desktop")
headers = {"User-Agent":userAgent,
            "Accept-Language":"ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}

options = webdriver.ChromeOptions()
options.add_argument(headers)
options.add_argument("--disable-gpu")



# Check if chrome driver is installed or not
chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
driver_path = f'./{chrome_ver}/chromedriver.exe'
if os.path.exists(driver_path):
    print(f"chrom driver is insatlled: {driver_path}")
else:
    print(f"install the chrome driver(ver: {chrome_ver})")
    chromedriver_autoinstaller.install(True)

driver_path = chromedriver_autoinstaller.install()


def getUserInfo():
    with open('myInfo.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

        user_id = json_data["information"]["ID"]
        user_pw = json_data["information"]["PW"]

        hook = json_data["slack-bot"]["hook"]
        if hook is None:
            hook = False

        return user_id, user_pw, hook

class GetCourses:

    def __init__(self, user_id, user_pw, hook, driver):

        '''
        user_id : 학번
        user_pw : 비밀번호
        hook : 슬랙봇 url
        '''
        self.user_id = user_id,
        self.user_pw = user_pw,
        self.hook = hook

        self.driver = driver

    def sendMessage(self, lectureName):
        '''
        수강 신청을 성공할 때 슬랙으로 메시지를 보내는 메서드
        '''
        hook = self.hook
        title = '수강 신청 성공'
        content = f"<{lectureName}> 과목을 잡았습니다~!"
        
        # 메시지 전송
        requests.post(
            hook,
            headers={'content-type':'application/json'},
            json={
                'text' : title,
                'blocks': [
                    {
                        'type':'section', # 메시지가 묶이지 않도록 section을 사용함
                        'text':{
                            'type':'mrkdwn',
                            'text':content
                        }
                    }
                ]
            }
        )

    def getSugangUrl(self):

        '''
        수강신청 사이트로 접근하는 메서드
        '''     
        self.driver.get('https://sugang.skhu.ac.kr/')
        self.driver.implicitly_wait(5)

        self.driver.switch_to.frame('Main') # iframe 전환

        login_id = driver.find_element(By.ID, 'txtUserID')
        login_pw = driver.find_element(By.ID, 'txtPwd')
        login_bt = driver.find_element(By.ID, 'btn-login')

        login_id.send_keys(self.user_id)
        login_pw.send_keys(self.user_pw)
        login_bt.click()
        self.driver.implicitly_wait(5)

        # 수강신청 버튼 클릭
        time.sleep(0.5)
        self.driver.execute_script("fnMenuLoad('/core/coreNotice1')")
        self.driver.implicitly_wait(5)

        start_bt = driver.find_element(By.CLASS_NAME, 'btnStart')
        start_bt.click()
        time.sleep(0.5)

        self.tryGetLecture()

    def checkAlert(self):
        try:
            alertBtn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[4]/button[1]")
            alertBtn.click()
            time.sleep(0.5)
            return True
            
        except:
            return False

    def tryGetLecture(self):
        '''
        수강바구니 속 수강신청을 반복적으로 시도하는 메서드.
        모든 강의를 잡으면 종료한다.
        '''
        
        table_tr = self.driver.find_elements(By.XPATH, '//*[@id="GridBasket"]/tbody/tr')
        elementNum = 1

        #아래는 반복문 횟수를 보기위한 단순한 변수
        iters = 0

        while len(table_tr) != 1:
            reset = False # 수강신청이 성공했다면 반복을 초기화 하는 변수

            for i in range(2):
                #과목명 변수
                lectureName = self.driver.find_element(By.XPATH, '//*[@id="GridBasket"]/tbody/tr[@id="{}"]/td[2]'.format(elementNum)).text
                selectBtn = self.driver.find_element(By.XPATH, '//*[@id="GridBasket"]/tbody/tr[@id="{}"]/td[1]/button'.format(elementNum))                
                selectBtn.click()

                ## 테스트를 위한 확인 출력문
                print(lectureName, f": 클릭함 {iters}-{i}")         
                # time.sleep(0.1)
                # 알림창이 있는 지 검사
                while True: # 알림창이 계속 있으면 없을 때까지 반복
                    reset = self.checkAlert()
                    if reset == False:
                        break

            if reset == True: 
                # 수강신청이 성공했다면 페이지가 리셋되고, 테이블이 변경되었을 것이다.
                # 따라서 테이블 요소를 다시 가져와야 한다. 
                table_tr = driver.find_elements(By.XPATH, '//*[@id="GridBasket"]/tbody/tr')

                self.sendMessage(lectureName) # 슬랙봇으로 메시지 출력
                print(f"<{lectureName}> 수강신청 성공~!")
            else:
                elementNum += 1 #tr 을 하나씩 넘김
                if elementNum > len(table_tr)-1: # 접근하는 tr 원소의 숫자가 테이블의 최대 숫자보다 크다면
                    elementNum = 1 # 1로 초기화. 즉 다시 처음부터 돌라는 말.

            iters += 1

        print("All Clear~!") 



if __name__=="__main__":
    user_id, user_pw, hook = getUserInfo()

    # driver_path = "C:\chromedriver\chromedriver.exe"
    driver = webdriver.Chrome(driver_path)
    gc = GetCourses(user_id, user_pw, hook, driver)
    
    # 매크로 시작
    gc.getSugangUrl()

    
    

