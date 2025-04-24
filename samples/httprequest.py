import requests

# 定义API的URL
url = 'https://uat.yeeflow.cn/openapi/v1/lists/30/1818904734567501824/fields'  # 替换为实际的API URL

# 定义headers，包括APIKEY
headers = {
    'apiKey': '176db230-d76c-474f-a288-da5a0e3a8d4a',  # 替换为你的实际API密钥
    'Content-Type': 'application/json'  # 根据需要设置其他头部信息，例如内容类型
}

# 创建一个session对象（可选，但推荐用于多个请求）
session = requests.Session()

# 使用session发送GET请求，并包含headers
response = session.get(url, headers=headers)

# 打印响应的状态码和响应内容
print(response.status_code)
print(response.text)
