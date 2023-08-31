import requests
from pyquery import PyQuery as pq
from test import data_data
import os
import json

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get?type=https").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

# your spider code
def getComments(comments):
    # ....
    retry_count = 1
    proxy = get_proxy().get("proxy")
    if proxy is None:
        return
    while retry_count > 0:
        try:
            # html = requests.get('https://www.example.com', proxies={"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)})
            print('----- 尝试抓取 ----')
            data_data(proxy, comments)
            return
        except Exception:
            retry_count -= 1
            # 删除代理池中代理
            delete_proxy(proxy)
    return None

comments = set()
prox_id = 1
while len(comments) < 600:
    print('代理', prox_id)
    getComments(comments)
    prox_id += 1
    print(f'共爬取{len(comments)}个评论')
f = open(os.getcwd()+'/comments.txt', 'a')
for c in list(comments):
    f.write(f'{c[0]}:\n{c[1]}\n\n')


