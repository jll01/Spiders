import requests

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


def vivoapp(app_name, is_all_find):
    """
    vivo应用市场
    @param is_all_find:
    @param app_name: app的名称
    @return: 下载量、评分、公司名
    """
    if not app_name:
        raise Exception('请输入app的名称，不能为空！')

    url = f'https://search.appstore.vivo.com.cn/port/packages/?key={app_name}'
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
        response = s.get(url, headers=headers, verify=False, timeout=10).json()
        app_values = response.get('value', '')
        for app_value in app_values:
            app_name_1 = app_value['title_zh']
            if app_name_1.strip() != app_name and is_all_find:
                continue
            # 查找到的app
            item['app_name'] = app_name_1.strip()
            # 下载量
            item['download_num'] = str_int(app_value.get('download_count', '0'))
            # 评分
            item['score'] = app_value.get('score', 0)
            # 开发者
            item['developer'] = app_value.get('developer', 0)
            # 包名
            item['package_name'] = app_value.get('package_name', '')
            # 是否查找到
            item['is_find'] = 1
            return item
        return item
    except Exception as e:
        raise e


if __name__ == '__main__':
    print(vivoapp('QQ', False))
