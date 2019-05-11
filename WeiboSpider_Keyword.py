# 微博数据抓取 基于关键词
# 作者: David
# Github: https://github.com/HEUDavid/WeiboSpider


import datetime
import random
import re
import time

import pandas as pd
from bs4 import BeautifulSoup

from CookieTest import CookieTest
from SpiderThread import SpiderThread


class WeiboSpider:

    def __init__(self, html):
        self.html = html

    def get_results(self):
        '''
        将每一页的内容抽取出来
        '''
        res = []
        soup = BeautifulSoup(self.html, 'html.parser')
        if len(soup.select('.card-no-result')) > 0:
            print('没有内容')
            return res
        else:
            for i in soup.select('div[action-type="feed_list_item"]'):
                try:
                    blog = {}
                    blog['博主昵称'] = i.select('.name')[0].get('nick-name')
                    blog['博主主页'] = 'https:' + i.select('.name')[0].get('href')

                    weibotext = ''
                    if i.select(
                            'div[class="content"] p[node-type="feed_list_content_full"]'):
                        weibotext = i.select('div[class="content"] p[node-type="feed_list_content_full"]')[
                            0].text.replace('收起全文d', '').strip()
                    if weibotext == '':
                        if i.select(
                                'div[class="content"] p[node-type="feed_list_content"]'):
                            weibotext = i.select(
                                'div[class="content"] p[node-type="feed_list_content"]')[0].text.strip()
                    blog['微博内容'] = weibotext

                    blog['发布时间'] = self.get_datetime(
                        i.select('div[class="content"] p[class="from"] a')[0].get_text().strip())

                    blog['微博地址'] = 'https:' + \
                        i.select('div[class="content"] p[class="from"] a')[
                        0].get('href')

                    try:
                        blog['微博来源'] = i.select('div[class="content"] p[class="from"] a')[
                            1].get_text()
                    except BaseException:
                        blog['微博来源'] = ''

                    try:
                        sd = i.select('.card-act ul li')
                    except Exception:
                        print('sd not found...')
                        print('Something wrong with')
                    try:
                        blog['转发'] = 0 if sd[1].text.replace(
                            '转发', '').strip() == '' else int(
                            sd[1].text.replace(
                                '转发', '').strip())
                    except BaseException:
                        blog['转发'] = 0
                    try:
                        blog['评论'] = 0 if sd[2].text.replace(
                            '评论', '').strip() == '' else int(
                            sd[2].text.replace(
                                '评论', '').strip())
                    except BaseException:
                        blog['评论'] = 0
                    try:
                        blog['赞'] = 0 if sd[3].select('em')[0].get_text(
                        ) == '' else int(sd[3].select('em')[0].get_text())
                    except BaseException:
                        blog['赞'] = 0
                    res.append(blog)

                except BaseException:
                    print('忽略:', i.get_text().replace('\n', '').strip())

            return res

    def get_datetime(self, s):
        '''
        格式化时间
        '''
        try:
            today = datetime.datetime.today()
            if '今天' in s:
                H, M = re.findall(r'\d+', s)
                date = datetime.datetime(
                    today.year,
                    today.month,
                    today.day,
                    int(H),
                    int(M)).strftime('%Y-%m-%d %H:%M')
            elif '分' in s:
                M = re.findall(r'\d+', s)[0]
                date = datetime.datetime(
                    today.year,
                    today.month,
                    today.day,
                    today.hour,
                    int(M)).strftime('%Y-%m-%d %H:%M')
            elif '秒' in s:
                date = datetime.datetime(
                    today.year,
                    today.month,
                    today.day,
                    today.hour,
                    today.minute).strftime('%Y-%m-%d %H:%M')
            elif '年' in s:
                y, m, d, H, M = re.findall(r'\d+', s)
                date = datetime.datetime(int(y), int(m), int(
                    d), int(H), int(M)).strftime('%Y-%m-%d %H:%M')
            else:
                # 当年数据
                m, d, H, M = re.findall(r'\d+', s)
                date = datetime.datetime(today.year, int(m), int(
                    d), int(H), int(M)).strftime('%Y-%m-%d %H:%M')
        except BaseException:
            print('时间格式异常', s)
            date = s

        return date


class Search:
    '''
    查询参数
    q: 刘强东
    region: custom:11:1000
    scope: ori
    suball: 1
    timescope: custom:2019-04-01:2019-04-02
    Refer: g
    page: 2
    '''

    def __init__(
            self,
            keyword,
            timescope,
            region,
            type='scope=ori',
            include='suball=1'):

        self.keyword = keyword
        self.timescope = timescope
        self.region = region  # 地点 省 市
        self.type = type  # 类型 全部 热门 原创scope=ori 关注人 认证用户 媒体 观点
        self.include = include  # 包含 含图片 含视频 含音乐 含短链
        self.totalPage = 0

    def get_url(self, page):
        '''
        拼接一个搜索 url
        '''
        url = f'https://s.weibo.com/weibo?q={self.keyword}&region={self.region}&{self.type}&{self.include}&timescope={self.timescope}&Refer=g&page={page}'
        return url

    def get_totalPage(self, html):
        '''
        通过分析第一页, 得到总共的页面数.
        '''
        soup = BeautifulSoup(html, 'html.parser')
        if len(soup.select('.card-no-result')) > 0:
            totalpage = 0
        else:
            totalpage = len(soup.select('.s-scroll li'))
        self.totalPage = totalpage
        return totalpage


def search():
    '''
    生成一个搜索实例
    '''
    keyword = '大卫'  # 搜索关键字
    startTime = '2018-04-01'
    endTime = '2018-05-01'
    # 微博默认按小时搜索, 我们可以控制时间范围增加查询精度
    timescope = f'custom:{startTime}-0:{endTime}-23'
    prov = '31'  # 省和直辖市
    city = '1000'  # 城市
    region = f'custom:{prov}:{city}'
    search_obj = Search(keyword, timescope, region)
    return search_obj


def get_data(search_obj, session_obj, start, end):
    '''
    爬 [start, end] 页数据
    '''
    print(f'抓取 {start} 到 {end} 页')
    data = []
    for i in range(start, end + 1):
        print('#' * 10 + f'第 {i} 页' + '#' * 10)
        url = search_obj.get_url(i)
        try:
            html = session_obj.get_page(url)
            spider = WeiboSpider(html)
            results = spider.get_results()
            if results:
                data.extend(results)
            time.sleep(random.randint(5, 10))
        except BaseException:
            print('出错')
            print(url)
            print('重试')
            time.sleep(20)
            html = session_obj.get_page(url)
            spider = WeiboSpider(html)
            results = spider.get_results()
            if results:
                data.extend(results)
            time.sleep(random.randint(5, 10))
        print(f'第 {i} 页抓取结束')

    print(f'{start} 到 {end} 页抓取结束')

    return data


def main():
    search_obj = search()
    session_obj1 = CookieTest('cookie_18846426742.json')  # cookie 路径
    session_obj2 = CookieTest('cookie_admin@mdavid.cn.json')

    url = search_obj.get_url(1)
    html = session_obj1.get_page(url)
    totalPage = search_obj.get_totalPage(html)

    if not totalPage:
        print('没有内容')
        return None

    print(f'共有 {totalPage} 页')

    '''
    print('展示前 3 页')  # Demo, 展示使用
    totalPage = 3
    data = get_data(search_obj, session_obj1, 1, totalPage)
    for i in data:
        print(i)
    '''

    starttime = time.time()  # 记录开始时间

    # 单线程
    # data = get_data(search_obj, session_obj1, 1, 40)

    # 多线程
    t1 = SpiderThread(get_data, args=(search_obj, session_obj1, 1, 20))
    t2 = SpiderThread(get_data, args=(search_obj, session_obj2, 21, 40))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    data = t1.get_result() + t2.get_result()

    endtime = time.time()  # 记录结束时间
    totaltime = endtime - starttime  # 执行耗时

    print("耗时: {0:.5f} 秒" .format(totaltime))  # 输出耗时

    # print(len(data))

    df = pd.DataFrame(data)
    # savePath = search_obj.keyword + '_' + \
    #     search_obj.timescope[7::] + '_' + search_obj.region[7::] + '.xlsx'
    savePath = search_obj.keyword + '.xlsx'
    df.to_excel(savePath)
    print(savePath, '保存成功')


main()
