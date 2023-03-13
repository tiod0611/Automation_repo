'''
GPT에 질의를 보내고 답변을 요청받아서 저장하는 코드
'''
import openai


class RunGPT:
    def __init__(self, key):
        openai.api_key = key

    def run(self, query):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":query}]
        )
        solution = response['choices'][0]['message']['content']

        print('제공된 solution은 다음과 같습니다.')
        print(solution)
        return solution