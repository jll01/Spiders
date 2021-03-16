import requests
import time
import json
import random
import pandas as pd
import pymysql
import re
import math

from threading import Thread, Lock


class Piaofang(object):
    def __init__(self, start, end):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36", 
        }
        self.url = 'http://piaofang.maoyan.com/second-box?beginDate={}'
        self.start = start
        self.end = end
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()
        self.lock = Lock()

    def datelist(self):
        return [d.strftime("%Y%m%d") for d in pd.date_range(self.start, self.end)]

    def request(self):
        date_list = self.datelist()
        for i in range(math.ceil(len(date_list)/5)):
            thread = []
            for date in date_list[i*5:(i+1)*5]:
                t = Thread(target=self.getdata, args=(date, ))
                t.start()
                thread.append(t)

            for th in thread:
                th.join()

    def getdata(self, date):
        req = requests.get(self.url.format(date), headers=self.headers).text
        datas = json.loads(req)
        total = datas.get('data', 'Null')
        item = dict()
        item['queryDate'] = total.get('queryDate', '')

        movies = total.get('list', 'Null')
        for movie in movies:
            item["movieId"] = movie.get('movieId')
            item["movieName"] = movie.get('movieName')
            item["releaseInfo"] = self.totalnum(movie.get('releaseInfo')) # 累计上映天数
            item["sumBoxInfo"] = int(self.str2num(movie.get('sumBoxInfo'))) # 综合票房总票房
            item["boxInfo"] = int(self.str2int(movie.get('boxInfo'))*10000)  # 综合票房
            item["boxRate"] = movie.get('boxRate') # 综合票房占比
            item["avgViewBox"] = self.str2int(movie.get('avgViewBox'))  # 综合平均票价
            item["splitSumBoxInfo"] = int(self.str2num(movie.get('splitSumBoxInfo')))  # 分账票房总票房
            item["splitBoxInfo"] = int(self.str2int(movie.get('splitBoxInfo'))*10000)  # 分账票房
            item["splitBoxRate"] = movie.get('splitBoxRate') # 分账票房占比
            item["splitAvgViewBox"] = self.str2int(movie.get('splitAvgViewBox'))  # 分账平均票价
            item["viewInfo"] = int(self.str2num(movie.get('viewInfoV2'))) # 观影人数
            item["avgSeatView"] = movie.get('avgSeatView') # 上座率
            item["avgShowView"] = int(self.str2int(movie.get('avgShowView')))  # 场均人次
            item["showInfo"] = int(self.str2int(movie.get('showInfo')))  # 排片场次
            item["seatRate"] = movie.get('seatRate')  # 排片场次占比
            item["showRate"] = movie.get('showRate')  # 排片占比

            print(item)
            self.saveitem(item)

        time.sleep(random.uniform(1, 2.5))

    @staticmethod
    def totalnum(res):
        if res.strip().startswith('上映'):
            if res.strip() == '上映首日':
                return 1
            else:
                return ''.join(re.findall(r'(\d+)', res))
        else:
            return res.strip()

    @staticmethod
    def str2int(res):
        try:
            return float(res)
        except:
            return 0

    @staticmethod
    def str2num(res):
        if res[-1] == '万':
            return float(res[:-1])*10000
        elif res[-1] == '亿':
            return float(res[:-1])*100000000
        else:
            return float(res)

    def saveitem(self, item):
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into moviepiaofang (日期, 电影ID, 电影名称, 上座率, 场均人次, 综合平均票价, 综合票房, 综合票房占比, 累计上映天数, 排片场次占比, 排片场次, 排片占比, 分账平均票价, 分账票房, 分账票房占比, 分账票房总票房, 综合票房总票房, 观影人数) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                (
                    item["queryDate"], 
                    item["movieId"], 
                    item["movieName"], 
                    item["avgSeatView"], 
                    item["avgShowView"], 
                    item["avgViewBox"], 
                    item["boxInfo"], 
                    item["boxRate"], 
                    item["releaseInfo"], 
                    item["seatRate"], 
                    item["showInfo"], 
                    item["showRate"], 
                    item["splitAvgViewBox"], 
                    item["splitBoxInfo"], 
                    item["splitBoxRate"], 
                    item["splitSumBoxInfo"], 
                    item["sumBoxInfo"], 
                    item["viewInfo"], 
                )
            )
            self.connect.commit()
        except Exception as e:
            print('一条数据出错了！{}'.format(e))
        self.lock.release()
        # self.cur.close()
        # self.connect.close()

    def main(self):
        self.request()


if __name__ == "__main__":
    start = input('请输入起始时间, (格式：20190101)：')
    end = input('请输入截至时间, (格式：20190101)：')

    pf = Piaofang(start, end)
    pf.main()