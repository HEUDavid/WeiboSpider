## 微博爬虫

基于 requests 实现模拟登录, 可以获取 cookie 并以 json 格式保存到本地.

基于 BeautifulSoup 实现内容采集, 用 pandas 保存 excel 到本地.

利用获取的 cookie 可以登录:
> * https://m.weibo.cn/ # 触屏版
> * https://weibo.cn/ # 旧版
> * https://weibo.com/ # PC 版
> * https://s.weibo.com/ # PC 版 高级搜索

### 1. [WeiboLogin.py](https://github.com/HEUDavid/WeiboSpider/blob/master/WeiboLogin.py)

获取 cookie 并以 json 的格式保存到本地.

**怎么使用:**

```python
def main():
    username = '18846426742' # 用户名
    password = 'mdavid.cn' # 密码
    login = WeiboLogin(username, password)
    cookies = login.get_cookie()

    cookie_name = 'cookie_' + username # 保存 cookie 的文件名称
    data = cookies.get_dict()
    save(cookie_name, data)
```

### 2. [WeiboTest.py](https://github.com/HEUDavid/WeiboSpider/blob/master/CookieTest.py)

测试 cookie 能否登录到某个 url.

### 3. [WeiboSpider_Keyword.py](https://github.com/HEUDavid/WeiboSpider/blob/master/WeiboSpider_Keyword.py)

![WeiboSpider_Keyword.png]("https://github.com/HEUDavid/WeiboSpider/blob/master/pictures/WeiboSpider_Keyword.png")

通过关键字搜索, 爬取关键字下的所有微博.

**怎么使用:**

```python
def search():
    '''
    生成一个搜索实例
    '''
    keyword = '刘强东'  # 搜索关键字
    startTime = '2019-04-20'
    endTime = '2019-04-25'
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
控制爬虫等待时间, 爬虫不是越快越好.
如何控制采集精度:
    分地区采集
    分时段采集
```

### 4. SpiderUser.py

爬取一个用户的全部微博.

### 5. SpiderComment.py

爬取一条微博下的所有评论.

### 6. 环境

```
Python3
requests
BeautifulSoup
pandas
```

*作者: David*

*2019 年 04 月 19 日*