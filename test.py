import requests

# 替换以下 URL 为你的服务地址
url = 'http://localhost:8000/v1/models'

try:
    response = requests.get(url)
    # 打印响应的状态码和内容
    print('Status Code:', response.status_code)
    print('Response Body:', response.text)
except requests.exceptions.RequestException as e:
    # 处理请求过程中的错误
    print('Error:', e)
