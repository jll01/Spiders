import requests
import queue
import urllib3
import time

from lxml import etree
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor


# 计时装饰器
def timer(inner):
    def func(self, *args, **kwargs):
        start = time.time()
        inner(self, *args, **kwargs)
        print("complete in {} seconds".format(time.time() - start))

    return func


class Crawl(object):
    def __init__(self, pagenum):
        self.url_queue = queue.Queue()
        self.pagenum = pagenum
        self.base_url = 'https://www.xiaohua.com/duanzi?page={}'
        self.ua = UserAgent(verify_ssl=False)

    def put_url(self):
        for i in range(1, self.pagenum+1):
            self.url_queue.put(self.base_url.format(i))

    def get_page(self, url):
        # while not self.url_queue.empty():
        #     url = self.url_queue.get()
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
            self.url_queue.put(url)

    @staticmethod
    def join_list(res):
        return ''.join(res)

    @timer
    def main(self):
        # 线程池
        pool = ThreadPoolExecutor(3)
        # 添加任务到线程池中
        pool.submit(self.put_url)
        while not self.url_queue.empty():
            pool.submit(self.get_page, self.url_queue.get())

        pool.shutdown()


if __name__ == '__main__':

    urllib3.disable_warnings()

    pagenum = 5
    cra = Crawl(pagenum)
    cra.main()
