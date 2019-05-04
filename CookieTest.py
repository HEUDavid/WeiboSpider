# cookie 测试
# 作者: David
# Github: https://github.com/HEUDavid/WeiboSpider

import json

import requests


class CookieTest:

    def __init__(self, cookie_path):
        self.cookie_path = cookie_path
        self.Session = requests.Session()
        self.Session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
        self.Session.cookies.update(self.load_cookie())

    def load_cookie(self):
        try:
            with open(self.cookie_path, 'r') as f:
                data = json.load(f)
            return data
        except BaseException:
            print(self.cookie_path, '未找到')
            return None

    def get_page(self, url='https://s.weibo.com/'):
        html = self.Session.get(url)
        return html.text.replace('\u200b', '')

    def is_OK(self, html):
        # PC 版
        if "CONFIG['islogin'] = '1'" in html:
            return True
        # 触屏版
        elif 'login: [1][0]' in html:
            return True
        # 旧版
        elif '详细资料' in html:
            return True
        else:
            return False


def main():
    cookie_path = 'cookie_18846426742.json'
    test = CookieTest(cookie_path)

    url1 = 'https://m.weibo.cn/'  # 触屏版
    url2 = 'https://weibo.cn/'  # 旧版 还有问题
    url3 = 'https://weibo.com/'  # PC 版
    url4 = 'https://s.weibo.com/'  # PC 版 高级搜索

    html = test.get_page(url4)
    # print(html)
    print(test.is_OK(html))


# main()
