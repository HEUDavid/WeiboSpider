## 微博爬虫

基于 requests 实现, 可以获取 cookie 并以 json 格式保存到本地.

利用获取的 cookie 可以登录:
> * https://m.weibo.cn/ # 触屏版
> * https://weibo.cn/ # 旧版
> * https://weibo.com/ # PC 版
> * https://s.weibo.com/ # PC 版 高级搜索

### 1. WeiboLogin.py
获取 cookie 并以 json 的格式保存到本地.

**怎么使用**
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

### 2. WeiboTest.py
测试 cookie 能否登录到某个 url.

### 3. SpiderKeyword.py
通过关键字搜索, 爬取关键字下的所有微博.

### 4. SpiderUser.py
爬取一个用户的全部微博.

### 5. SpiderComment.py
爬取一条微博下的所有评论

### 6. 环境
```
Python3
requests
```

* 作者: David *

* 2019 年 04 月 19 日 *
