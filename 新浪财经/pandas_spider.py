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


