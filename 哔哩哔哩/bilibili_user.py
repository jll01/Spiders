import requests
import time

from queue import Queue
from threading import Thread
from fake_useragent import UserAgent


class Bilibili(object):
    def __init__(self):
        self.space_url = '''https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'''
        self.relation_url = '''https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp'''
        self.upstat_url = '''https://api.bilibili.com/x/space/upstat?mid={}&jsonp=jsonp'''
        self.navnum_url = '''https://api.bilibili.com/x/space/navnum?mid={}&jsonp=jsonp'''
        self.queue = Queue()

    def put_url(self):
        for i in range(1, 10):
            self.queue.put(i)

    def get_url(self):
        while not self.queue.empty():
            uid = self.queue.get()
            item = {}
            space_source = requests.get(self.space_url.format(uid), headers={'User-Agent': UserAgent().random})
            try:
                space_json = space_source.json()
                if space_json.get('code') == 0:
                    contents = space_json.get('data')
                    # 用户id
                    item['mid'] = contents.get('mid', int(time.time()))
                    # 昵称
                    item['name'] = contents.get('name', 'Null')
                    # 性别
                    item['sex'] = contents.get('sex', 'Null')
                    # 头像
                    item['face'] = contents.get('face', 'Null')
                    # 签名
                    item['sign'] = contents.get('sign', 'Null')

                    item['rank'] = contents.get('rank', 0)
                    # vip等级
                    item['level'] = contents.get('level', 0)
                    # 注册时间
                    item['jointime'] = contents.get('jointime', 0)
                    # 生日
                    item['birthday'] = contents.get('birthday', 'Null')

                    item.update(self.get_relation(uid))
                    item.update(self.get_upstat(uid))
                    item.update(self.get_navnum(uid))

                    print(item)

            except Exception as e:
                print('一条数据获取出错{}'.format(e))

    def get_relation(self, uid):
        rel = {}
        try:
            relation_source = requests.get(self.relation_url.format(uid), headers={'User-Agent': UserAgent().random})
            relation_json = relation_source.json()
            # 关注数
            rel['following'] = relation_json['data'].get('following', 0)
            # 粉丝数
            rel['follower'] = relation_json['data'].get('follower', 0)
        except Exception as e:
            rel['following'] = 0
            # 粉丝数
            rel['follower'] = 0
        return rel

    def get_upstat(self, uid):
        upstat = {}
        try:
            up_source = requests.get(self.upstat_url.format(uid), headers={'User-Agent': UserAgent().random})
            up_json = up_source.json()
            # 播放数
            upstat['view'] = up_json['data']['archive'].get('view', 0)
            # 获赞数
            upstat['likes'] = up_json['data'].get('likes', 0)
        except Exception as e:
            upstat['view'] = 0
            upstat['view'] = 0
        return upstat

    def get_navnum(self, uid):
        navnum = {}
        try:
            nav_source = requests.get(self.navnum_url.format(uid), headers={'User-Agent': UserAgent().random})
            nav_json = nav_source.json()
            # TA的视频数量
            navnum['video'] = nav_json['data'].get('video', 0)
            # 订阅番剧
            navnum['bangumi'] = nav_json['data'].get('bangumi', 0)
            # TA的相簿
            navnum['album'] = nav_json['data'].get('album', 0)
            # 频道
            navnum['channel_master'] = nav_json['data']['channel'].get('master', 0)
            # 收藏
            navnum['favourite_master'] = nav_json['data']['favourite'].get('master', 0)
        except Exception as e:
            navnum['video'] = 0
            navnum['bangumi'] = 0
            navnum['album'] = 0
            navnum['channel_master'] = 0
            navnum['favourite_master'] = 0
        return navnum

    def main(self):
        put_th = Thread(target=self.put_url)
        get_th = Thread(target=self.get_url)

        put_th.start()
        time.sleep(1)
        get_th.start()

        put_th.join()
        get_th.join()


if __name__ == '__main__':
    bl = Bilibili()
    bl.main()


