'''
GPT에 질의를 보내고 답변을 요청받아서 저장하는 코드
'''

import requests
import json

# ChatGPT API endpoint URL
url = "https://api.openai.com/v1/engines/davinci-codex/completions"

with open('info.json', 'r') as file:
    data = json.load(file)
    key = data['openai-api']['key']

# ChatGPT API key
api_key = key

# Input text
input_text = "백준 문제 '소용돌이 예쁘게 출력하기' 1022번 문제 풀어줘"

# Request headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Request data
data = {
    "prompt": input_text,
    "max_tokens": 500,
    "temperature": 1
}

# Send API request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Get response data
response_data = response.json()

# Get generated text from response
generated_text = response_data["choices"][0]["text"]

# Print generated text
print(generated_text)