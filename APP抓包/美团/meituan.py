import requests
import time
import json
import urllib3
import pymysql
import re

from urllib import parse


class MeiTuan(object):
    def __init__(self, cityname):
        self.headers = {
            'User-Agent': 'AiMeiTuan /HUAWEI-4.4.2-HUAWEI MLA-AL10-1280x720-240-5.5.4-254-863064010680710-qqcpd',
        }
        # 获取城市id
        self.id_url = 'http://api.meituan.com/group/v1/city/list'

        self.offset = 0
        # 存储城市id
        self.city_id = []
        # 输入城市的名称
        self.city_name = cityname
        # mysql数据库
        self.conn = pymysql.connect(host='',port=0,user='',passwd='',db='')
        self.cur = self.conn.cursor()

    def get_id(self):
        """
        获取每个城市的id并保存
        """
        response = requests.get(self.id_url,headers=self.headers).text
        ids = json.loads(response).get('data')

        for city_id in ids:
            self.city_id.append({city_id.get('name'): city_id.get('id')})

        with open('cityid.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.city_id, ensure_ascii=False))

    def judge_key(self,city):
        """
        判断商家信息所在的城市，在返回的信息中值返回了城市的id
        """
        for value in self.city_id:
            for k, v in value.items():
                if v == int(city):
                    return k

    def judge_value(self, city):
        """
        获取输入的城市的id
        """
        # 输入错误的时候有一次重新输入的机会
        count = 0
        while True:
            # 判断是否存在这个城市的id，如果存在值为1
            num = 0
            # 在存储城市id的列表中判断是否存在输入的城市id
            for value in self.city_id:
                for k, v in value.items():
                    if k == city:
                        num = 1
                        return v
            # 没找到id的时候，给一次重新检查输入格式是否正确的机会
            if num != 1 and count == 0:
                print('输入错误或查找失败!', end='')
                self.city_name = input('请重新输入城市名(格式：北京)：')
                count += 1
            # 一次机会之后返回id=1的城市（北京）
            if count == 1:
                return 1

    @staticmethod
    def get_menu(des):
        """
        获取详细信息中的菜单信息
        """
        # 如果返回的信息中存在菜单信息，则获取下标为0的值
        if len(des) != 0:
            des_2 = des[0]
            # 判断是否为空
            if len(des_2) != 0:
                # 存储菜单信息
                list_menu = []
                # 提取的菜单信息市列表中含有字典的格式[{},{}]
                for menu in des_2:
                    # 存储每个字典的信息
                    me = []
                    for key, value in menu.items():
                        if value != '':
                            # 对详细图片单独处理
                            if key == 'images':
                                # 转换成list
                                urls = eval(value)
                                # 存储images的url
                                url_li = []
                                for url in urls:
                                    try:
                                        # 正则匹配出url
                                        url_li.append(re.match(r'(.*?)@.*?',url)[1])
                                    except Exception as e:
                                        pass
                                # 对images的url进行拼接
                                value = str(','.join(url_li))
                            mess = key + ':' + value
                            me.append(mess)
                    # 对当前这个字典进行拼接，获取到字符串的形式存储
                    list_menu.append(','.join(me))
                # 对所有字典转换后的字符串拼接，以|隔开
                return '|'.join(list_menu)
        else:
            return ''

    def get_response(self):
        """
        发送请求获取json数据
        """
        # 获取到输入城市的id
        id_city = self.judge_value(self.city_name)
        while True:
            # url中的参数
            data = {
                'sort': 'defaults',
                'mypos': '36.00108291925976,115.56923237942485',
                'ste': '_b4',
                'mpt_cate1': '-1',
                'offset': self.offset,  # 翻页 +20
                'limit': '20',
                'fields': 'id,slug,cate,subcate,dtype,ctype,mlls,solds,status,range,start,end,imgurl,squareimgurl,title,hotelroomname,price,value,mname,brandname,rating,rate-count,satisfaction,mealcount,nobooking,attrJson,hotelExt,campaigns,terms,recreason,showtype,deposit,securityinfo,optionalattrs,bookinginfo,pricecalendar,isappointonline,couponbegintime,couponendtime,rdploc,rdcount,digestion,isAvailableToday',
                'client': 'android',
                'utm_source': 'qqcpd',
                'utm_medium': 'android',
                'utm_term': '254',
                'version_name': '5.5.4',
                'utm_content': '863064010680710',
                'utm_campaign': 'AgroupBgroupC0E0Ghomepage_allcate',
                'ci': id_city,
                'uuid': 'E0950FB5296BFAEC18D8310611AB53A4A4578E5260F17F9E1DE27DE8980CAC29',
                'msid': '8630640106807101563443352363',
                '__skck': '09474a920b2f4c8092f3aaed9cf3d218',
                '__skts': int(time.time()*1000),  # 时间戳
                '__skua': '6d8565c16e42af5ebc0fefd58087d246',
            }
            info_url = 'http://api.meituan.com/group/v1/deal/select/city/{}/cate/-1?'.format(id_city)
            info_res = requests.get(info_url + parse.urlencode(data),headers=self.headers).text
            try:
                infos = json.loads(info_res).get('data')
                if len(infos) != 0:
                    # 提取信息
                    self.get_info(infos)
                    time.sleep(5)
                    self.offset += 20
                else:
                    break
            except Exception as e:
                print('出现异常，请稍后重试！{}'.format(e))

    def get_info(self, infos):
        """
        提取详细信息
        """
        for info in infos:
            item = {}
            try:
                city = info.get('rdploc')[0].get('city')
                item['city'] = self.judge_key(city) # 城市

                item['name'] = info.get('rdploc')[0].get('name') # 店名
                item['addr'] = info.get('rdploc')[0].get('addr') # 地址
                item['phone'] = info.get('rdploc')[0].get('phone') # 电话
                item['showtype'] = info.get('rdploc')[0].get('showType') # 经营类型

                item['before_discount'] = info.get('value')  # 原价

                item['discount'] = info.get('price')  # 打折

                item['menu'] = self.get_menu(info.get('menu'))  # menu

                item['comment_count'] = info.get('rate-count')  # 评价人数
                item['start'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info.get('start'))) # 开店时间

                terms = info.get('terms')
                list_term = []
                for term in terms:
                    mess = term['title'] + ':' + ','.join(term['content'])
                    list_term.append(mess)
                item['shopping_notice'] = '|'.join(list_term).replace('\n', '') # 购买须知
                print(item)
                self.save_data(item)
            except Exception as e:
                print('提取信息异常{}'.format(e))

    def save_data(self, item):
        """
        保存信息
        """
        with open('meituan.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

        # 保存到mysql数据库中
        self.cur.execute(
            '''insert into meituan(city,name,addr,phone,showtype,before_discount,discount,menu,comment_count,start,shopping_notice) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (
                item['city'],
                item['name'],
                item['addr'],
                item['phone'],
                item['showtype'],
                item['before_discount'],
                item['discount'],
                item['menu'],
                item['comment_count'],
                item['start'],
                item['shopping_notice'],
            )
        )
        self.conn.commit()

    def main(self):
        self.get_id()
        self.get_response()
        # self.judge_value(self.city_name)


if __name__ == '__main__':
    urllib3.disable_warnings()
    city_name = input('请输入城市(格式如：北京)：')
    mt = MeiTuan(city_name)
    mt.main()
