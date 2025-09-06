import requests
import os

class YandexClient:
    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.api_url = 'https://api.yandex.cloud.ai/gpt/v1/chat/completions'

    def get_response(self, prompt):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}]
        }
        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")