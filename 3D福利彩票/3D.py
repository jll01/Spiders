import requests
import time
import re
import random
import math
import pymysql

from threading import Thread, Lock


class Ticket(object):
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
        }
        self.url = 'http://kaijiang.zhcw.com/zhcw/html/3d/list_{}.html'
        # 网页页码
        self.page = 1
        # 存放url
        self.urllist = []
        # 线程锁
        self.lock = Lock()
        # 连接mysql数据库
        self.connect = pymysql.connect(host='****', port=0000, user='****', passwd='****', db='****')
        self.cur = self.connect.cursor()

    def send_request(self):
        for i in range(259, 269):
            self.urllist.append(self.url.format(i))

        # 每次请求5个线程
        for j in range(math.ceil(268/5)):
            t = []
            for url in self.urllist[j*5:(j+1)*5]:
                th = Thread(target=self.requ, args=(url,))
                th.start()
                t.append(th)

            for k in t:
                k.join()

            time.sleep(random.uniform(1.2,2.5))

    def requ(self, url):
        data = requests.get(url, headers=self.headers).text
        contents = re.findall(r'<tr>\s*<td align="center">(.*?)</td>\s*<td align="center">(.*?)</td>\s*<td align="center" style="padding-left:20px;"><em>(.*?)</em>\s*<em>(.*?)</em>\s*<em>(.*?)</em></td>\s*<td align="center">(.*?)</td>\s*<td align="center">(.*?)</td>\s*<td align="center">(.*?)</td>\s*<td><strong>(.*?)</strong>\s*</td>\s*<td align="center".*?>(.*?)</td>',data)

        for content in contents:
            item = dict()
            item['date'] = content[0]
            item['issuenum'] = content[1]
            item['bai'] = content[2]
            item['shi'] = content[3]
            item['ge'] = content[4]
            item['singlenum'] = content[5]
            item['groupselect3'] = content[6]
            item['groupselect6'] = content[7]
            item['money'] = content[8].replace(',','').strip()
            item['rewardratio'] = ''.join(content[9]).replace('%','').strip()

            print(item)
            self.saveitem(item)

    def saveitem(self, item):
        """
        保存到数据库
        :param item: 要保存的数据
        """
        # 加锁
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into 3d (date,issuenum,bai,shi,ge,singlenum,groupselect3,groupselect6,money,rewardratio) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['date'],
                    item['issuenum'],
                    item['bai'],
                    item['shi'],
                    item['ge'],
                    item['singlenum'],
                    item['groupselect3'],
                    item['groupselect6'],
                    item['money'],
                    item['rewardratio'],
                )
            )
            self.connect.commit()
        except Exception as e:
            print('出错：{}'.format(e))
        # 释放
        self.lock.release()

    def main(self):
        self.send_request()


if __name__ == '__main__':
    tc = Ticket()
    tc.main()
