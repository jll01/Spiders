#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   bilibili_ciyun.py
# @Time    :   2020/5/16 17:03
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud, STOPWORDS
import pymysql

connect = pymysql.connect(host='localhost', user='root', password='0000', db='scrapytest', port=3306)
cur = connect.cursor()


sql = '''select content from bili_comment'''

cur.execute(sql)
res = cur.fetchall()
str_list = []
for i in res:
    str_list.append(i[0])
file = ','.join(str_list)

default_mode = jieba.cut(''.join(file))
text = ''.join(default_mode)
print(text)
# 要制作词云的图像模板，背景
im = Image.open('1.png')
alice_mask = np.array(im)


# 设置停止显示的词
stopwords = set(STOPWORDS)
stopwords.add("1")
wc = WordCloud(
    # 设置字体，不指定就会出现乱码,这个字体文件需要下载
    font_path=r'C:\Windows\Fonts\STKAITI.TTF',
    background_color="white",
    max_words=2000,
    # 图片背景
    mask=alice_mask,
    stopwords=stopwords)

wc.generate(text)
wc.to_file("qq_result.jpg")

plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()
