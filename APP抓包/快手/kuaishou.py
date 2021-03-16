import os
import time
import requests
import json
import urllib3

from threading import Thread


class KuaiShou(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'kwai-android',
        }
        # 视频保存路径
        self.pathinfo = r'****'
        self.video_url = 'http://api.gifshow.com/rest/n/feed/hot?app=0&kpf=ANDROID_PHONE&ver=6.5&c=HUAWEI&mod=HUAWEI%28KNT-AL20%29&appver=6.5.4.9545&ftt=&isp=CMCC&kpn=KUAISHOU&lon=0&language=zh-cn&' \
                         'sys=ANDROID_8.0.0&max_memory=384&ud=0&country_code=cn&pm_tag=&oc=HUAWEI&hotfix_ver=&did_gt=1561381139167&iuid=&extId=685bd7481b876399c5868b403f8d2e24&net=WIFI&did=ANDROID_c9eaefd0e95832b1&lat=0&type=7&page=1&coldStart=false&count=20&pv=false&id=8&refreshTimes=6&pcursor=&source=1&needInterestTag=false&browseType=1&seid=363afc3f-4733-4e85-8d82-f85847d3b86d&volume=0.0&os=android&sig=2bc3095c94eb47c0169dcbe93ad9b40e&client_key=3c2cd3f3'
        # 保存视频下载url
        self.video_downurl = []

    def get_info(self):
        for i in range(10):
            res = requests.get(self.video_url, headers=self.headers).text
            contents = json.loads(res).get('feeds', 'None')
            if contents != 'None':
                for content in contents:
                    con = dict()
                    con['user_id'] = content.get('user_id')
                    con['user_name'] = content.get('user_name')
                    con['comment_count'] = content.get('comment_count')
                    con['view_count'] = content.get('view_count')
                    if content.get('user_sex') == 'F':
                        con['user_sex'] = '女'
                    else:
                        con['user_sex'] = '男'
                    con['time'] = content.get('time')
                    down_url = content.get('main_mv_urls', 'None')
                    if down_url != 'None':
                        con['download'] = down_url[0].get('url','None')
                        t = Thread(target=self.down_video,args=(con['user_id'],con['download']))
                        t.start()
                        t.join()
                    else:
                        con['download'] = ''
                    self.save_info(con)
            else:
                break

    @staticmethod
    def save_info(con):
        """
        视频信息保存到json文件中
        :param con: 要保存的信息
        """
        with open('kuaishouapp.json', 'a+', encoding='utf-8') as f:
            f.write(json.dumps(con, ensure_ascii=False) + '\n')

    def down_video(self, userid, downurl):
        """
        下载视频
        :param userid: 用户id
        :param downurl: 下载url
        """
        video = requests.get(downurl, headers=self.headers, verify=False, stream=True)
        temp_size = 0
        name = str(userid) + '_' + str(int(time.time()*1000)) + '.mp4'
        with open(os.path.join(self.pathinfo, name), 'wb') as file:
            for chunk in video.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    file.write(chunk)
                    # 刷新缓存
                    file.flush()
            print("%s下载完成！" % name)

    def main(self):
        self.get_info()


if __name__ == '__main__':
    urllib3.disable_warnings()

    ks = KuaiShou()
    ks.main()
