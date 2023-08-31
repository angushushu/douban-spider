import requests
from bs4 import BeautifulSoup

# 豆瓣电影页面的URL
url = 'https://movie.douban.com/subject/26631790/comments?status=P'

# 发起HTTP GET请求获取页面内容
response = requests.get(url)

# 使用BeautifulSoup解析页面内容
soup = BeautifulSoup(response.text, 'html.parser')

# 获取所有评论的元素
comments = soup.find_all(class_='comment-item')

print(len(comments))
# 遍历评论元素并提取评论内容
for comment in comments:
    # 提取用户名
    username = comment.find(class_='comment-info').find('a').text.strip()
  
    # 提取评论内容
    content = comment.find(class_='short').text.strip()
  
    # 打印用户名和评论内容
    print('用户名:', username)
    print('评论内容:', content)
    print('---')

# 判断评论是否为空
if len(comments) == 0:
    print('暂无评论')

# 显示爬虫结束提示
print('本次爬虫结束')