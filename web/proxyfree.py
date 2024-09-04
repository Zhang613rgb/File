import requests
from bs4 import BeautifulSoup

# 目标网址
url = 'https://www.javbus.com/'

# 发送请求并获取响应
response = requests.get(url)

# 保存网页响应到文件
with open('response.html', 'w', encoding='utf-8') as file:
    file.write(response.text)

# 解析网页内容
soup = BeautifulSoup(response.text, 'html.parser')

# 提取防屏蔽地址的示例（假设地址在某个特定的元素中）
# 请根据实际网页结构修改选择器
defensive_address = None
for a_tag in soup.find_all('a', href=True):
    if '防屏蔽' in a_tag.text:
        defensive_address = a_tag['href']
        break

if defensive_address:
    print(f"防屏蔽地址: {defensive_address}")
else:
    print("未找到防屏蔽地址")

