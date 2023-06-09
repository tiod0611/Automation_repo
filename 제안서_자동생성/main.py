import pandas as pd
import dotenv
import os
import argparse

from slack_api import SlackAPI
from chatgpt_api import ChatGPTAPI

def make_prompt(row):

    prompt = f"""
    협업 제안서 메일을 작성해줘.
    
    - 메일을 작성할 때 {row.company}의 최근 사업 성과에 놀라움을 표현하고, 앞으로 더욱 발전을 기대하는 표현을 넣어줘.
    - 제목 앞에 타겟 회사의 메일을 명시해줘. 예를들면
        " {row.company} : asdf@asdf.com
        
        이메일 제목 : " 이런 식으로.
        
    - 적절한 이메일 제목을 만들어줘.
    - 다음 내용을 토대로 {row.company}에 보내는 제안서를 완성해줘.
    "
    우리 회사 정보
    보내는 사람: "(주)ㅁㅁ회사" 영업 담당자 'ㅇㅇㅇ'
    연락처: '000-000-0000'
    강점 1. 1000평 규모의 생산 공장을 보유하고 있기 때문에 중개 수수료가 없어 가격 경쟁력이 우수하다.
    강점 2. 숙련된 전문가와 자동화 설비가 모두 갖춰져 있어 높은 품질을 보장한다.
    
    타겟 회사 정보
    담당자 메일 : {row.email}
    {row.company}의 업종: {row.type}
    콜라보하고 싶은 제품
    1. {row.product1}
    2. {row.product2}
    3. {row.product3}

    {row.company}가 가져갈 수 있는 이점
    {row.advantage}
    
    협업 포인트
    {row.recom_point}
    "
    """

    return prompt


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='metadata.xlsx', help="input the path with metedata.csv or metadata.xlsx")
    args = parser.parse_args()

    file = args.file

    # get ENV
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    slack_token = os.environ['SLACK-TOKEN']
    openapi_key = os.environ['OPENAPI-KEY']

    # 
    slack = SlackAPI(slack_token)
    chatgpt = ChatGPTAPI(openapi_key)

    channel_id = slack.get_channel_id('제안서공유')

    # read metadata
    metadata = pd.read_excel(file)
    
    for row in metadata.itertuples(index=False):
        print(f"Let's make the proposal for {row.company}.")
        prompt = make_prompt(row)
        answer = chatgpt.run(prompt)
        slack.post_message(channel_id, answer)
        print(f"proposal for {row.company} is complete.")