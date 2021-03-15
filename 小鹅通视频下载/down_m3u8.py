import requests
import re
import getopt
import sys

from Crypto.Cipher import AES


def m3u8():
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
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
    keycontent = requests.get(keyurl, headers=header).content

    # 得到每一个完整视频的链接地址
    base_url = url.replace(url.split('/')[-1], '')
    tslisturl = []
    for i in newlist:
        tsurl = base_url + i
        tslisturl.append(tsurl)

    cryptor = AES.new(keycontent, AES.MODE_CBC, b'0000000000000000')

    # for循环获取视频文件
    for i in tslisturl:
        print(i)
        res = requests.get(i, header)
        # 使用解密方法解密得到的视频文件
        cont = cryptor.decrypt(res.content)
        # 以追加的形式保存为mp4文件，mp4可以随意命名，这里命名为小鹅通视频下载测试
        with open(file_path, 'ab+') as f:
            f.write(cont)
    return True


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "u:n:", ["url=", "name="])
    url = ''
    file_path = ''
    for opt, arg in opts:
        if opt in ("-u", "--url"):
            url = arg
        elif opt in ("-n", "--name"):
            file_path = arg
    if url and file_path:
        pd = m3u8()
        if pd:
            print('视频下载完成！')
    else:
        print('请检查输入的参数')
