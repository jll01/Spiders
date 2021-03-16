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


def baidumobileapp(app_name, is_all_find):
    """
    百度手机助手app下载量和评分下载
    @param is_all_find: 是否全名匹配
    @param app_name: app名称
    @return: 下载量，评分(5分制，两位小数)
    """
    if not app_name:
        raise Exception('请输入app的名称，不能为空！')

    url = 'https://appc.baidu.com/mosug?type=app&source=mobile&wd={}'
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
        # 包名
        'package_name': '',
        # 是否查找到了
        'is_find': 0
    }
    try:
        response = s.get(url.format(app_name), headers=headers, verify=False, timeout=10).json()
        details = response.get('result').get('s')
        for detail in details:
            app_name_1 = detail.get('title', '')
            if is_all_find and app_name_1.strip() != app_name:
                continue
            # 搜索到的app名称
            item['app_name'] = app_name_1.strip()
            # 下载量
            item['download_num'] = detail.get('download_num', 0)
            # 评分
            item['score'] = round(str_int(detail.get('score', '0'))/20, 2)
            # 包名
            item['package_name'] = detail.get('package', '')
            # 是否查到了
            item['is_find'] = 1
            return item
        return item
    except Exception as e:
        raise e


if __name__ == '__main__':
    print(baidumobileapp('QQ', True))
