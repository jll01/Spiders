import requests

from fake_useragent import UserAgent
from requests.packages import urllib3
from requests.adapters import HTTPAdapter


urllib3.disable_warnings()

# 请求失败的时候重试次数3
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def meizu(app_name, is_all_find):
    """
    魅族应用商店
    @param is_all_find:
    @param app_name:
    @return:
    """
    if not app_name:
        raise Exception('请输入app的名称，不能为空！')

    url = f'http://app.meizu.com/apps/public/search/page?cat_id=1&keyword={app_name}&start=0&max=18'
    headers = {
        'Host': 'app.meizu.com',
        # 'Referer': f'http://app.meizu.com/apps/public/search?keyword={app_name}',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': UserAgent(verify_ssl=False).random,
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
        response = s.get(url, headers=headers, timeout=3).json()
        datas = response.get('value').get('list')
        for data in datas:
            app_name_1 = data.get('name', '').replace(';', '').replace('&#x', '\\u').encode('utf-8').decode('unicode_escape')
            if app_name_1.strip() != app_name and is_all_find:
                continue
            # 搜索到的app名
            item['app_name'] = app_name_1.strip()
            # 开发者  unicode转中文
            item['developer'] = data.get('publisher', '').replace(';', '').replace('&#x', '\\u').encode('utf-8').decode('unicode_escape')
            # 下载量
            item['download_num'] = data.get('download_count', 0)
            # 评分
            item['score'] = round(data.get('star', 0)/10, 2)
            # 包名
            item['package_name'] = data.get('package_name', '')
            # 是否找到了
            item['is_find'] = 1
            return item
        return item
    except Exception as e:
        raise e


if __name__ == '__main__':
    print(meizu('微信', True))
