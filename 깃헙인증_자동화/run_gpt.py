'''
GPT에 질의를 보내고 답변을 요청받아서 저장하는 코드
'''
import openai


class RunGPT:
    def __init__(self, key):
        openai.api_key = key

    def run(query):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":query}]
        )
        result = response['choices'][0]['message']['content']

        return result