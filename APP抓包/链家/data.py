import pandas as pd
import matplotlib.pyplot as plt
import pymysql


connect = pymysql.connect(host='',port=0,user='',passwd='',db='')
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
