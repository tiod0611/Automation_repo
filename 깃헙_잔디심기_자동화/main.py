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


def get_solution_baekjoon_from_GPT():
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



def save_to_py(number, solution):
    path = f"C:/Users/Kyeul/Desktop/code/baekjoon_gpt_solution/{number}.py"

    with open(path, 'w', encoding='utf8') as f:
        f.write('# 아래 코드는 ChatGPT가 자동으로 생성한 코드입니다.\n')
        f.write(f'# 문제 정보: {number}\n')
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

    solution, number = get_solution_baekjoon_from_GPT()

    crawler = Crawler(id, pw)
    crawler.login_solved()

    while True:
        isSolved = summit(crawler, number, solution)

        if isSolved: # 정답이라면 commit~!
            os.system("start cmd /k git_command.bat")
            os.system("exit")
            print('Github Commit도 완료!')
            break
        else:
            print("[재도전]  ", end='')
            solution, number = get_solution_baekjoon_from_GPT()

    