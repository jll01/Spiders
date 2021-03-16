import requests
import re
import json

from fake_useragent import UserAgent
from requests.packages import urllib3
from requests.adapters import HTTPAdapter


urllib3.disable_warnings()

# 请求失败的时候重试次数3
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def str_int(in_num):
    """
    str转int
    @param in_num: 需要转换的字符
    @return: 转换后的数字
    """
    try:
        if in_num:
            return eval(in_num)
        else:
            return 0
    except:
        return 0


def str2num(str_num):
    """
    正则 字符串格式的数字转换为数字
    @param str_num: 需要转换的数字
    @return: 转换后的数字
    """
    if str_num:
        try:
            return eval(str_num[0])
        except:
            return 0
    else:
        return 0


def huaweiapp(app_name, is_all_find):
    """
    华为应用市场app下载量和评分
    @param is_all_find:
    @param app_name: app名称
    @return: 下载量，评分(5分制，两位小数)
    """
    if not app_name:
        raise Exception('请输入app的名称，不能为空！')

    url = 'https://web-drcn.hispace.dbankcloud.cn/uowap/index?method=internal.completeSearchWord&serviceType=20&keyword={}&zone=&locale=zh_CN'
    rage_rating_url = 'https://web-drcn.hispace.dbankcloud.cn/uowap/index?method=internal.getTabDetail&serviceType=20&reqPageNum=1&maxResults=25&uri=app|{}&shareTo=&currentUrl=https://appgallery.huawei.com/#/app/{}&accessId=&appid={}&zone=&locale=zh_CN'
    headers = {
        'User-Agent': UserAgent(verify_ssl=False).random
    }
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
        response = s.get(url.format(app_name), headers=headers, verify=False, timeout=10).json()
        detail = response.get('app')
        app_name_1 = detail.get('name', '').strip()
        if is_all_find and app_name_1 != app_name:
            return item
        # 搜索到的app
        item['app_name'] = app_name_1
        # 下载量
        item['download_num'] = str_int(detail.get('downloads', '0'))
        # 包名
        item['package_name'] = detail.get('package', '')
        # 开发者
        item['developer'] = detail.get('developer', '')
        # 是否查找到了
        item['is_find'] = 1
        # 获取评分
        app_id = detail.get('id', '')
        response_rate = s.get(rage_rating_url.format(app_id, app_id, app_id), headers=headers, verify=False, timeout=10).json()
        res_con = json.dumps(response_rate, ensure_ascii=False).replace(' ', '')
        item['score'] = str2num(re.findall(r'["\']score["\']:["\'](.*?)["\'][,，]', res_con))
        return item
    except Exception as e:
        raise e


if __name__ == '__main__':
    print(huaweiapp('微信', True))
