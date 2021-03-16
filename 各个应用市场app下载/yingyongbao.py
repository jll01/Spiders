import requests

from fake_useragent import UserAgent
from requests.packages import urllib3
from requests.adapters import HTTPAdapter


urllib3.disable_warnings()

# 请求失败的时候重试次数3
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def yingyongbao(app_name, is_all_find):
    """
    应用宝app下载量和评分
    @param is_all_find: 是否完全匹配名称
    @param app_name: app名称
    @return: 下载量，评分(5分制，两位小数)
    """
    if not app_name:
        raise Exception('请输入app的名称，不能为空！')

    url = 'https://sj.qq.com/myapp/searchAjax.htm'
    data = {
        'kw': app_name,
        'pns': '',
        'sid': '',
    }
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
        response = s.post(url, data=data, headers=headers, verify=False, timeout=10).json()
        details = response.get('obj').get('items')
        for i in details:
            detail = i.get('appDetail', '')
            app_name_1 = detail.get('appName', '')
            if is_all_find and app_name_1.strip() != app_name:
                # 只有名称一样的时候才返回数据
                # if app_name_1.strip() != app_name:
                continue
            # 查找到的app名称
            item['app_name'] = app_name_1.strip()
            # 下载量
            item['download_num'] = detail.get('appDownCount', 0)
            # 主体名
            item['developer'] = detail.get('authorName', '')
            # 评分
            item['score'] = round(detail.get('averageRating', 0), 2)
            # 包名
            item['package_name'] = detail.get('pkgName', '')
            # 是否查找成功
            item['is_find'] = 1
            return item
        return item
    except Exception as e:
        raise e


if __name__ == '__main__':
    print(yingyongbao('QQ', False))
