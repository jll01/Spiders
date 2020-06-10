#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   xiaohongshu.py
# @Time    :   2020/5/31 11:27
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import json
import time
import os
import queue
import requests
import re
import random

from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from threading import Thread


class XiaoHongShu(object):
    def __init__(self):
        self.filepath = r'***\save_json'
        self.save_path = r'***\{}.mp4'
        self.save_json = r'***\xiaohongshu.json'
        self.queue = queue.Queue()
        self.pool = ThreadPoolExecutor(3)
        self.flag = True
        self.num = 0

    def read_json(self):
        while True:
            filenames = os.listdir(self.filepath)
            if len(filenames) != 0:
                for filename in filenames:
                    file = os.path.join(self.filepath, filename)
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            contents = json.loads(f.read())
                        os.remove(file)
                        print(f'{filename}获取成功！')
                        self.queue.put(contents)
                    except Exception as e:
                        print('出错了！{}'.format(e))

                self.flag = True
                self.num = 0
                time.sleep(1)
            else:
                print('{}目录暂时为空！等待中！'.format(self.filepath))
                self.flag = False
                self.num += 1
                time.sleep(3)

            if self.num == 3 and self.flag is False:
                print(f'{self.filepath}长时间为空, 已退出获取json数据！')
                break

    def get_data(self):
        f = open(self.save_json, 'a', encoding='utf-8')
        while True:
            if not self.queue.empty():
                get_data = self.queue.get()
                json_datas = get_data['data']
                if json_datas:
                    for data in json_datas:
                        item = dict()
                        # 分类
                        item['category_name'] = data['recommend'].get('category_name', '空')
                        # 类型
                        item['type'] = data.get('type', '空')
                        # 发布时间
                        item['timestamp'] = self.time2str(data.get('timestamp', int(time.time())))
                        # 标题
                        item['title'] = data.get('title', '空')
                        # 描述
                        item['desc'] = data.get('desc', '空')
                        # 喜欢人数
                        item['likes'] = data.get('likes', 0)
                        # 昵称
                        item['nickname'] = data['user'].get('nickname', '空')
                        # 头像
                        item['images'] = data['user'].get('images', '空')
                        # id
                        item['userid'] = data['user'].get('userid', '空')

                        if item['type'] == 'video':
                            # 视频分辨率
                            item['height'] = data['video_info'].get('height', 0)
                            item['width'] = data['video_info'].get('width', 0)
                            # 视频url
                            item['url'] = data['video_info'].get('url', '空')
                        else:
                            item['height'], item['width'], item['url'] = 0, 0, ''
                        print(item)
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')

                        self.pool.submit(self.download_video, item['url'])
            elif self.flag:
                time.sleep(random.uniform(3, 6))
            elif self.num == 3 and self.flag is False:
                print('数据为空！已退出信息获取！')
                break
        f.close()

    def download_video(self, url):
        if url:
            name = ''.join(re.findall(r'http:\/\/sns-video-qn\.xhscdn.com\/(.*)', url))
            print(f'{name}.mp4开始下载!')
            down = requests.get(url, headers={'User-Agent': UserAgent().random})
            if down.status_code == 200:

                with open(self.save_path.format(name), 'wb') as f:
                    f.write(down.content)
                print(f'{name}.mp4下载完成!')
            else:
                print(f'{name}.mp4下载失败!')

    @staticmethod
    def time2str(in_time):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(in_time))

    def main(self):
        t_read = Thread(target=self.read_json)
        t_read.start()
        time.sleep(2)

        t_get = Thread(target=self.get_data)
        t_get.start()

        t_read.join()
        t_get.join()


if __name__ == '__main__':

    xhs = XiaoHongShu()
    xhs.main()

