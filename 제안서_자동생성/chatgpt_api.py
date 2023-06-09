import openai


class ChatGPTAPI:
    def __init__(self, key):
        openai.api_key = key

    def run(self, query):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":query}]
        )
        answer = response['choices'][0]['message']['content']

        return answer