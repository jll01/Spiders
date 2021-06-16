import requests
import re
import getopt
import sys
import argparse

from Crypto.Cipher import AES


def m3u8():
    header = {
        'Host': 'encrypt-k-vod.xet.tech',
        'Origin': 'https://app5vfffdhz8371.pc.xiaoe-tech.com',
        'Referer': 'https://app5vfffdhz8371.pc.xiaoe-tech.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    }
    # requests得到m3u8文件内容
    content = requests.get(url, headers=header).text
    if "#EXTM3U" not in content:
        print("这不是一个m3u8的视频链接！")
        return False
    if "EXT-X-KEY" not in content:
        print("没有加密")
        return False

    # 使用re正则得到key和视频地址
    jiami = re.findall('#EXT-X-KEY:(.*)\n', content)
    key = re.findall('URI="(.*)"', jiami[0])
    vi = re.findall('IV=(.*)', jiami[0])[0]
    # 得到每一个ts视频链接
    tslist = re.findall('EXTINF:(.*),\n(.*)\n#', content)
    newlist = []
    for i in tslist:
        newlist.append(i[1])

    # 得到key的链接并请求得到加密的key值
    keyurl = key[0]
    header_key = {
        'Referer': 'https://app5vfffdhz8371.pc.xiaoe-tech.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    }
    keycontent = requests.get(keyurl, headers=header_key).content

    # 得到每一个完整视频的链接地址
    base_url = url.replace(url.split('/')[-1], '')
    tslisturl = []
    for i in newlist:
        tsurl = base_url + i
        tslisturl.append(tsurl)

    cryptor = AES.new(keycontent, AES.MODE_CBC, b'0000000000000000')
    header_url = {
        'Host': 'encrypt-k-vod.xet.tech',
        'Origin': 'https://app5vfffdhz8371.pc.xiaoe-tech.com',
        'Referer': 'https://app5vfffdhz8371.pc.xiaoe-tech.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    }
    with open(file_path, 'ab+') as f:
        # for循环获取视频文件
        for i in tslisturl:
            print(i)
            res = requests.get(i, headers=header_url)
            # 使用解密方法解密得到的视频文件
            cont = cryptor.decrypt(res.content)
            # 以追加的形式保存为mp4文件，mp4可以随意命名，这里命名为小鹅通视频下载测试
            f.write(cont)
    return True


def get_args():
    parser = argparse.ArgumentParser(description="download m3u8 from xiaoetong", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", type=str, required=True, help="video name")
    parser.add_argument("-u", type=str, required=True, help="video url")
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()
    file_path = args.n
    url = args.u
    pd = m3u8()
    if pd:
        print('视频下载完成！')
    else:
        print('请检查输入的参数')
