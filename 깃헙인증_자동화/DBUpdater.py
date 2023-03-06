'''
DB에 데이터를 저장하거나, 데이터 변경을 진행하는 코드.

> 추후에 크롤링 부분을 따로 분리할 예정임.
'''

import pymysql
import pandas as pd


class DBUpdater:

    def __init__(self, db_pw):
        """
        생성자 : mysql 연결 
        최초 실행시 테이블을 생성한다.
        """

        self.conn = pymysql.connect(host='127.0.0.1', user='root', password=db_pw, db='baekjoon', charset='utf8')

        with self.conn.cursor() as curs:
            sql="""
            CREATE TABLE IF NOT EXISTS problem_info(
                number INT,
                title VARCHAR(40),
                level INT,
                g_attempt INT,
                PRIMARY KEY (number)
            );
            
            """
            curs.execute(sql)

        with self.conn.cursor() as curs:
            sql="""
            CREATE TABLE IF NOT EXISTS attempt(
                number INT,
                my_attempt INT,
                isSolved BOOLEAN,
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


    def replace_into_db(self, df):
        '''
        데이터베이스의 데이터를 입력한다.
        '''
        with self.conn.cursor() as curs:
            for r in df.itertuples(index=False):
                print(r)
                sql=f"REPLACE INTO problem_info VALUES ({r.number}, '{r.title}', {r.level}, {r.attempt});"
                curs.execute(sql)

                sql=f"REPLACE INTO attempt VALUES ({r.number}, 0, {r.isSolved});"
                curs.execute(sql)
    
            
            self.conn.commit()
            print(f"[{len(df)}]개의 데이터 DB 저장 완료")

    def update_isSolved(self, number):
        '''
        해결한 문제의 isSolved 값을 변경한다.
        '''

        with self.conn.cursor() as curs:
            sql=f"SELECT my_attempt FROM attempt WHERE number={number}"
            curs.execute(sql)
            my_attempt = curs.fetchone()

            sql=f"""
            UPDATE attempt
            SET isSolved = True
            SET my_attempt = {my_attempt + 1}
            WHERE number = {number};
            """
            curs.execute(sql)
        
        self.conn.commit()
        print("f{number} 문제를 해결했습니다.")

    def select_problem(self):
        '''
        해결할 문제를 선택하는 함수
        '''
        with self.conn.cursor() as curs:
            sql=f"""
            SELECT problem_info.number, title
            FROM problem_info
            INNER JOIN attempt
            ON problem_info.number = attempt.number 
            WHERE attempt.isSolved = False AND problem.g_attempt > 5000
            """

            df = pd.read_sql(sql, self.conn)
            return df

                



