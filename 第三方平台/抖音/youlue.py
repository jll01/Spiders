import requests
import random
import hashlib
import time
import datetime
import os
import string

from fake_useragent import UserAgent
from requests.packages import urllib3
from dateutil.relativedelta import relativedelta


urllib3.disable_warnings()


def get_six_str():
    """
    获取随机的六位字符
    @return: 6位字符
    """
    get_random_str = string.digits + string.ascii_letters
    six_str = ''.join(random.sample(get_random_str, 6))
    return six_str


def get_machine_str():
    """
    获取machine
    @return:
    """
    get_random_str = string.digits + string.ascii_lowercase
    machine_1 = ''.join(random.sample(get_random_str, 8))
    machine_2 = ''.join(random.sample(get_random_str, 4))
    machine_3 = ''.join(random.sample(get_random_str, 3))
    machine_4 = ''.join(random.sample(get_random_str, 4))
    machine_5 = ''.join(random.sample(get_random_str, 12))
    machine = f'{machine_1}-{machine_2}-4{machine_3}-{machine_4}-{machine_5}'
    return machine


def get_now_time():
    """
    获取现在的时间戳(10位)
    @return: 10位时间戳
    """
    now_time = int(time.time())
    return now_time


def now_last_month():
    """
    获取今天日期和一月前日期对应的10位时间戳
    @return: 现在的时间戳、上一个月的时间戳
    """
    # 现在的
    today_date = datetime.datetime.today()
    now_date = int(time.mktime((today_date.year, today_date.month, today_date.day, 23, 59, 59, 0, 0, 0)))
    # 一月前的
    last_month = today_date - relativedelta(months=1)
    last_date = int(time.mktime((last_month.year, last_month.month, last_month.day, 0, 0, 0, 0, 0, 0)))

    return now_date, last_date


def get_sign(in_six_str, in_now_time, post_data):
    """
    获取请求参数sign
    @param in_six_str: 6位随机的字符串
    @param in_now_time: 当前时间对应的时间戳(10位)
    @param post_data: post请求的参数
    @return: 解密后的sign
    """
    # 将字典格式的请求数据转换成url gte &拼接的形式
    join_str = ''
    for k, v in post_data.items():
        join_str = f'{join_str}{k}={v}&'
    join_str = f'{join_str}time={in_now_time}'
    # 第一次md5加密
    md5_1 = hashlib.md5(join_str.encode('utf-8')).hexdigest()
    # 第二次md5加密
    md5_2 = hashlib.md5(md5_1.encode('utf-8')).hexdigest()
    # 拼接处特定的格式
    sign = f'{md5_2}{in_now_time}{in_six_str}'
    return sign


def search_live_user(search_word, cookie):
    """
    搜索抖音号获取搜索列表
    @return: 获取到的参数
    """
    search_url = 'https://www.youlue.com/yl/expert'
    headers = {
        'origin': 'https://www.youlue.com',
        'referer': 'https://www.youlue.com/intelligent/searchIntelligent',
        'user-agent': UserAgent(verify_ssl=False).random,
        # 'cookie': 'UM_distinctid=1771dec4b75924-036e98b04e28f6-3a3d530a-15f900-1771dec4b78741; sz=think%3A%7B%22cid%22%3A%22yBvXYTs1NlyuxA%252BGRV6tcA%253D%253D%22%2C%22machine%22%3A%22660f629481f0fc5f2936edbaa1ff0036%22%7D; Hm_lvt_de7959c699fcf15619ce7307d2430445=1611114761,1611120006; PHPSESSID=ct33ru781l2a7qrerhn3uuh77b; CNZZDATA1279040360=1084472877-1611114760-https%253A%252F%252Flink.zhihu.com%252F%7C1611122075; Hm_lpvt_de7959c699fcf15619ce7307d2430445=1611125052; SERVERID=af4ae1d4ee28b909870b522b93571ff7|1611125058|1611120006',
        'cookie': cookie,
    }
    search_data = {
        'page': '1',
        'category': '',
        'gender': '0',
        'fans': '0',
        'zan': '0',
        'video': '0',
        'aweme_with_good_count': '',
        'verify_keyword': '',
        'signature': '',
        'age': '0',
        'name': search_word,
        'province': '0',
        'city': '0',
        'personal': '0',
        'enterprise': '0',
        'window': '0',
        'is_contact_way': '0',
        'is_mcn': '0',
        'is_wc': '0',
        'sort': '1',
        'search': '2',
        'index': '10',
        'dy_user_category_id': '',
    }
    # 6位随机字符串
    six_str = get_six_str()
    # 现在的时间戳
    now_time = get_now_time()
    # sign
    sign = get_sign(six_str, now_time, search_data)
    # 更新到请求参数
    search_data.update({'sign': sign})
    item = {}
    try:
        response = requests.post(search_url, data=search_data, headers=headers, verify=False).json()

        datas = response.get('data')[0]
        # 粉丝数
        item['fans_num'] = datas.get('fans', 0)
        # 点赞
        item['total_favorited'] = datas.get('total_favorited', 0)
        # 作品数
        item['video'] = datas.get('aweme_count', 0)
        # 所在城市
        item['city'] = datas.get('city', '')
        # 昵称
        item['nickname'] = datas.get('nickname', '')
        # 后面的请求需要的参数
        item['get_id'] = datas.get('id')
        item['dy_user_id'] = datas.get('dy_user_id')
    except:
        pass
    return item


def get_fans_add_num(in_get_id, in_dy_user_id, cookie):
    """
    获取粉丝增加的数量
    @param cookie:
    @param in_get_id:
    @param in_dy_user_id:
    @return:
    """
    # 跳转的链接
    detail_url = f'https://www.youlue.com/intelligent/intelligentDetail?id={in_get_id}&user_id={in_dy_user_id}&tab=1'
    # 请求的参数
    get_fans_add_url = 'https://www.youlue.com/yl/fanschangeTotal'
    headers_fans = {
        # 'cookie': 'UM_distinctid=1771dec4b75924-036e98b04e28f6-3a3d530a-15f900-1771dec4b78741; sz=think%3A%7B%22cid%22%3A%22yBvXYTs1NlyuxA%252BGRV6tcA%253D%253D%22%2C%22machine%22%3A%22660f629481f0fc5f2936edbaa1ff0036%22%7D; Hm_lvt_de7959c699fcf15619ce7307d2430445=1611114761,1611120006; PHPSESSID=ct33ru781l2a7qrerhn3uuh77b; CNZZDATA1279040360=1084472877-1611114760-https%253A%252F%252Flink.zhihu.com%252F%7C1611122075; Hm_lpvt_de7959c699fcf15619ce7307d2430445=1611126261; SERVERID=af4ae1d4ee28b909870b522b93571ff7|1611126263|1611120006',
        'cookie': cookie,
        'origin': 'https://www.youlue.com',
        'referer': detail_url,
        'user-agent': UserAgent(verify_ssl=False).random,
    }
    fans_data = {
        'id': in_get_id,
        'type': '2',
    }

    six_str = get_six_str()
    now_time = get_now_time()
    sign = get_sign(six_str, now_time, fans_data)

    fans_data.update({'sign': sign})
    video_num = 0
    try:
        response = requests.post(get_fans_add_url, data=fans_data, headers=headers_fans, verify=False).json()
        video_num = response.get('collect').get('works', 0)
    except:
        pass
    return video_num


def get_goods_num(in_get_id, in_dy_user_id, cookie):
    """
    获取直播带货的数量
    @param cookie:
    @param in_get_id:
    @param in_dy_user_id:
    @return:
    """
    # 请求的页数
    page = 1
    goods_url = 'https://www.youlue.com/yl/webcast/dyUserWebcastList'
    # 跳转的url
    detail_url = f'https://www.youlue.com/intelligent/intelligentDetail?id={in_get_id}&user_id={in_dy_user_id}&tab=1'
    headers_goods = {
        'cookie': cookie,
        'origin': 'https://www.youlue.com',
        'referer': detail_url,
        'user-agent': UserAgent(verify_ssl=False).random,
    }
    # 带货数量
    goods_num = 0
    # 直播数
    total = 0
    # 今天的时间戳、一月前的时间戳
    start, end = now_last_month()
    while True:
        goods_data = {
            'title': '',
            'has_commerce_goods': '-1',
            'order_by': '1',
            'wc_finish_time': start,
            'wc_start_time': end,
            'dy_user_id': in_dy_user_id,
            'page': page,
            'limitNum': '10',
        }

        six_str = get_six_str()
        now_time = get_now_time()
        sign = get_sign(six_str, now_time, goods_data)
        goods_data.update({'sign': sign})

        try:
            response = requests.post(goods_url, data=goods_data, headers=headers_goods, verify=False).json()
            datas = response.get('data')
            total = datas.get('total', 0)
            datas_list = datas.get('list')
            # 计算总数
            for i in datas_list:
                goods_num += i.get('good_count', 0)
            # 判断总数是否请求完成
            if page < total // 10 + 1:
                page += 1
                time.sleep(random.uniform(1, 3))
            else:
                break
        except:
            break

    return total, goods_num


def login(save_cookie_path, phone, passwd):
    """
    登陆获取cookie
    @param passwd: 密码
    @param phone: 登陆手机号
    @param save_cookie_path: cookie保存路径
    @return: cookie值
    """
    login_url = 'https://www.youlue.com/yl/yllogin'
    headers_login = {
        'cookie': 'UM_distinctid=1771dec4b75924-036e98b04e28f6-3a3d530a-15f900-1771dec4b78741; CNZZDATA1279040360=1084472877-1611114760-https%253A%252F%252Flink.zhihu.com%252F%7C1611130212; Hm_lvt_de7959c699fcf15619ce7307d2430445=1611120006,1611131185,1611131266,1611131991; PHPSESSID=5n4h9a2849k1gn94uki0mnkemo; Hm_lpvt_de7959c699fcf15619ce7307d2430445=1611132108; SERVERID=af4ae1d4ee28b909870b522b93571ff7|1611132118|1611131991',
        'origin': 'https://www.youlue.com',
        'referer': 'https://www.youlue.com/',
        'user-agent': UserAgent(verify_ssl=False).random,
    }
    login_data = {
        'phone': phone,
        'password': passwd,
        'machine': get_machine_str(),
    }
    six_str = get_six_str()
    now_time = get_now_time()
    sign = get_sign(six_str, now_time, login_data)
    login_data.update({'sign': sign})
    response = requests.post(login_url, data=login_data, headers=headers_login, verify=False)
    cookies = response.cookies.items()
    cookie = ''
    for name, value in cookies:
        cookie += '{0}={1};'.format(name, value)

    with open(save_cookie_path, 'w', encoding='utf-8') as f:
        f.write(cookie)

    return cookie


def main(login_phone, login_passwd, key_word):
    save_cookie_path = 'youlue.json'
    if os.path.exists(save_cookie_path):
        with open(save_cookie_path, 'r', encoding='utf-8') as f:
            cookie = f.read()
    else:
        cookie = login(save_cookie_path, login_phone, login_passwd)
    # 获取后面需要请求的参数
    res = search_live_user(key_word, cookie)
    if not res:
        cookie = login(save_cookie_path, login_phone, passwd)
        res = search_live_user(key_word, cookie)

    try:
        get_id = res['get_id']
        dy_user_id = res['dy_user_id']
        video_num = get_fans_add_num(get_id, dy_user_id, cookie)
        res.update({
            'video_add_count': video_num
        })
        total, goods_num = get_goods_num(get_id, dy_user_id, cookie)
        res.update({
            'live_total': total,
            'goods_count': goods_num
        })
        return res
    except:
        return {}


if __name__ == '__main__':
    phone = '****'
    passwd = '****'
    keyword = ''
    print(main(phone, passwd, keyword))
