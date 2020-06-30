#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   danmu.py
# @Time    :   2020/6/22 19:18
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import time
import random
import json
import urllib3
import pymysql

from fake_useragent import UserAgent
from lxml import etree


class TencentDanmu(object):
    def __init__(self):
        # 获取弹幕url
        self.danmu_url = '''https://mfm.video.qq.com/danmu?target_id={}&timestamp={}'''
        # 弹幕增量
        self.offset = 0
        # 获取每集视频的id
        self.get_id_url = '''https://v.qq.com/x/cover/m441e3rjq9kwpsc.html'''
        # 获取每集的target_id
        self.target_id_url = '''https://access.video.qq.com/danmu_manage/regist?vappid=97767206&vsecret=c0bdcbae120669fff425d0ef853674614aa659c605a613a4&raw=1'''
        # 存储target_id
        self.target_id = []
        # 连接mysql
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='spiderdb')
        self.cur = self.connect.cursor()

    def get_id(self):
        """
        获取每集视频的id
        :return:
        """
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        res = requests.get(self.get_id_url, headers=headers, verify=False).text
        html = etree.HTML(res)
        # 每集的id
        ids = html.xpath('//div[@id="video_scroll_wrap"]//div[@class="mod_episode"]/span/@id')
        return ids

    def get_target_id(self):
        """
        获取target_id
        :return:
        """
        print('请稍后！正在获取参数！')
        # 首先获取每集的id
        all_ids = self.get_id()
        for vid in all_ids:
            headers = {
                'User-Agent': UserAgent(verify_ssl=False).random,
                'cookie': 'RK=AE5Bw8Zyb0; ptcz=094dd7bc3fe1766ee24dfcd3458f8e1cc65d092a5fbc5975f04fcfc52a097e2b; tvfe_boss_uuid=ec12aebe4bbbaafa; video_platform=2; video_guid=16710a5e0f705259; pgv_pvid=7158771600; o_cookie=491692391; pac_uid=1_491692391; XWINDEXGREY=0; iip=0; pgv_pvi=4883317760; pgv_info=ssid=s5794474470',
            }
            # post请求data
            post_data = {
                "wRegistType": 2,
                "vecIdList": [vid],
                "wSpeSource": 0,
                "bIsGetUserCfg": 1,
                "mapExtData": {
                    "m00253deqqo": {
                        "strCid": "m441e3rjq9kwpsc",
                        "strLid": ""
                    }
                }
            }
            try:
                resp = requests.post(self.target_id_url, headers=headers, data=json.dumps(post_data), verify=False).text
                # 正则匹配targetid
                target_id = ''.join(re.findall(r'targetid=(\d+)', resp, re.DOTALL))
                self.target_id.append(target_id)

                time.sleep(random.uniform(0.5, 1))
            except Exception as e:
                print('target_id获取失败')

        print('参数获取完成！')
        # print(self.target_id)

    def get_danmu(self):
        """
        获取弹幕
        :return:
        """
        # 循环获取每集的弹幕
        for targetid in self.target_id:
            print(f'{targetid}弹幕开始下载！')
            while True:
                headers = {
                    'User-Agent': UserAgent(verify_ssl=False).random,
                }
                try:
                    danmu_text = requests.get(self.danmu_url.format(targetid, self.offset), headers=headers, verify=False).text
                    danmu = json.loads(danmu_text, strict=False)
                    # 有弹幕的时候
                    if danmu['count'] != 0:
                        comments = danmu['comments']
                        for comment in comments:
                            item = dict()
                            # target_id
                            item['target_id'] = targetid
                            # 弹幕id、
                            item['commentid'] = comment['commentid']
                            # 弹幕内容
                            item['content'] = comment['content']
                            # 点赞
                            item['liked'] = comment['upcount']
                            # 发布者
                            item['nickname'] = comment['opername']
                            # 出现的时间点
                            item['timepoint'] = comment['timepoint']
                            # 发布者的头像
                            item['headurl'] = comment['headurl']

                            print(item)
                            self.save_con(item)
                            self.save_mysql(item)
                        self.offset += 30
                        time.sleep(random.uniform(0.5, 1.2))
                    else:
                        break
                except Exception as e:
                    print(f'{targetid}请求出错！{e}')

            print(f'{targetid}弹幕下载完成！')
            time.sleep(random.uniform(1, 1.5))
            # 每当一集获取完成后增量重置为0
            self.offset = 0

    @staticmethod
    def save_con(item):
        """
        保存到本地json中
        :param item: 要保存的内容
        :return:
        """
        with open('弹幕.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def save_mysql(self, item):
        """
        保存到mysql数据库
        :param item: 保存的弹幕
        :return:
        """
        try:
            self.cur.execute(
                """insert into tencent_danmu (target_id, commentid, content, liked, nickname, timepoint, headurl) values (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    item['target_id'],
                    item['commentid'],
                    item['content'],
                    item['liked'],
                    item['nickname'],
                    item['timepoint'],
                    item['headurl'],
                )
            )
            self.connect.commit()
        except Exception as e:
            print(f'{item}出错了{e}')

    def main(self):
        self.get_target_id()
        # targetid获取成功
        if self.target_id:
            self.get_danmu()
        else:
            print('请检查程序后再重新运行！')


if __name__ == '__main__':
    urllib3.disable_warnings()

    dm = TencentDanmu()
    dm.main()
