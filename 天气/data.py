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




