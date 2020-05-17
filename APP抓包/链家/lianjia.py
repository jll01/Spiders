#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   lianjia.py
# @Time    :   2020/2/15 9:00
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import json
import time
import urllib3
import pymysql


class LianJia(object):
    def __init__(self, input_area):
        self.headers = {
            'User-Agent': 'HomeLink7.1.1;HUAWEI HUAWEI+MLA-AL10; Android 4.4.2',
        }
        self.url = 'https://app.api.lianjia.com/newhouse/apisearch'
        # 增量
        self.offset = 0
        # mysql数据库
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()
        # 输入的城市名
        self.area = input_area

    def get_areas(self):
        """
        根据输入的地区获取给地区的行政区划代码
        """
        with open('areas.json', 'r', encoding='utf-8') as f:
            areas = json.loads(f.read().encode('utf-8'))
        while True:
            for area in areas:
                # 获取该城市的代码
                key = area.get(self.area)
                # 不为None则输入的城市存在
                if key != None:
                    value = key
                    break
                else:
                    value = 0
            if value != 0:
                return value
            else:
                print('输入错误或查找失败!', end='')
                self.area = input('请重新输入城市名(格式：北京市)：')

    def get_response(self):
        """
        发送请求获取到json数据
        """
        while True:
            data = {
                'is_showing_topic': '0',
                'city_id': self.get_areas(),
                'limit_offset': self.offset,
                'limit_count': '20',
                'is_showing_banner': '0',
                'dataParams': '{}',
                'request_ts': int(time.time()),
            }
            response = requests.post(self.url,headers=self.headers,data=data,verify=False,timeout=3).text
            json_data = json.loads(response)
            total = int(json_data.get('data').get('resblock_list').get('total_count'))
            infos = json_data.get('data').get('resblock_list').get('list')
            # 判断链家是否支持该城市查询
            if len(infos) == 0:
                print('链家暂时不支持{}城市'.format(self.area))
            else:
                self.get_info(infos)
                self.offset += 20
                # 比如总共有total=1145个楼盘，当self.offset大于total的时候会出错，因此在最后一次self.offset自增后通过判断将self.offset的值设置为total的值
                if total - 20 < self.offset < total:
                    self.offset = total
                if self.offset > total:
                    break

    def get_info(self, infos):
        """
        json文件中提取需要的参数
        """
        for info in infos:
            item = {}
            item['city_name'] = info.get('city_name') # 城市名
            item['district_name'] = info.get('district_name') # 所在区
            item['resblock_name'] = info.get('resblock_name') # 楼盘名
            item['resblock_alias'] = info.get('resblock_alias') # 楼盘别名
            item['address'] = info.get('address') # 地址
            item['house_type'] = info.get('house_type') # 房屋类型 商业类/住宅等
            item['sale_status'] = info.get('sale_status') # 是否售卖
            item['project_desc'] = info.get('project_desc') # 楼盘描述
            item['resblock_frame_area'] = info.get('resblock_frame_area') # 建筑面积
            item['show_price_info'] = info.get('show_price_info') # 价格
            item['total_price_start'] = info.get('total_price_start') + info.get('total_price_start_unit') # 一套的总价钱
            item['decoration'] = info.get('decoration')
            item['frame_rooms_desc'] = info.get('frame_rooms_desc') # 卧室  1/2/3居等
            tags = info.get('tags')
            item['tags'] = '|'.join(tags) # 小户型|自持商业|环线房|开发区
            item['open_date'] = info.get('open_date') # 开盘时间
            image = info.get('preload_detail_image')[0]
            item['image'] = image.get('image_list_size_url') # 效果图
            print(item)
            self.save_data(item)

    def save_data(self, item):
        """
        将数据保存到数据库中
        """
        self.cur.execute(
            """insert into lianjia(city_name,district_name,resblock_name,resblock_alias,address,house_type,sale_status,project_desc,resblock_frame_area,show_price_info,total_price_start,decoration,frame_rooms_desc,tags,open_date,image) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['city_name'],
                item['district_name'],
                item['resblock_name'],
                item['resblock_alias'],
                item['address'],
                item['house_type'],
                item['sale_status'],
                item['project_desc'],
                item['resblock_frame_area'],
                item['show_price_info'],
                item['total_price_start'],
                item['decoration'],
                item['frame_rooms_desc'],
                item['tags'],
                item['open_date'],
                item['image'],
            )
        )
        self.connect.commit()

        with open('lianjia.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def main(self):
        self.get_response()


if __name__ == '__main__':
    # 避免requests请求的时候提示警告信息
    urllib3.disable_warnings()

    area = input('请输入城市名(格式：北京市)：')
    lianjia = LianJia(area)
    lianjia.main()
