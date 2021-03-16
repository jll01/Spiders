import requests
import random
import time
import json
import urllib3
import pymongo
import pymysql


class QQMusic(object):
    def __init__(self):
        self.url = 'https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?g_tk=1638848441&hostUin=0&format=json&inCharset=utf8&outCharset=GB2312&notice=0&platform=yqq.json&needNewCode=0&cid=205360772&reqtype=2&biztype=1&topid=237773700&cmd=8&needmusiccrit=0&pagenum={}&pagesize=25&lasthotcommentid=&domain=qq.com&ct=24&cv=10101010'
        self.pagenum = 0
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
        }
        # mongo数据库
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client.python
        self.collection = self.db.qqmusic
        # mysql数据库
        self.connect = pymysql.connect(host='192.168.1.103',port=3306,user='root',passwd='0000',db='scrapytest')
        self.cur = self.connect.cursor()

    def request_comment(self):
        while True:
            json_comment = requests.get(self.url.format(self.pagenum), headers=self.headers, verify=False).text
            comments = json.loads(json_comment)
            try:
                commentlist = comments.get('comment','NULL').get('commentlist','NULL')
            except Exception as e:
                pass
            else:
                if commentlist != None:
                    for comment in commentlist:
                        item = {}
                        item['nick'] = comment.get('nick','Null')
                        item['praisenum'] = comment.get('praisenum',0)
                        item['content'] = comment.get('rootcommentcontent','Null')
                        item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(comment.get('time',int(time.time()))))
                        item['qq'] = eval(comment.get('uin','Null')) # QQ号
                        item['image'] = comment.get('avatarurl','Null')
                        try:
                            middlecomments = comment.get('middlecommentcontent','Null')
                            mid = []
                            for middlecomment in middlecomments:
                                item_mid = {}
                                item_mid['replyednick'] = middlecomment.get('replyednick','Null').replace('@','')
                                item_mid['replyeduin'] = eval(middlecomment.get('replyeduin','Null'))
                                item_mid['subcommentcontent'] = middlecomment.get('subcommentcontent','Null')

                                mid.append(item_mid)

                            item['middlecomments'] = str(mid)
                        except:
                            item['middlecomments'] = ''
                        finally:
                            print(item)
                            self.savecomment(item)
                    print('----------第{}页评论提取完成！----------'.format(self.pagenum+1))
                    time.sleep(random.uniform(2,3.5))
                    self.pagenum += 1
                else:
                    break

    def savecomment(self,item):
        # try:
        #     self.collection.insert_one(item)
        # except Exception as e:
        #     print('数据{}出错：{}'.format(item, e))
        try:
            self.cur.execute(
                '''insert into qqmusic (nick,praisenum,content,time,qq,image,middlecomments) values (%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['nick'],
                    item['praisenum'],
                    item['content'],
                    item['time'],
                    item['qq'],
                    item['image'],
                    item['middlecomments']
                )
            )
            self.connect.commit()
        except Exception as e:
            print('出错：{}'.format(e))


    def main(self):
        self.request_comment()


if __name__ == '__main__':
    urllib3.disable_warnings()

    qq = QQMusic()
    qq.main()
