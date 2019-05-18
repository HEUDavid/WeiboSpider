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
            print('这一页没有内容')
            return res
        else:
            for i in soup.select('div[action-type="feed_list_item"]'):
                try:
                    blog = {}
                    blog['博主昵称'] = i.select('.name')[0].get('nick-name')
                    blog['博主主页'] = 'https:' + i.select('.name')[0].get('href')

                    weibotext = ''
                    if i.select('div[class="content"] p[node-type="feed_list_content_full"]'):
                        weibotext = i.select('div[class="content"] p[node-type="feed_list_content_full"]')[
                            0].text.replace('收起全文d', '').strip()
                    if weibotext == '':
                        if i.select('div[class="content"] p[node-type="feed_list_content"]'):
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
                date = datetime.datetime(
                    int(y),
                    int(m),
                    int(d),
                    int(H),
                    int(M)).strftime('%Y-%m-%d %H:%M')
            else:
                # 当年数据
                m, d, H, M = re.findall(r'\d+', s)
                date = datetime.datetime(
                    today.year,
                    int(m),
                    int(d),
                    int(H),
                    int(M)).strftime('%Y-%m-%d %H:%M')
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

    def __init__(self, keyword, timescope, region, type='scope=ori', include='suball=1'):
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
        elif soup.select('.s-scroll li'):
            totalpage = len(soup.select('.s-scroll li'))
        else:
            totalpage = 1  # 没有翻页, 只有一页
        self.totalPage = totalpage
        return totalpage


def search():
    '''
    每一个时间段都生成一个搜索实例, 返回一个列表
    '''
    search = []
    keyword = '华为'  # 搜索关键字
    prov = '0'  # 省市代码见图片 prov.png
    city = '1000'  # 不限城市
    region = f'custom:{prov}:{city}'

    startTime = '2018-01-01-0'
    endTime = '2019-01-01-0'
    start_date = datetime.datetime.strptime(startTime, '%Y-%m-%d-%H')
    end_date = datetime.datetime.strptime(endTime, '%Y-%m-%d-%H')

    period_length = 100  # 时间段的长度控制查询精度

    start_temp = start_date
    end_temp = start_temp + datetime.timedelta(days=period_length)

    while end_temp <= end_date:
        startTime = start_temp.strftime('%Y-%m-%d-%H')
        endTime = end_temp.strftime('%Y-%m-%d-%H')
        timescope = f'custom:{startTime}:{endTime}'
        search.append(Search(keyword, timescope, region))
        start_temp = end_temp
        end_temp = start_temp + datetime.timedelta(days=period_length)

    return search


def get_data(search_obj, session_obj, start, end):
    '''
    爬 [start, end] 页数据
    '''
    print(f'抓取 {start} 到 {end} 页')
    data = []
    for i in range(start, end + 1):
        # print('#' * 10 + f'第 {i} 页' + '#' * 10)
        url = search_obj.get_url(i)
        try:
            html = session_obj.get_page(url)
            spider = WeiboSpider(html)
            results = spider.get_results()
            if results:
                data.extend(results)
            else:
                print(f'\033[0;0;31m{url}\033[0m')
            time.sleep(random.randint(5, 10))
        except BaseException:
            print(f'出错重试: {url}')
            time.sleep(20)
            html = session_obj.get_page(url)
            spider = WeiboSpider(html)
            results = spider.get_results()
            if results:
                data.extend(results)
            else:
                print(f'\033[0;37;41m{url}\033[0m')
            time.sleep(random.randint(5, 10))
        print(f'第 {i} 页抓取结束')
    print(f'\033[0;30;47m抓取 {start} 到 {end} 页结束\033[0m')

    return data


def main():

    session_obj1 = CookieTest('./cookies/cookie_18846426742.json')  # cookie 路径
    session_obj2 = CookieTest('./cookies/cookie_admin@mdavid.cn.json')
    session_obj3 = CookieTest('./cookies/cookie_854107424@qq.com.json')
    session_obj4 = CookieTest('./cookies/cookie_965019007@qq.com.json')

    html1 = session_obj1.get_page()
    html2 = session_obj2.get_page()
    html3 = session_obj3.get_page()
    html4 = session_obj4.get_page()

    if not session_obj1.is_OK(html1):
        print('cookie_18846426742.json 失效')
        return None
    if not session_obj2.is_OK(html2):
        print('cookie_admin@mdavid.cn.json 失效')
        return None
    if not session_obj3.is_OK(html3):
        print('cookie_854107424@qq.com.json 失效')
        return None
    if not session_obj4.is_OK(html4):
        print('cookie_965019007@qq.com.json 失效')
        return None

    searchList = search()  # 就是时间范围不一样

    count = 0
    savePath = searchList[0].keyword + '.csv'

    for search_obj in searchList:

        url = search_obj.get_url(1)
        html = session_obj1.get_page(url)
        totalPage = search_obj.get_totalPage(html)
        if totalPage == 0:
            print(f'\033[0;0;43m{search_obj.timescope[7:]} 没有微博\033[0m')
            continue
        print(f'\033[0;0;33m{search_obj.timescope[7:]} 有 {totalPage} 页\033[0m')

        starttime = time.time()

        # 单线程
        # data = get_data(search_obj, session_obj1, 1, totalPage)

        # 多线程
        if totalPage < 12.5:
            data = get_data(search_obj, session_obj1, 1, totalPage)
        else:
            totalPage = 15  # demo 展示
            step = int(totalPage / 4)
            t1 = SpiderThread(get_data, args=(
                search_obj, session_obj1, 1, 1 + step))
            t2 = SpiderThread(get_data, args=(
                search_obj, session_obj2, 2 + step, 2 + step * 2))
            t3 = SpiderThread(get_data, args=(
                search_obj, session_obj3, 3 + step * 2, 3 + step * 3))
            t4 = SpiderThread(get_data, args=(
                search_obj, session_obj4, 4 + step * 3, totalPage))
            t1.start()
            t2.start()
            t3.start()
            t4.start()
            t1.join()
            t2.join()
            t3.join()
            t4.join()
            data = t1.get_result() + t2.get_result() + t3.get_result() + t4.get_result()

        endtime = time.time()
        totaltime = endtime - starttime  # 一个时间段内, 爬虫执行耗时
        print(f'\033[0;0;32m采集到 {len(data)} 条微博,\033[0m',
              '耗时: {0:.5f} 秒'.format(totaltime))

        count += len(data)

        df = pd.DataFrame(data)
        df.to_csv(savePath, mode='a', header=None, index=None)  # 追加模式
        # header: 博主主页,博主昵称,发布时间,微博内容,微博地址,微博来源,评论,赞,转发

    print(f'\033[1;0;31m共采集 {count} 条微博\033[0m')

    print(savePath, '保存成功')


main()
