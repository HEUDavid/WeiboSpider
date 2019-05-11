# 线程类
# 作者: David
# Github: https://github.com/HEUDavid/WeiboSpider


import threading


class SpiderThread(threading.Thread):

    def __init__(self, func, args=()):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        # 得到函数返回值
        try:
            return self.result
        except Exception:
            return None
