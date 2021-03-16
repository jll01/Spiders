import requests
import urllib3
import json
import math

from proj.tasks import get_content


class qqmusic(object):
    """
    QQ音乐爬虫
    """
    def __init__(self):
        self.url = 'https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?g_tk=1638848441&hostUin=0&format=json&inCharset=utf8&outCharset=GB2312&notice=0&platform=yqq.json&needNewCode=0&cid=205360772&reqtype=2&biztype=1&topid=237773700&cmd=8&needmusiccrit=0&pagenum={}&pagesize=25&lasthotcommentid=&domain=qq.com&ct=24&cv=10101010'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
        }
        self.pagenum = 0
        # 存储分类的url
        self.savestarturl = []

    def startrequests(self):
        """
        获取起始页分类的链接和名称
        """
        json_comment = requests.get(self.url.format(self.pagenum), headers=self.headers, verify=False).text
        comments = json.loads(json_comment)

        commenttotal = comments.get('comment', 'NULL').get('commenttotal', 0)
        num = math.ceil(commenttotal/25)

        # num = 10
        for i in range(num):
            self.savestarturl.append(self.url.format(i))

        get_content.delay(self.savestarturl)

    def main(self):
        self.startrequests()
        print('url请求完成！')


if __name__ == '__main__':

    urllib3.disable_warnings()

    qq = qqmusic()
    qq.main()
