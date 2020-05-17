#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   data.py
# @Time    :   2020/1/19 20:34
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters


register_matplotlib_converters()

# 一年中每个月白天夜晚的最大温度和温度差
connect = pymysql.connect(host='localhost',port=3306,passwd='0000',user='root',db='scrapytest')
sql = '''select date,bWendu,yWendu from weather where date<"2012-01-01"'''
datas = pd.read_sql(sql,connect)
d = datas.set_index('date')
d.index = pd.to_datetime(d.index)
d = d.sort_index()

gg = d.resample('M').mean()

gg['bhigh'] = d.bWendu.resample('M').max()
gg['ylow'] = d.yWendu.resample('M').min()
gg.index = pd.DatetimeIndex(gg.index).month

gg['wencha'] = gg.bhigh - gg.ylow
print(gg)
# gg = gg.drop(['bWendu','yWendu'],axis=1)
# print(gg)
plt.plot(gg)
plt.show()




