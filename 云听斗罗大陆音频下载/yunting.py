#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   yunting.py
# @Time    :   2020/6/25 9:24
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import os
import time
import random

from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from pydub import AudioSegment


def get_url():
    """
    获取每集的标题和对应的url
    :return:
    """
    item = dict()
    url = '''http://pacc.radio.cn/sharenew/ondemand?ondemandId=1382204&type=1&offset={}&limit=30'''
    offset = 1
    while offset < 18:
        datas = requests.get(url.format(offset), headers={'User-Agent': UserAgent(verify_ssl=False).random}, verify=False).json()
        contents = datas['progarms']
        for content in contents:
            name = content['name']
            down_url = content['streamsm4a']
            print(name, down_url)
            item[name] = down_url
        offset += 1
        time.sleep(random.uniform(1, 1.5))
    return item


def down(url, name):
    """
    下载音频
    :param url: 音频url
    :param name: 音频名称
    :return:
    """
    try:
        print(f'{name}开始保存！')
        path = os.path.join(file_path, f'{name}.m4a')
        name = re.sub(r'[\\/:?*"<>\n]', '', name)
        datas = requests.get(url, headers={'User-Agent': UserAgent(verify_ssl=False).random}, verify=False).content
        with open(path, 'wb') as f:
            f.write(datas)
        print(f'{name}下载成功！')
    except Exception as e:
        print(f'{name}保存失败！')


def process(file):
    """
    截取音频，从第15秒开始到除最后2分钟之间的音频
    :param file: 音频名称
    :return:
    """
    print(f'正在处理{file}')
    # 截取名称，1.mp3-->1
    save_name = os.path.splitext(file)[0]
    # 加载文件
    song = AudioSegment.from_file(os.path.join(file_path, file), format='m4a')
    # 截取音频，最后8秒分贝降低
    without = song[15*1000:-120*1000].fade_out(8000)
    # 保存mp3
    without.export(os.path.join(save_path, f'{save_name}.mp3'), format='mp3')
    print(f'{file}处理完成！保存为{save_name}.mp3')


if __name__ == '__main__':
    file_path = r'****'
    res = get_url()
    # 下载音频
    pool = ThreadPoolExecutor(3)
    for do_name, do_url in res.items():
        pool.submit(down, do_url, do_name)

    pool.shutdown(wait=True)
    # 处理音频
    pool_process = ThreadPoolExecutor(5)
    # path = r'E:\Study\项目\008面试\斗罗大陆'
    save_path = r'****'
    all_files = os.listdir(file_path)
    for in_file in all_files:
        pool_process.submit(process, in_file)

    pool_process.shutdown(wait=True)
