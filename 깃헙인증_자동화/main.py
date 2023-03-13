'''

'''
import json
import os

from DBUpdater import DBUpdater
from crawler import Crawler
from run_gpt import RunGPT

def getBaekjoonData(crawler):
    # 솔브드 크롤링
    # 웹에 로그인 한 뒤 데이터를 모은다.
    crawler.login_solved()
    df = crawler.read_solved()
    
    return df

def updateDBBaekjoon(df):
    dbupdater.replace_into_db(df)


def get_solution_baekjoon_with_GPT():
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
    dbupdater.plus_attempt(number)
        
    result = crawler.summit_solution(number, solution)
    if result: # 결과가 정답이라면 저장
        dbupdater.update_isSolved(number)
        save_to_py(number, solution)
        return True
    else:
        get_solution_and_summit(crawler)

def get_solution_and_summit(crawler):
    solution, number = get_solution_baekjoon_with_GPT()

    """
    로그인-문제 접근-언어 변경 및 제출- 결과 확인 - 틀릴 경우 반복(최대 3번)/맞은 경우 코드 저장
    """

    
    return summit(crawler, number, solution)


def save_to_py(number, solution):
    path = f"C:/Users/Kyeul/Desktop/code/baekjoon_gpt_solution/{number}.py"

    with open(path, 'w', encoding='utf8') as f:
        f.write(solution)

    print(f"코드 결과물 '{number}.py'로 저장함")        

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
    
    global dbupdater
    dbupdater = DBUpdater(db_pw)
    global runGPT
    runGPT = RunGPT(key)

    # 데이터베이스를 업데이트 한다면 
    if init_db:
        crawler = Crawler(id, pw)
        df = getBaekjoonData(crawler)
        updateDBBaekjoon(dbupdater, df)

    crawler = Crawler(id, pw)
    crawler.login_solved()
    for _ in range(3):
        isSolved = get_solution_and_summit(crawler)
        if isSolved: # 정답이라면 commit~!
            os.system("start cmd /k git_command.bat")
            os.system("exit")
            print('Github Commit도 완료!')
            break

    