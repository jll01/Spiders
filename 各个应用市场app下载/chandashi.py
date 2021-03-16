import requests

from fake_useragent import UserAgent
from requests.packages import urllib3
from requests.adapters import HTTPAdapter
from lxml import etree


urllib3.disable_warnings()

# 请求失败的时候重试次数3
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def judge_num(in_num):
    """
    判断返回数字
    @param in_num: 字符串格式的数字
    @return:
    """
    in_num = in_num.strip()
    try:
        return eval(in_num)
    except:
        return 0


def get_app_detail(app_id):
    """
    获取下载量和评分
    @param app_id: app对应的id
    @return: 评分和下载量、公司名
    """
    url = app_id
    headers = {
        'User-Agent': UserAgent(verify_ssl=False).random,
        'Host': 'www.chandashi.com',
    }
    try:
        res = s.get(url, headers=headers, verify=False, timeout=10)
        html = etree.HTML(res.text)
        # 下载量
        down_num = html.xpath('//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div[4]/div[2]/text()')
        down_num = down_num[0] if len(down_num) >= 1 else '0'
        down_num = judge_num(down_num.strip().replace(',', ''))
        # 评分
        score_all = html.xpath('//*[@id="main-content"]/div/div[1]/div/table/tbody/tr')
        score_list = []
        for i in score_all:
            score = i.xpath('./td[2]/text()')
            score = score[0] if len(score) >= 1 else '0'
            score_list.append(judge_num(score))
        return round(sum(score_list)/len(score_list), 2), down_num
    except:
        return 0, 0


def get_app_id(app_name, is_all_find):
    """
    禅大师
    @param is_all_find:
    @param app_name:app名称
    @return:评分、下载量、公司名
    """
    if not app_name:
        raise Exception('请输入app的名称，不能为空！')
    # 华为
    url_huawei = f"https://www.chandashi.com/interf/v1/Androidsearch/indexPC?country=cn&keyword={app_name}&market=huawei&from=input&page=1&pageSize=10"
    # vivo
    url_vivo = f"https://www.chandashi.com/interf/v1/Androidsearch/indexPC?country=cn&keyword={app_name}&market=vivo&from=input&page=1&pageSize=10"
    # oppo
    url_oppo = f"https://www.chandashi.com/interf/v1/Androidsearch/indexPC?country=cn&keyword={app_name}&market=oppo&from=input&page=1&pageSize=10"
    # 应用宝
    url_yongyongbao = f"https://www.chandashi.com/new/search/android?keyword={app_name}&country=cn&market=yingyongbao&from=input"
    # 小米
    url_xiaomi = f'https://www.chandashi.com/new/search/android?keyword={app_name}&country=cn&market=xiaomi&from=input'
    urls = [url_huawei, url_vivo, url_oppo, url_yongyongbao, url_xiaomi]
    huawei_detail = 'https://www.chandashi.com/android/review/appId/{}/market/huawei/country/cn.html'
    vivo_detail = 'https://www.chandashi.com/android/review/appId/{}/market/vivo/country/cn.html'
    oppo_detail = 'https://www.chandashi.com/android/review/appId/{}/market/oppo/country/cn.html'
    yingyongbao_detail = 'https://www.chandashi.com/android/review/appId/{}/market/yingyongbao/country/cn.html'
    xiaomi_detail = 'https://www.chandashi.com/android/review/appId/{}/market/xiaomi/country/cn.html'
    last_urls = [huawei_detail, vivo_detail, oppo_detail, yingyongbao_detail, xiaomi_detail]
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
    for url_j in urls:
        try:
            response = s.get(url_j, headers=headers).json()
            res_list = response.get('data', {'list': []}).get('list', [{}])
            for i in res_list:
                app_name_get = i.get('trackName', '')
                get_company_name = i.get('sellerName', '')
                if app_name != app_name_get.strip() and is_all_find:
                    continue
                last_url = last_urls[urls.index(url_j)].format(i['trackId'])
                # 包名
                item['package_name'] = i.get('packageName', '')
                # 评分，下载量
                item['score'], item['download_num'] = get_app_detail(last_url)
                # 开发者
                item['developer'] = get_company_name
                # 搜索到的app名
                item['app_name'] = app_name_get.strip()
                # 是否查找到了
                item['is_find'] = 1
                return item
            return item
        except Exception as e:
            raise e


if __name__ == '__main__':
    print(get_app_id('QQ', False))
