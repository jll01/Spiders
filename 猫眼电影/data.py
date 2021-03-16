import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymysql


connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')

# 每部电影最后票房
# sql = '''select 日期,电影名称,累计上映天数,综合票房总票房 from moviepiaofang where id<21'''
# d = pd.read_sql(sql=sql,con=connect)
# d = d.set_index('电影名称')
# d = d.sort_values(by=['电影名称', '综合票房总票房'], ascending=(False,True))
# d = d[~d.index.duplicated(keep='last')]
# s = [str(i) for i in list(range(1,100))]
# d = d[d['累计上映天数'].isin(s)]
# print(d)

# 按年综合票房
# sql = "select 日期,电影名称,综合票房 from moviepiaofang"
# df = pd.read_sql(sql,connect)
# df = df.set_index('日期')
# df = df.sort_index(ascending=True)
# g = df.groupby(df.index).sum()
# g.index = pd.to_datetime(g.index)
# df = g.resample('A').sum()
# df.index = df.index.year
# print(df)
# plt.plot(df)
# plt.show()


# 每部电影综合平均票价
# sql = '''select 日期,电影名称,综合平均票价 from moviepiaofang'''
# d = pd.read_sql(sql=sql,con=connect)
# d = d.set_index('电影名称')
# # print(d)
# d = d.groupby(d.index).mean()
# print(d)


# 电影排片场次
sql = "select 日期,排片场次 from moviepiaofang where 电影名称='战狼2'"
d = pd.read_sql(sql=sql,con=connect)
d = d.set_index('日期')
d = d.sort_values(by='日期',ascending=True)
print(d)
plt.plot(d)
plt.show()


