import numpy as np
import pandas as pd
import pymysql

from matplotlib.pyplot import plot


connection = pymysql.connect(host='localhost',user='root',passwd='0000',port=3306,db='scrapytest')
cur = connection.cursor()
# sql_time = "select time from qqmusic where time>='2019-09-16 23:00:00'"
sql_time = "select time from qqmusic"

cur.execute(sql_time)
data_qq = cur.fetchall()
data_list = []
for i in data_qq:
    data_list.append(pd.to_datetime(i[0]))

s = pd.Series(1, index=data_list)
d = s.resample('60min').sum()
print(d)



