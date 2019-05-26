# 微博模拟登录
# 作者: David
# Github: https://github.com/HEUDavid/WeiboSpider


import base64
import binascii
import json
import random
import re
import time
from urllib.parse import quote_plus

import requests
import rsa


class WeiboLogin:

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.Session = requests.Session()
        self.Session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

        # login.php?client=ssologin.js(v1.4.19) 找到 POST 的表单数据
        self.Form_Data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '0',
            'useticket': '1',
            'pagerefer': 'https://passport.weibo.com',
            'vsnf': '1',
            'service': 'miniblog',
            'pwencode': 'rsa2',
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '243',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'TEXT'  # 这里是 TEXT, META 不可以
        }

    def get_su(self):
        '''
        对应 prelogin.php
        对 账号 先 javascript 中 encodeURIComponent
        对应 Python3 中的是 urllib.parse.quote_plus
        然后在 base64 加密后 decode
        '''
        username_quote = quote_plus(self.username)
        username_base64 = base64.b64encode(username_quote.encode('utf-8'))
        su = username_base64.decode('utf-8')
        # print('处理后的账户:', su)

        self.Form_Data['su'] = su

        return su

    def get_server_data(self, su):
        '''
        预登陆获得 servertime, nonce, pubkey, rsakv
        '''
        url_str1 = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su='
        url_str2 = '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_='
        pre_url = url_str1 + su + url_str2 + str(int(time.time() * 1000))
        pre_data_res = self.Session.get(pre_url)
        server_data = eval(pre_data_res.content.decode(
            'utf-8').replace('sinaSSOController.preloginCallBack', ''))

        self.Form_Data['servertime'] = server_data['servertime']
        self.Form_Data['nonce'] = server_data['nonce']
        self.Form_Data['rsakv'] = server_data['rsakv']

        return server_data

    def get_password(self, servertime, nonce, pubkey):
        '''
        对密码进行 rsa 加密
        '''
        rsaPublickey = int(pubkey, 16)  # 16进制 string 转化为 int
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + nonce + '\n' + self.password
        message = message.encode('utf-8')
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制
        # print('处理后的密码:', passwd)

        self.Form_Data['sp'] = passwd

        return passwd

    def get_png(self, pcid):
        '''
        获取验证码, 如何识别验证码? 
        '''
        png_url = 'https://login.sina.com.cn/cgi/pin.php?r=' + \
            str(int(random.random() * 100000000)) + '&s=0&p=' + pcid
        png_page = self.Session.get(png_url)
        with open('pin.png', 'wb') as f:
            f.write(png_page.content)
            f.close()
            print('验证码下载成功, 请到目录下查看')
        verification_code = input('请输入验证码: ')
        return verification_code

    def get_cookie(self):
        su = self.get_su()
        '''
        握草, 莫名奇妙每次登录都要输入验证码了!
        握草, 莫名其妙每次登录又不需要输入验证码了!
        {'retcode': '4049', 'reason': '为了您的帐号安全，请输入验证码'}
        {'retcode': '2093', 'reason': '抱歉！登录失败，请稍候再试'}
        {'retcode': '0', 'ticket': 'ST-NTcwNjQxMzA3Mg==-1557049968-yf-6EE75B29C64734704473DCDD74DBC755-1', 'uid': '5706413072', 'nick': '大大大卫哥'}
        '''
        for i in range(5):
            try:
                # 不输入验证码
                server_data = self.get_server_data(su)
                self.get_password(
                    server_data['servertime'],
                    server_data['nonce'],
                    server_data['pubkey'])
                login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_' + str(
                    time.time() * 1000)

                login_page = self.Session.post(login_url, data=self.Form_Data)
                ticket_js = login_page.json()
                print('不输入验证码登录成功, 用户昵称:', ticket_js['nick'])
                break

            except BaseException:
                # 输入验证码
                server_data = self.get_server_data(su)  # 刷新
                self.get_password(
                    server_data['servertime'],
                    server_data['nonce'],
                    server_data['pubkey'])
                login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_' + str(
                    time.time() * 1000)

                self.Form_Data['door'] = self.get_png(server_data['pcid'])

                login_page = self.Session.post(login_url, data=self.Form_Data)
                ticket_js = login_page.json()

                if ticket_js['retcode'] != '0':
                    print(ticket_js['reason'])
                    # return None

                else:
                    print('输入验证码登录成功, 用户昵称:', ticket_js['nick'])
                    break

        else:
            return None

        ticket = ticket_js['ticket']
        ssosavestate = ticket.split('-')[2]
        # 处理跳转
        jump_ticket_params = {
            'callback': 'sinaSSOController.callbackLoginStatus',
            'ticket': ticket,
            'ssosavestate': ssosavestate,
            'client': 'ssologin.js(v1.4.19)',
            '_': str(time.time() * 1000),
        }
        jump_url = 'https://passport.weibo.com/wbsso/login'

        jump_login = self.Session.get(jump_url, params=jump_ticket_params)
        jump_login_data = json.loads(
            re.search(r'{.*}', jump_login.text).group(0))
        print('登录状态:', jump_login_data)
        if not jump_login_data['result']:
            # 登录失败 退出
            return None

        # PC 版 个人主页
        weibo_com_home = 'https://weibo.com/u/' + \
            jump_login_data['userinfo']['uniqueid']
        weibo_com_home_page = self.Session.get(weibo_com_home)
        # print('weibo_com_home_page.cookies', weibo_com_home_page.cookies)
        # print(weibo_com_home_page.text[:1500:])
        weibo_com_home_title_pat = r'<title>(.*)</title>'
        weibo_com_home_title = re.findall(
            weibo_com_home_title_pat,
            weibo_com_home_page.text)[0]
        print('PC 版个人主页:', weibo_com_home_title)  # PC 版登录成功

        # PC 版 首页
        weibo_com = 'https://weibo.com'
        weibo_com_page = self.Session.get(weibo_com)
        # print('weibo_com_page.cookies', weibo_com_page.cookies)
        # print(weibo_com_page.text[:1500:])

        # PC 版 搜索页
        s_weibo_com = 'https://s.weibo.com'
        s_weibo_com_page = self.Session.get(s_weibo_com)

        # 触屏版 m.weibo.com
        mParams = {
            'url': 'https://m.weibo.cn/',
            '_rand': str(time.time()),
            'gateway': '1',
            'service': 'sinawap',
            'entry': 'sinawap',
            'useticket': '1',
            'returntype': 'META',
            'sudaref': '',
            '_client_version': '0.6.26',
        }
        murl = 'https://login.sina.com.cn/sso/login.php'
        mhtml = self.Session.get(murl, params=mParams)

        mpa = r'replace\((.*?)\);'
        mres = re.findall(mpa, mhtml.text)[0]  # 从新浪通行证中找到跳转链接

        mlogin = self.Session.get(eval(mres))

        m_weibo_com = 'https://m.weibo.cn'
        m_weibo_com_page = self.Session.get(m_weibo_com)

        login_start = m_weibo_com_page.text.index('login:')
        uid_start = m_weibo_com_page.text.index('uid:')

        print('触屏版登录状态')
        print(m_weibo_com_page.text[login_start:login_start + 13:])
        print(m_weibo_com_page.text[uid_start:uid_start + 17:])

        # 旧版
        # weibo_cn = 'https://weibo.cn'
        # weibo_cn_page = self.Session.get(weibo_cn)
        # print(weibo_cn_page.text)

        return self.Session.cookies


def save(name, data):
    path = './cookies/' + name + '.json'
    with open(path, 'w+') as f:
        json.dump(data, f)
        print(path, '保存成功')


def main(username, password):
    # username = input('请输入账号: ')  # 用户名
    # password = input('请输入密码: ')  # 密码

    username = username
    password = password
    login = WeiboLogin(username, password)
    cookies = login.get_cookie()

    if cookies:
        data = cookies.get_dict()
        cookie_name = 'cookie_' + username  # 保存 cookie 的文件名称
        save(cookie_name, data)


def login():
    accounts = [
        ['username', 'password'],
        ['username', 'password'],
        ['username', 'password'],
        ['username', 'password']
    ]
    for account in accounts:
        main(account[0], account[1])


login()
