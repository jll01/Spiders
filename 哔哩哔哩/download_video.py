#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   download_video.py
# @Time    :   2020/5/17 15:42
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import re
import requests
import threading
import time
import random
import math
import urllib3
import json
import os

from fake_useragent import UserAgent


class BilibiliSpider(object):
    def __init__(self, keyword):
        # 搜索的up主昵称
        self.keyword = keyword
        # 搜索相关的up主
        self.input_keyword = '''https://api.bilibili.com/x/web-interface/search/type?search_type=bili_user&page={}&keyword={}'''
        # 获取相关up的页码增量
        self.page = 1
        # 保存每个up主的信息
        self.mid_list = []
        # 要下载视频的up主的id
        self.mid = ''
        # 获取输入up主id的所有视频
        self.up_all_video = '''https://api.bilibili.com/x/space/arc/search?mid={}&ps=30&pn={}'''
        # 要下载up主的视频数量
        self.video_num = 0
        # 下载保存视频的路径，路径不能有中文
        self.save_path = r'''E:\Study\bilibili'''
        # 获取视频数据的请求头
        self.dataHeaders = {
            'accept': '*/*',
            'accept-encoding': 'identity',
            'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6,zh-HK;q=0.5',
            'origin': 'https://www.bilibili.com',
            'range': 'bytes=0-169123900000000',
            'referer': 'https://www.bilibili.com/video/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': UserAgent().random,
        }

    def get_mid_uname(self):
        """
        获取与输入的up主相似的up主的相关信息：up主的is，昵称，视频数量，性别
        :return:
        """
        while True:
            headers = {
                'User-Agent': UserAgent().random
            }
            source = requests.get(self.input_keyword.format(self.page, self.keyword, headers=headers))
            try:
                page_source = source.json()
                contents = page_source['data'].get('result', 0)
                if contents != 0:
                    for content in contents:
                        mid_dict = dict()
                        # up主的id
                        mid_dict['mid'] = content['mid']
                        # 昵称
                        mid_dict['uname'] = content['uname']
                        # 视频数量
                        mid_dict['videos'] = content['videos']
                        # 性别
                        mid_dict['gender'] = self.male_num2str(content['gender'])

                        self.mid_list.append(mid_dict)

                    self.page += 1
                    time.sleep(random.uniform(0.5, 1))
                else:
                    break
            except Exception as e:
                pass
        print('查找完成！')

    def get_up_id(self):
        """
        及那个获取到与输入up主逆臣美国星官的up主信息全部输出，并获取要系啊在哪个up主的视频
        :return:
        """
        mid = 'up主id'
        uname = '昵称'
        gender = '性别'
        videos = '视频数量'
        print("{mid:<11}\t{uname:<{len1}}\t{gender:<{len2}}\t{videos:<10}".format(
            mid=mid, uname=uname, gender=gender, videos=videos, len1=self.pad_len(uname, 35), len2=self.pad_len(gender, 15)))

        # 所有相关up主的信息输出
        for item in self.mid_list:
            mid = item['mid']
            uname = item['uname']
            gender = item['gender']
            videos = item['videos']

            print("{mid:<15}\t{uname:<{len1}}\t{gender:<{len2}}\t{videos:<10}".format(
                mid=mid, uname=uname, gender=gender, videos=videos, len1=self.pad_len(uname, 35), len2=self.pad_len(gender, 15)))

        # 获取系啊在up主的id
        self.mid = input('请选择要下载视频的up主的id: ').strip()
        for con in self.mid_list:
            if con['mid'] == int(self.mid):
                self.video_num = int(con['videos'])

    def get_all_urls(self):
        """
        获取up主空间所有的视频id，并通过多线程获取下载
        :return:
        """
        for i in range(1, math.ceil(self.video_num/30)+1):
            headers = {
                'User-Agent': UserAgent().random,
            }
            try:
                html = requests.get(self.up_all_video.format(self.mid, i), headers=headers).json()
                vlist = html['data']['list']['vlist']
                if vlist:
                    for content in vlist:
                        # 视频url、音频url、视频名
                        videoUrl, audioUrl, name = self.get_url('''https://www.bilibili.com/video/{}'''.format(content['bvid']))
                        if videoUrl != 0:
                            # 获取的name中太多的特殊字符，重新命名视频名
                            n = str(int(time.time()*1000))
                            videoThread = threading.Thread(target=self.download_video, args=(videoUrl, n))
                            audioThread = threading.Thread(target=self.download_audio, args=(audioUrl, n))
                            videoThread.start()
                            audioThread.start()
                            videoThread.join()
                            audioThread.join()
                            # 将视音频合并到一个文件
                            self.merge_video_and_audio(n)
                        else:
                            print('获取第{}页失败'.format(i))
                else:
                    print('提取失败！')
            except Exception as e:
                print('获取第{}页失败{}'.format(i, e))

    def get_url(self, video_url):
        """
        请求视频播放页面，在源码中获取视音频链接和视频名称
        :return: 视频链接、音频链接、视频名称
        """
        try:
            htmlData = requests.get(video_url, headers=self.dataHeaders, verify=False).text
            # 视频数据
            urlData = json.loads(re.findall('<script>window.__playinfo__=(.*?)</script>', htmlData, re.M)[0])
            videoUrl = urlData['data']['dash']['video'][0]['baseUrl']
            audioUrl = urlData['data']['dash']['audio'][0]['baseUrl']
            name = re.findall('<h1 title="(.*?)" class="video-title">', htmlData, re.M)[0]
            return videoUrl, audioUrl, name
        except Exception as e:
            print('视频下载出错{}！'.format(e))
            return 0, 0, 0

    def download_video(self, videourl, name):
        """
        传入url和名称，开始下载
        :param videourl:    视频链接
        :param name:    视频名称
        :return:
        """
        videoContent = requests.get(videourl, headers=self.dataHeaders).content

        m4s_file = self.save_path + '\\' + '{}.m4s'.format(name)
        with open(m4s_file, 'wb') as f:
            f.write(videoContent)

        print('{}.m4s视频下载成功！'.format(name))

    def download_audio(self, audiourl, name):
        """
        传入url和名称，开始下载
        :param audiourl:    音频链接
        :param name:        音频名称
        :return:
        """
        audioContent = requests.get(audiourl, headers=self.dataHeaders).content
        mp3_file = self.save_path + '\\' + '{}.mp3'.format(name)
        with open(mp3_file, 'wb') as f:
            f.write(audioContent)

        print('{}.mp3音频下载成功！'.format(name))

    def merge_video_and_audio(self, video_name):
        """
        音视频合并函数，利用ffmpeg合并音视频
        :param video_name: 传入标题
        :return:
        """
        file_path = os.path.join(self.save_path, '{}')
        save_file_path = os.path.join(self.save_path, '{}_1.mp4'.format(video_name))

        command = r'''ffmpeg -i "{}.mp3" -i "{}.m4s" -c copy "{}"'''.format(file_path.format(video_name), file_path.format(video_name), save_file_path)
        os.popen(command)
        print(f'{video_name}.mp4合并完成！')

    def remove_file(self):
        files = os.listdir(self.save_path)
        for file in files:
            name, ext = os.path.splitext(file)
            if ext in ['.mp3', '.m4s']:
                os.remove(os.path.join(self.save_path, file))

    @staticmethod
    def pad_len(string, length):
        """
        print字符串对齐
        :param string:  字符串
        :param length:  对齐长度
        :return:    补齐的长度
        """
        return length - len(string.encode('GBK')) + len(string)

    @staticmethod
    def male_num2str(num):
        """
        性别转换
        :param num: 性别编码1、2、3
        :return: 转换后的性别 男、女、保密
        """
        if num == 1:
            return '男'
        elif num == 2:
            return '女'
        else:
            return '保密'

    def main(self):
        print('正在查询请稍后！')
        self.get_mid_uname()
        self.get_up_id()
        self.get_all_urls()
        self.remove_file()


if __name__ == '__main__':

    urllib3.disable_warnings()

    uname_input = input('请输入要下载的up主的昵称: ')
    spider = BilibiliSpider(uname_input)
    spider.main()
