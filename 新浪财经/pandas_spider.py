#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   pandas_spider.py
# @Time    :   2020/4/15 15:57
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import pandas as pd
import time
import random


df = pd.DataFrame()
url = 'http://stock.finance.sina.com.cn/stock/go.php/vPerformancePrediction/kind/eps/index.phtml?p={}'
for i in range(1, 101):
    df = pd.concat([df, pd.read_html(url.format(i))[0]])
    print("第{}页下载完成了".format(i))
    time.sleep(random.uniform(1, 3))

df.to_csv('./data.csv', encoding='utf_8_sig', index=0)


