# 微博爬虫

## 高度灵活的微博爬虫, 轻量, 高效, 易于使用!

### 基于 requests 实现模拟登录, 可以获取 cookie 并以 json 格式保存到本地.

利用获取的 cookie 可以登录:

> * https://m.weibo.cn/  # 触屏版
> * https://weibo.cn/  # 旧版
> * https://weibo.com/  # PC 版
> * https://s.weibo.com/  # PC 版 高级搜索

### 基于 BeautifulSoup 实现内容采集, 通过 pandas 保存 excel 到本地.

![WeiboSpider_Keyword.png](https://github.com/HEUDavid/WeiboSpider/blob/master/pictures/WeiboSpider_Keyword.png)

### 通过 threading 实现多线程爬虫, 大大提高采集效率.

多线程效率说明:

网络爬虫是 IO密集型 程序, 因此采用多线程可以显著提高效率.

相同的搜索实例, 采集 40 页微博, 每页 20 条 博文:

单个线程单个账号共采集 678 条微博, 耗时 345.29462 秒.

```python
data = get_data(search_obj, session_obj1, 1, 40)
```

两个线程两个账号共采集 684 条微博, 耗时 186.58252 秒.

```python
t1 = SpiderThread(get_data, args=(search_obj, session_obj1, 1, 20))
t2 = SpiderThread(get_data, args=(search_obj, session_obj2, 21, 40))
t1.start()
t2.start()
t1.join()
t2.join()
data = t1.get_result() + t2.get_result()
```

### 1. [WeiboLogin.py](https://github.com/HEUDavid/WeiboSpider/blob/master/WeiboLogin.py)

获取 cookie 并以 json 的格式保存到本地.

**怎么使用:**

```python
def main():
    ‘’‘
    请使用自己的账号
    ’‘’
    username = '18846426742'  # 用户名
    password = 'mdavid.cn'  # 密码
    login = WeiboLogin(username, password)
    cookies = login.get_cookie()

    cookie_name = 'cookie_' + username  # 保存 cookie 的文件名称
    data = cookies.get_dict()
    save(cookie_name, data)
```

### 2. [CookieTest.py](https://github.com/HEUDavid/WeiboSpider/blob/master/CookieTest.py)

测试 cookie 能否登录到某个 url.

**怎么使用:**

```python
html = test.get_page(url)
print(test.is_OK(html))
```

### 3. [WeiboSpider_Keyword.py](https://github.com/HEUDavid/WeiboSpider/blob/master/WeiboSpider_Keyword.py)

主要使用[微博搜索接口](https://s.weibo.com/), 通过关键字搜索, 爬取所有的结果.

**怎么使用:**

```python
def search():
    '''
    生成一个搜索实例, 参数修改请观察微博搜索的 url.
    '''
    keyword = '大卫'  # 搜索关键字
    startTime = '2019-04-22'
    endTime = '2019-04-23'
    # 微博默认按小时搜索, 我们可以控制时间范围增加查询精度
    timescope = f'custom:{startTime}-0:{endTime}-23'
    prov = '11'  # 省和直辖市
    city = '1000'  # 城市
    region = f'custom:{prov}:{city}'
    search_obj = Search(keyword, timescope, region)
    return search_obj
```

**注意点:**

```
控制爬虫休眠时间, 避免账号被封.
如何控制采集精度:
    分地区采集, 设置 region 参数;
    分时段采集, 一般地, 一次搜索微博会返回 50 页, 每页 20 条微博, 我们可以把时间切成多个, 分别采集, 得到更丰富的数据.
```

### 4. WeiboSpider_User.py

爬取一个用户的全部微博, 可以用来分析该用户并为其打标签.

### 5. WeiboSpider_Comment.py

爬取一条热门微博下的所有评论.

### 6. 环境依赖

```
Python3
requests
rsa
pandas
beautifulsoup4
openpyxl
threading
```

*作者: David*

*2019 年 04 月 19 日*