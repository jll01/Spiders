import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


connect = pymysql.connect(host='****', port=0000, user='****', passwd='****', db='****')
cur = connect.cursor()
sql = 'select bai,shi,ge from 3d'# where id<10'
cur.execute(sql)
datas = cur.fetchall()

bai = []
shi = []
ge = []
for data in datas:
    bai.append(data[0])
    shi.append(data[1])
    ge.append(data[2])

item_bai = {}
for i in range(10):
    item_bai[i] = bai.count(i)

item_shi = {}
for i in range(10):
    item_shi[i] = shi.count(i)

item_ge = {}
for i in range(10):
    item_ge[i] = ge.count(i)

# 三个数相加
item_sum = {}
sum_and = []
for i,j,k in zip(bai,shi,ge):
    sum_and.append(i+j+k)

for i in sum_and:
    item_sum[i] = sum_and.count(i)


item = {}
item['key'] = []
item['value'] = []

item['bai'] = []
item['shi'] = []
item['ge'] = []


for key,value in item_bai.items():
    item['key'].append(key)
    item['bai'].append(value)
for key,value in item_shi.items():
    item['shi'].append(value)
for key,value in item_ge.items():
    item['ge'].append(value)

# 百、十、个位分别画图
l = pd.DataFrame({'bai':item['bai'],'shi':item['shi'],'ge':item['ge']},index=list(range(10)))

l.plot()
plt.show()

# 每个号出现的次数
item_all = {}
sum_all = []
for i,j,k in zip(bai,shi,ge):
    sum_all.append(i*100+j*10+k)

for i in sum_all:
    item_all[i] = sum_all.count(i)


s = pd.DataFrame({'value':list(item_all.values())},index=list(item_all.keys()))
s = s.sort_index()
print(s)
s.plot(figsize=(16,12))
plt.show()
