import requests
import time
import hashlib
import json
import base64
import aircv as ac
import tldextract
import cv2
import numpy as np

from fake_useragent import UserAgent
from requests.packages import urllib3
from requests.adapters import HTTPAdapter


urllib3.disable_warnings()
s = requests.Session()
s.keep_alive = False
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def get_token():
    """
    获取所需的请求参数 token
    @return: token值
    """
    # 请求url
    token_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth'
    timestamp = int(time.time()*1000)
    authkey = hashlib.md5(f'testtest{timestamp}'.encode('utf-8')).hexdigest()
    data_token = {
        "authKey": authkey,
        "timeStamp": timestamp
    }

    headers = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Origin': 'https://beian.miit.gov.cn',
        'Referer': 'https://beian.miit.gov.cn/',
        'User-Agent': UserAgent(verify_ssl=False).random,
    }
    token = ''
    try:
        token_response = s.post(token_url, headers=headers, data=data_token, timeout=10, verify=False).json()
        token = token_response.get('params').get('bussiness')
    except:
        pass
    return token


def get_img(in_token):
    """
    获取滑动验证的图片并计算需要滑动的距离
    @param in_token: token值
    @return: 下一步所需参数uuid、滑动距离
    """
    get_big_img = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage'
    headers_img = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Origin': 'https://beian.miit.gov.cn',
        'Referer': 'https://beian.miit.gov.cn/',
        'User-Agent': UserAgent(verify_ssl=False).random,
        'token': in_token,
    }
    try:
        img_response = s.post(get_big_img, headers=headers_img, timeout=10, verify=False).json()
        big_img = img_response.get('params').get('bigImage')
        small_image = img_response.get('params').get('smallImage')
        uuid = img_response.get('params').get('uuid')
        # 保存背景图
        big_data = base64.b64decode(big_img)
        img_array = np.frombuffer(big_data, np.uint8)
        # 转换成opencv可用格式
        im_bg_img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)

        # 保存滑动的小图
        small_data = base64.b64decode(small_image)
        img_array = np.frombuffer(small_data, np.uint8)
        # 转换成opencv可用格式
        im_small_img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)

        # 计算距离
        pos = ac.find_template(im_bg_img, im_small_img, threshold=0.001)
        rec = pos['rectangle']
        dis = rec[0][0]
        if not dis:
            dis = 0
    except:
        uuid, dis = '', 0

    return uuid, dis


def check_img(in_token, in_uuid, in_dis):
    """
    判断计算的滑动距离是否正确
    @param in_token: 第一步 token值
    @param in_uuid: 第二步 uuid
    @param in_dis: 滑动距离
    @return: 下一步所需参数
    """
    check_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage'
    headers_check = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Origin': 'https://beian.miit.gov.cn',
        'Referer': 'https://beian.miit.gov.cn/',
        'User-Agent': UserAgent(verify_ssl=False).random,
        'token': in_token,
        'Content-Type': 'application/json',
    }
    data_check = {
        'key': in_uuid,
        'value': in_dis,
    }
    try:
        check_response = requests.post(check_url, headers=headers_check, data=json.dumps(data_check), timeout=10, verify=False).json()
        sign = check_response.get('params')
    except:
        sign = ''

    return sign


def get_info(in_token, in_sign, in_domain):
    """
    获取当前域名对应的icp
    @param in_token: 第一步 token值
    @param in_sign: 第三步 sign值
    @param in_domain: 需要查找的域名
    @return: icp、主体单位名
    """
    last_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition'
    headers_last = {
        'Host': 'hlwicpfwc.miit.gov.cn',
        'Origin': 'https://beian.miit.gov.cn',
        'Referer': 'https://beian.miit.gov.cn/',
        'User-Agent': UserAgent(verify_ssl=False).random,
        'token': in_token,
        'Content-Type': 'application/json',
        'sign': in_sign
    }
    last_data = {
        "pageNum": "",
        "pageSize": "",
        "unitName": in_domain
    }
    try:
        last_response = requests.post(last_url, headers=headers_last, data=json.dumps(last_data), timeout=10, verify=False).json()
        last = last_response.get('params').get('list')[0]
        icp = last.get('serviceLicence', '')
        company_name = last.get('unitName', '')
        item = {
            'icp': icp,
            'company_name': company_name
        }
    except Exception as e:
        print(e)
        item = {}

    return item


def main(domain):
    token = get_token()
    uuid, dis = get_img(token)
    sign = check_img(token, uuid, dis)
    # 提取满足查找条件的域名 https://www.baidu.com/--->baidu.com
    get_domain = tldextract.extract(domain)
    domain = f'{get_domain.domain}.{get_domain.suffix}'
    result = get_info(token, sign, domain)
    return result


if __name__ == '__main__':
    print(main('http://www.jd.com/'))
