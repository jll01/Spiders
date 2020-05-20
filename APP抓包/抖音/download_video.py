#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   download_video.py
# @Time    :   2020/5/20 10:45
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import re
import requests
import time

from fake_useragent import UserAgent


def get(share_url):
    """
    获取author, title, audioName, audios, videoName, videos
    """
    data = dict()
    headers = {
        'accept': 'application/json',
        'User-Agent': UserAgent().random
    }
    api = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={item_id}&dytk={dytk}"

    rep = requests.get(share_url, headers=headers, timeout=10)
    if not rep.ok:
        return {"msg": "获取失败"}
    html_text = rep.text

    item_id = re.findall(r'itemId: "(\d+)"', html_text)
    dytk = re.findall(r'dytk: "(.*?)"', html_text)
    if not item_id or not dytk:
        return {"msg": "获取失败"}
    item_id = item_id[0]
    dytk = dytk[0]

    rep = requests.get(api.format(item_id=item_id, dytk=dytk), headers=headers, timeout=6)
    if not rep.ok or not rep.json()["status_code"] == 0:
        return {"msg": "获取失败"}
    info = rep.json()["item_list"][0]

    data["author"] = info["author"]["nickname"]
    data["title"] = data["videoName"] = info["desc"]
    data["audioName"] = info["music"]["title"]
    data["audios"] = info["music"]["play_url"]["uri"]

    play_url = info["video"]["play_addr"]["url_list"][0].replace('playwm', 'play')

    rep = requests.get(play_url, headers=headers, allow_redirects=False, timeout=6)
    video_url = rep.headers.get('location', '')
    data["videos"] = video_url
    down_audio(data['audios'])
    down_video(data['videos'])

    print(data)


def down_audio(audio_url):
    audio = requests.get(audio_url, headers={'User-Agent': UserAgent().random}).content
    with open('{}.mp3'.format(int(time.time() * 1000)), 'wb') as f:
        f.write(audio)


def down_video(video_url):
    audio = requests.get(video_url, headers={'User-Agent': UserAgent().random}).content
    with open('{}.mp4'.format(int(time.time() * 1000)), 'wb') as f:
        f.write(audio)


if __name__ == "__main__":
    res = get(input('share url: '))
