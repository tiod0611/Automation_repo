'''

'''
import json

from DBUpdater import DBUpdater
from crawler import Crawler
from run_gpt import RunGPT

def getBaekjoonData(crawler):
    # 솔브드 크롤링
    # 웹에 로그인 한 뒤 데이터를 모은다.
    crawler.login_solved()
    df = crawler.read_solved()
    
    return df

def updateDBBaekjoon(dbupdater, df):
    dbupdater.replace_into_db(df)


def get_solution_baekjoon_with_GPT(dbupdater, runGPT):
    number, title = dbupdater.select_problem() # DB에서 적정 문제 가져오기

    query = f"""
            백준 {number}, '{title}' 파이썬으로 풀어줘.
            입력 예시는 작성 하지마.
            출력 예시도 작성 하지마.
            설명도 작성 하지마.
            코드만 작성해줘.
            """
    solution = runGPT.run(query)


    print()
    print("GPT: 해결책을 드렸습니다.")
    return solution, number

def summit(crawler, number, solution):
    crawler.login_solved()
    crawler.summit_solution(number, solution)

    # 아래 코드는 백준에 제출 후, 정답이 나올 때 저장하도록 하자. 
    # with open(f'{number}_solution.py', 'w') as f:
    #     f.write(result_code)
    


if __name__=='__main__':

    # ENV SETTING
    # init_db : 데이터베이스를 초기화 하는지
    init_db = False

    with open('info.json', 'r') as file:
        data = json.load(file)
        db_pw = data['db_info']['pw']

        id = data['user_info']['id']
        pw = data['user_info']['pw']

        key = data['openai-api']['key']
    
    dbupdater = DBUpdater(db_pw)
    runGPT = RunGPT(key)

    # 데이터베이스를 업데이트 한다면 
    if init_db:
        crawler = Crawler(id, pw)
        df = getBaekjoonData(crawler)
        updateDBBaekjoon(dbupdater, df)

    solution, number = get_solution_baekjoon_with_GPT(dbupdater, runGPT)


    # 이제부터 백준 사이트 자동화를 진행해야 함. 
    """
    로그인-문제 접근-언어 변경 및 제출- 결과 확인 - 틀릴 경우 반복(최대 3번)/맞은 경우 코드 저장
    """
    crawler = Crawler(id, pw)
    summit(crawler, number, solution)

    # 이제는 결과물을 자동으로 commit할 차례! 
    """
    batch 파일을 사용해 commit하기 - url링크를 슬랙봇으로 전송하기
    """




