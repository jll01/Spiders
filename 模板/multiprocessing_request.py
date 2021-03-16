import requests
import urllib3
import time

from lxml import etree
from fake_useragent import UserAgent
from multiprocessing import Process, Queue


# 计时装饰器
def timer(inner):
    def func(self, *args, **kwargs):
        start = time.time()
        inner(self, *args, **kwargs)
        print("complete in {} seconds".format(time.time() - start))

    return func


class Crawl(object):
    def __init__(self, thnum, page_num):
        self.url_queue = Queue()
        self.thnum = thnum
        self.pagenum = page_num
        self.base_url = 'https://www.xiaohua.com/duanzi?page={}'
        self.ua = UserAgent(verify_ssl=False)
        self.urls = []

    def put_url(self):
        for i in range(1, self.pagenum+1):
            self.url_queue.put(self.base_url.format(i))
            # self.urls.append(self.base_url.format(i))
        # return self.url_queue.qsize()

    def get_page(self):
        while not self.url_queue.empty():
            url = self.url_queue.get()
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
        th_put = Process(target=self.put_url)
        th_put.run()
        for i in range(self.thnum):
            thread_url = Process(target=self.get_page)
            thread_url.run()


if __name__ == '__main__':

    urllib3.disable_warnings()

    threadNum = 3
    pagenum = 50
    cra = Crawl(threadNum, pagenum)
    cra.main()
