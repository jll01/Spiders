import random
import requests
from Crypto.Cipher import AES
from binascii import hexlify
import json
import base64
import time
import os
import string
import re

from fake_useragent import UserAgent


class NetEasy(object):
    """
    先执行js中的a函数，生成16位随机字符串，然后执行两次AES加密(b函数)，然后执行RSA加密(c函数)
    """
    def __init__(self):
        self.search_url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        self.song_url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
        self.singer_name = input('输入歌手/歌曲名：')
        num = input('请输入要下载的数量，如若出错请减少下载数量：')
        self.text = json.dumps({"hlpretag": "<span class=s-fc7>", "hlposttag": "</span>", "s": self.singer_name, "type": "1", "offset": "0", "total": "true", "limit": num, "csrf_token": ""})

    @staticmethod
    def get_random_str():
        """
        获取16位随机字符(a-zA-Z0-9)，js中的a函数
        :return: 生成的16位随机字符串
        """
        return ''.join(random.sample(string.ascii_letters + string.digits, 16))

    @staticmethod
    def aes_encrypt(text, key):
        """
        AES加密，js中的b函数
        :param text: 要加密的密文
        :param key: 密钥
        :return: 加密后的结果
        """
        iv = b'0102030405060708'
        pad = 16 - len(text) % 16
        text = text + chr(2) * pad
        encryptor = AES.new(key.encode(), AES.MODE_CBC, iv)
        encryptor_str = encryptor.encrypt(text.encode())
        result_str = base64.b64encode(encryptor_str).decode()
        return result_str

    @staticmethod
    def rsa_encrypt(text):
        """
        RSA加密，js中的c函数
        :param text: 加密文本
        :return:
        """
        # js中的e
        pub_key = '010001'
        # js中的f
        modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        text = text[::-1]
        result = pow(int(hexlify(text.encode()), 16), int(pub_key, 16), int(modulus, 16))
        return format(result, 'x').zfill(131)

    def get_post_data(self, text, random_str):
        """
        获取加密的参数
        :param text: 加密的文本
        :param random_str: 16位随机字符串
        :return:
        """
        # key是固定的，相当于g
        params = self.aes_encrypt(self.aes_encrypt(text, key='0CoJUm6Qyw8W8jud'), random_str)
        encseckey = self.rsa_encrypt(random_str)
        return {'params': params, 'encSecKey': encseckey}

    @staticmethod
    def post_requests(url, data):
        """
        :param url: 请求url
        :param data: post请求的data数据
        :return: json格式的歌曲信息
        """
        headers = {
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': UserAgent(verify_ssl=False).random,
        }
        session = requests.Session()
        session.headers.update(headers)
        res = session.post(url, data=data)
        return res.json()

    def get_song_data(self, song_id, random_str):
        """
        获取歌曲的下载url
        :param song_id:
        :param random_str:
        :return:
        """
        # 'MD 128k': 128000, 'HD 320k': 320000
        text = {'ids': [song_id], 'br': 128000, 'csrf_token': ''}
        return self.get_post_data(json.dumps(text), random_str)

    def main(self):
        random_str = self.get_random_str()
        post_data = self.get_post_data(self.text, random_str)
        try:
            # 歌曲列表
            song_list = self.post_requests(self.search_url, post_data)
            songs = song_list['result']['songs']

            for song in songs:
                # 歌曲id
                song_id = song['id']
                # 歌曲名
                song_name = re.sub(r'[/|\?:"*<>]', '', song['name'])
                # 下载歌曲所需药的参数
                data_song = self.get_song_data(song_id, random_str)
                # 获取歌曲url
                song_urls = self.post_requests(self.song_url, data_song)
                song_url = song_urls['data'][0]['url']
                # 判断是否存在该歌手/歌曲保存的文件夹
                if not os.path.exists(self.singer_name):
                    # 新建文件夹
                    os.mkdir(self.singer_name)
                # 下载保存歌曲
                with open(self.singer_name + '/' + song_name + '.mp3', 'wb') as f:
                    try:
                        response = requests.get(song_url, timeout=10)
                    except Exception as e:  # 超时重新请求
                        print(f'歌曲 {song_name} 请求失败！不能下载vip！')
                    else:
                        print(f'歌曲 {song_name} {song_url}下载成功！')
                    f.write(response.content)

                time.sleep(random.uniform(1, 1.5))

        except Exception as e:
            print(f'出错了{e}')


if __name__ == '__main__':
    ne = NetEasy()
    ne.main()
