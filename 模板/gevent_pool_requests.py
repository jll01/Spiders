from gevent import monkey
monkey.patch_all()

import gevent
import requests
import urllib3
import time

from lxml import etree
from fake_useragent import UserAgent
from gevent import queue, pool


# 计时装饰器
def timer(inner):
    def func(self, *args, **kwargs):
        start = time.time()
        inner(self, *args, **kwargs)
        print("complete in {} seconds".format(time.time() - start))

    return func


class Crawl(object):
    """
        下面使用的是Queue存储url， 还可以先将所有url获取存储到列表中在使用spawn
    """
    def __init__(self, thnum, pagenum):
        # Pool并发数
        self.thnum = thnum
        # 爬取页数
        self.pagenum = pagenum
        self.base_url = 'https://www.xiaohua.com/duanzi?page={}'
        # User-Agent
        self.ua = UserAgent(verify_ssl=False)

    def put_url(self, q):
        # 将爬取的url添加到队列当中
        for i in range(1, self.pagenum+1):
            q.put(self.base_url.format(i))

    def get_page(self, url, q):
        # 获取详情信息
        headers = {
            'User-Agent': self.ua.random
        }
        request = requests.get(url, headers=headers, verify=False)
        if request.status_code == 200:
            html = etree.HTML(request.text)
            contents = html.xpath('//div[@class="content-left"]/div[@class="one-cont"]')
            for content in contents:
                item = dict()
                item['nickname'] = self.join_list(content.xpath('./div[1]/div/a/i/text()'))
                item['content'] = self.join_list(content.xpath('./p[@class="fonts"]/a/text()'))
                item['support'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                item['not_support'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                item['collect'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                item['message'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                item['share'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                print(item)
        else:
            # 请求错误的话重新添加到队列下次重新爬虫
            q.url_queue.put(url)

    @staticmethod
    def join_list(res):
        # 拼接列表中的值
        return ''.join(res)

    @timer
    def main(self):
        # 队列
        q = queue.Queue()
        # 池
        g_pool = pool.Pool(self.thnum)
        self.put_url(q)
        while not q.empty():
            url = q.get()
            g_pool.add(gevent.spawn(self.get_page, url, q))
        g_pool.join()


if __name__ == '__main__':

    urllib3.disable_warnings()

    threadNum = 3
    pageNum = 5
    cra = Crawl(threadNum, pageNum)
    cra.main()
