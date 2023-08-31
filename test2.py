import requests
from pyquery import PyQuery as pq
import time
import random
from verify import Douban

s = requests.session()
# def data_html():
#     url = 'https://accounts.douban.com/j/mobile/login/basic'
#     headers = {
#         "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
#     }
#     data = {
#         'name':"usrnm",
#         "password":"pswd",
#         "remember":"false"
#     }
#     r = s.post(url,headers=headers,data=data,verify = False)
#     if '安静' in r.text:
#         print('登录成功')
#     else:
#         print('登录失败')

def data_shuju(count=0, proxy=None, comments=set()):
    print('开始爬取第%d页' % int(count))
    start = int(count * 20)
    headers = {
        "User-Agent":f"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{proxy.split(':')[0]} Safari/537.36"
    }
    # url2 = 'https://movie.douban.com/subject/26794435/comments?start=%d&limit=20&sort=new_score&status=P' %(start)
    url2 = f'https://movie.douban.com/subject/26631790/comments?start={start}&limit=40&status=P&sort=new_score'
    try:
        r2 = s.get(url2,headers=headers, proxies={"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}, timeout=2).content
    except Exception:
        print('>> 出现异常，跳过')
        return
    doc = pq(r2)
    items = doc('.comment-item').items()
    # print(items)
    for i in items:
        name = i('.comment-info a').text()
        if not name:
            return 0
        content = i('.short').text()
        comment = (name, content)
        comments.add(comment)
        # print('comment added')
        # with open('./comments.txt','a+',encoding='utf-8') as f:
        #     f.write(f'{name}:\n{content}\n\n')

def data_data(proxy, comments): 
    # douban = Douban(proxy)  # 实例化
    # douban.login()  # 之后调用登陆方法
    count = 0 
    for i in range(20): 
        data_shuju(count, proxy, comments)
        count += 1
        time.sleep(random.random() * 3) 

    print('爬取完毕')