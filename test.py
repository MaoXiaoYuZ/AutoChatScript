import requests
import ssl
import certifi

MODEL = "chatgpt-3.5-turbo"
OPENAI_SECRET_KEY = "none"
# Assuming MODEL and OPENAI_SECRET_KEY are defined earlier in your code.

def chat_with_chatgpt(prompt: str):
    payload = {
        'model': MODEL,
        'messages': [
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_SECRET_KEY}"
    }
    url = 'http://127.0.0.1:8000/v1/chat/completions'
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=certifi.where())
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                print(f"OpenAI request failed with error {response_data['error']}")
                return None
            return response_data['choices'][0]['message']['content']
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

response = chat_with_chatgpt('what can you do for me')
print(response)