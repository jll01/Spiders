import requests
import re
import tldextract

from urllib.parse import urlparse
from fake_useragent import UserAgent
from lxml import etree


def requests_url(index_url):
    """
    站长之家 获取icp和主体单位名称
    @param index_url: 域名
    @return: icp备案，公司名
    """
    # 正则匹配域名
    domain = tldextract.extract(index_url)
    # 请求url
    url = f'''http://icp.chinaz.com/{domain.domain}.{domain.suffix}'''
    re_url = f'http://icp.chinaz.com/home/info?host={domain.domain}.{domain.suffix}'
    headers = {
        'User-Agent': UserAgent(verify_ssl=False).random,
        'Host': 'icp.chinaz.com',
        'Referer': url,
    }
    try:
        response = requests.get(re_url, headers=headers, timeout=10)
        html = etree.HTML(response.content)
        company = html.xpath('//div[@class="icpMainBox"]/div[@class="tableBox"]/div[@class="ztInfo"]/p[3]/text()')
        icp = html.xpath('//div[@class="icpMainBox"]/div[@class="tableBox"]/div[@class="siteInfo"]/p[2]/text()')
        return_company_name = company[0].replace('--', '') if len(company) >= 1 else ''
        return_icp = icp[0].replace('--', '') if len(icp) >= 1 else ''
        return_data = {"icp": return_icp, "company_name": return_company_name}
    except Exception as e:
        print(f'站长之家获取ICP失败--->{index_url}--->{e}')
        return_data = {}

    return return_data


def aizhan_get_icp(index_url):
    """
    爱站网 获取icp备案和肢体公司名
    @param index_url: 域名
    @return: icp备案，公司名
    """
    # 正则匹配域名
    do_url = urlparse(index_url).netloc

    # 请求url
    url = f'https://www.aizhan.com/cha/{do_url}/'

    headers = {
        'User-Agent': UserAgent(verify_ssl=False).random,
        'Host': 'www.aizhan.com',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10).text
        return_icp = ''.join(re.findall(r'id=["\']icp_icp["\']>(.*?)</a>', response))
        return_company_name = ''.join(re.findall(r'id=["\']icp_company["\']>(.*?)</span>', response))
        return_data = {"icp": return_icp, "company_name": return_company_name}
    except Exception as e:
        print(f'爱站网获取ICP失败--->{index_url}--->{e}')
        return_data = {}

    return return_data


def toolfk(index_url):
    """
    在线工具人获取icp
    @param index_url:
    @return: icp,公司
    """
    do_url = urlparse(index_url).netloc
    url = f'http://www.toolfk.com/online-icp?query={do_url}'
    headers = {
        'Host': 'www.toolfk.com',
        'User-Agent': UserAgent(verify_ssl=False).random,
        'Referer': url,
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return_icp = ''.join(re.findall('备案许可证号</td>.*?<td>(.*?)</td>', response.text, re.DOTALL)).strip()
        return_company_name = ''.join(re.findall('主办单位名称</td>.*?<td>(.*?)</td>', response.text, re.DOTALL)).strip()
        return_data = {"icp": return_icp, "company_name": return_company_name}
    except Exception as e:
        print(f'在线工具人获取ICP失败--->{index_url}--->{e}')
        return_data = {}

    return return_data


def requests_url_zhanzhang(index_url):
    """
    站长之家 更新数据的接口
    @param index_url: 域名url
    @return: 获取到的数据
    """
    # 获取域名
    domain = tldextract.extract(index_url)
    headers = {
        'User-Agent': UserAgent(verify_ssl=False).random
    }
    url = 'http://icp.chinaz.com/home/up'
    # post请求数据
    data = {
        'kw': f'{domain.domain}.{domain.suffix}'
    }
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        con = response.json()
    except Exception as e:
        print(f'使用站长之家更新请求出错！---> {e}')
        return {}
    else:
        if con.get('code', 4) == 200:
            company_name = con['data'][0]['comName']
            icp = con['data'][0]['permit']
            return_data = {"icp": icp, "company_name": company_name}
            return return_data
        elif con.get('code', 5) == 0:
            requests_url_zhanzhang(index_url)
        else:
            return {}


def judge_return(in_return):
    """
    判断获取的icp是否满足条件
    @param in_return: 获取的返回值(icp和公司)
    @return: bool,满足为True
    """
    try:
        len_icp = len(in_return.get('icp'))
        if len_icp <= 10 or len_icp >= 25:
            return False
        else:
            return True
    except:
        return False


def main(index_url):
    """
    @param index_url: 域名
    @return: 获取到的数据
    """
    # 站长之家 满足条件直接返回
    return_info = requests_url(index_url)
    if judge_return(return_info):
        return return_info

    # 爱站网 满足条件直接返回
    return_info = aizhan_get_icp(index_url)
    if judge_return(return_info):
        return return_info

    # 工具人 满足条件直接返回
    return_info = toolfk(index_url)
    if judge_return(return_info):
        return return_info
    else:
        return {}


if __name__ == '__main__':
    print(requests_url('http://www.cscecst.com/'))
