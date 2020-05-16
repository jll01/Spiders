#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   data.py
# @Time    :   2019/10/19 10:46
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import pandas as pd
import matplotlib.pyplot as plt
import pymysql


connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')
sql = '''select * from lianjia'''
datas = pd.read_sql(sql,con=connect)
cp_data = datas[:]

q_datas = cp_data[~cp_data['show_price_info'].str.contains('总价')]
q_datas = q_datas[~q_datas['show_price_info'].str.contains('待定')]
q_datas = q_datas[q_datas['city_name'].str.contains('西安')]
df = pd.DataFrame(q_datas,columns=['city_name','district_name','show_price_info'])

df.show_price_info = df.show_price_info.str.replace('均价','')
df.show_price_info = df.show_price_info.str.replace('元/平','')
df.show_price_info = df.show_price_info.astype('float64')
mean_data = df.groupby(df['district_name']).mean()
print(mean_data)

plt.plot(mean_data)
plt.show()