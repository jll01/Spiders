import requests
import json
import re

from fake_useragent import UserAgent
from requests.packages import urllib3
from requests.adapters import HTTPAdapter


urllib3.disable_warnings()

# 请求失败的时候重试次数3
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def market10086(app_name, is_all_find):
    """
    中国移动10086应用商城
    @param is_all_find:
    @param app_name: app名称
    @return: 下载量、评分、公司名
    """
    if not app_name:
        raise Exception('请输入app的名称，不能为空！')

    item = {
        # 搜索的app名
        'search_app_name': app_name,
        # 查找到的app
        'app_name': '',
        # 下载量
        'download_num': 0,
        # 评分
        'score': 0,
        # 开发者
        'developer': '',
        # 包名
        'package_name': '',
        # 是否查找到了
        'is_find': 0
    }
    try:
        url_get_id = 'http://mm.10086.mmarket.com/mm_maap/maap/search.do'
        data_get_id = {
            'currentPage': '1',
            'keyword': app_name,
        }
        user_agent = UserAgent(verify_ssl=False).random
        headers = {
            'User-Agent': user_agent,
            'Content-Type': 'application/json;charset=UTF-8',
            'Host': 'mm.10086.mmarket.com',
            'Origin': 'http://mm.10086.mmarket.com',
            'Referer': 'http://mm.10086.mmarket.com/maap/',
        }
        response = s.post(url_get_id, data=json.dumps(data_get_id), headers=headers).json()
        # detail = response.get('data').get('blocks')[0]
        details = response.get('data').get('blocks')
        for detail in details:
            key_id = detail['contentId']
            app_name_1 = detail['title']
            if app_name_1.strip() != app_name and is_all_find:
                continue
            detail_url = 'http://mm.10086.mmarket.com/mm_maap/maap/getAppDetail.do'
            data_detail = {
                'goodsid': key_id
            }
            headers = {
                'User-Agent': user_agent,
                'Content-Type': 'application/json',
                'Host': 'mm.10086.mmarket.com',
                'Origin': 'http://mm.10086.mmarket.com',
                'Referer': 'http://mm.10086.mmarket.com/maap/',
                'ua': 'android-24-1080x2040-RNE-AL00',
                'appname': 'MM7.3.2.001.01_CTAndroid_JT',
            }
            response_detail = s.post(detail_url, data=json.dumps(data_detail), headers=headers).json()
            data = response_detail.get('data')

            item['score'] = round(data.get('score', 0), 2)
            item['developer'] = data.get('provider', '')
            item['package_name'] = data.get('appUid', '')

            app_down_count = data.get('interested', '')
            app_down_count_re = re.findall(r'\d+', app_down_count)
            app_down_count_1 = app_down_count_re[0] if len(app_down_count_re) >= 1 else 0
            if '万' in app_down_count:
                app_down_count = eval(app_down_count_1) * 10000
            else:
                app_down_count = eval(app_down_count)
            item['download_num'] = app_down_count
            item['app_name'] = app_name_1.strip()
            item['is_find'] = 1
            return item
        return item
    except Exception as e:
        raise e


if __name__ == '__main__':
    print(market10086('QQ', True))
