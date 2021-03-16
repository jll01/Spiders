import requests
import time
import random
import pymysql

from queue import Queue
from fake_useragent import UserAgent
from threading import Thread, Lock


class HouLangComment(object):
    def __init__(self):
        self.url = '''https://api.bilibili.com/x/v2/reply?pn={}&type=1&oid=412935552&sort=2&_={}'''
        self.rep_comment_url = '''https://api.bilibili.com/x/v2/reply/reply?pn={}&type=1&oid=412935552&ps=10&root={}&_={}'''
        self.queue = Queue()
        self.replies_queue = Queue()
        self.flag = True
        self.replies_flag = True
        self.comment_num = 1
        self.lock = Lock()
        self.lock_rep = Lock()
        self.connect = pymysql.connect(host='localhost', user='root', password='0000', db='scrapytest', port=3306)
        self.cur = self.connect.cursor()

        self.connect_replies = pymysql.connect(host='localhost', user='root', password='0000', db='scrapytest', port=3306)
        self.cur_replies = self.connect_replies.cursor()

    def put_url(self):
        i = 1
        while True:
            try:
                source = requests.get(self.url.format(i, int(time.time()*1000)), headers={'User-Agent': UserAgent().random})
                json_source = source.json()
                replies = json_source['data']['replies']

                if isinstance(replies, list):
                    self.queue.put(replies)
                    print('第{}页评论添加成功！'.format(i))
                    i += 1
                else:
                    self.flag = False
                    break
            except Exception as e:
                print('一页数据获取失败！')

            time.sleep(random.uniform(0.8, 1.5))

    def get_url(self):
        while True:
            if not self.queue.empty():
                contents = self.queue.get()
                for content in contents:
                    item = dict()
                    # 评论id
                    item['rpid'] = content.get('rpid', 0)
                    # 用户id
                    item['mid'] = content.get('mid', 0)
                    # 返回时间戳
                    item['comment_date'] = self.time2date(content.get('ctime', 0))
                    # 点赞
                    item['likes'] = content.get('like', 0)
                    # 评论内容
                    item['content'] = content['content'].get('message', 'Null')
                    # 回复数
                    item['rcount'] = content.get('rcount', 0)
                    # 用户信息
                    user = content.get('member', 'Null')
                    if user != 'Null':
                        item['uname'] = user.get('uname', 'Null')
                        item['sex'] = user.get('sex', 'Null')
                        item['sign'] = user.get('sign', 'Null')
                        # 头像
                        item['avatar'] = user.get('avatar', 'Null')
                        item['ranks'] = user.get('rank', 'Null')
                        item['official_verify'] = user['official_verify'].get('desc', 'Null')
                        item['level_info'] = user['level_info'].get('current_level', 0)
                        item['viptodate'] = self.time2date(user['vip'].get('vipDueDate', 0))
                    else:
                        item['uname'], item['sex'], item['sign'], item['avatar'], item['rank'], item['official_verify'], item['level_info'], item['viptodate'] = '', '', '', '', '', '', '', ''

                    print('第{}条评论获取成功！'.format(self.comment_num))
                    self.comment_num += 1
                    self.save_comment(item)

                    if item['rcount'] > 0:
                        self.replies_queue.put(item['rpid'])

            elif self.flag:
                print('等待中..........')
                time.sleep(random.uniform(3, 6))
            else:
                self.replies_flag = False
                break

    def get_replies_comment(self):
        while True:
            if not self.replies_queue.empty():
                num = 1
                root_id = self.replies_queue.get()
                while True:
                    try:
                        source = requests.get(self.rep_comment_url.format(num, root_id, int(time.time() * 1000)), headers={'User-Agent': UserAgent().random})
                        json_source = source.json()
                        replies = json_source['data']['replies']
                        if isinstance(replies, list):
                            for content in replies:
                                item_com = dict()
                                # 评论id
                                item_com['rpid'] = content.get('rpid', 0)
                                # 用户id
                                item_com['mid'] = content.get('mid', 0)
                                # 回复评论的id
                                item_com['root_id'] = content.get('root', 0)
                                # 返回时间戳
                                item_com['comment_date'] = self.time2date(content.get('ctime', 0))
                                # 点赞
                                item_com['likes'] = content.get('like', 0)
                                # 评论内容
                                item_com['content'] = content['content'].get('message', 'Null')
                                # 回复数
                                item_com['rcount'] = content.get('rcount', 0)
                                # 用户信息
                                user = content.get('member', 'Null')
                                if user != 'Null':
                                    item_com['uname'] = user.get('uname', 'Null')
                                    item_com['sex'] = user.get('sex', 'Null')
                                    item_com['sign'] = user.get('sign', 'Null')
                                    # 头像
                                    item_com['avatar'] = user.get('avatar', 'Null')
                                    item_com['ranks'] = user.get('rank', 'Null')
                                    item_com['official_verify'] = user['official_verify'].get('desc', 'Null')
                                    item_com['level_info'] = user['level_info'].get('current_level', 0)
                                    item_com['viptodate'] = self.time2date(user['vip'].get('vipDueDate', 0))
                                else:
                                    item_com['uname'], item_com['sex'], item_com['sign'], item_com['avatar'], item_com['rank'], item_com['official_verify'], item_com['level_info'], item_com['viptodate'] = '', '', '', '', '', '', '', ''

                                self.save_comment_replies(item_com)
                            num += 1
                        else:
                            break
                    except Exception as e:
                        print('一条回复评论获取失败!-----')
                    time.sleep(random.uniform(0.5, 1.2))

            elif self.replies_flag:
                print('等待中..........')
                time.sleep(random.uniform(3, 6))
            else:
                break

    def save_comment(self, item):
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into bili_comment (rpid, mid, comment_date, likes, content, rcount, uname, sex, sign, avatar, ranks, official_verify, level_info, viptodate) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (
                    item['rpid'],
                    item['mid'],
                    item['comment_date'],
                    item['likes'],
                    item['content'],
                    item['rcount'],
                    item['uname'],
                    item['sex'],
                    item['sign'],
                    item['avatar'],
                    item['ranks'],
                    item['official_verify'],
                    item['level_info'],
                    item['viptodate']
                )
            )
            self.connect.commit()
            print('{}评论信息已经保存到数据库！'.format(item['rpid']))
        except Exception as e:
            print('{}出错{}'.format(item, e))
        self.lock.release()

    def save_comment_replies(self, item):
        self.lock_rep.acquire()
        try:
            self.cur_replies.execute(
                '''insert into bili_comment_replies (rpid, mid, root_id, comment_date, likes, content, rcount, uname, sex, sign, avatar, ranks, official_verify, level_info, viptodate) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (
                    item['rpid'],
                    item['mid'],
                    item['root_id'],
                    item['comment_date'],
                    item['likes'],
                    item['content'],
                    item['rcount'],
                    item['uname'],
                    item['sex'],
                    item['sign'],
                    item['avatar'],
                    item['ranks'],
                    item['official_verify'],
                    item['level_info'],
                    item['viptodate']
                )
            )
            self.connect_replies.commit()
            print('{}的{}评论信息已经保存到数据库！'.format(item['root_id'], item['rpid']))
        except Exception as e:
            print('{}出错{}'.format(item, e))
        self.lock_rep.release()

    @staticmethod
    def time2date(ctime):
        if len(str(ctime)) == 10:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime))
        elif len(str(ctime)) == 13:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime/1000))
        else:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def main(self):
        put_th = Thread(target=self.put_url)
        get_th = Thread(target=self.get_url)
        rep_th = Thread(target=self.get_replies_comment)

        put_th.start()
        time.sleep(1.3)
        get_th.start()
        time.sleep(4)
        rep_th.start()

        put_th.join()
        get_th.join()
        rep_th.join()


if __name__ == '__main__':
    hl = HouLangComment()
    hl.main()

