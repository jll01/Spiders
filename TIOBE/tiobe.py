import requests
import time
import re
import os
import csv
import plotly.express as px
import pandas as pd

from fake_useragent import UserAgent


def get_data():
    f = open('tiobe.csv', 'w', newline='')
    writer = csv.DictWriter(f, ['name', 'date', 'value'])
    writer.writeheader()

    url = '''https://www.tiobe.com/tiobe-index/'''
    headers = {
        'User-Agent': UserAgent().random
    }

    source = requests.get(url, headers=headers).text
    result = ''.join(re.findall(r'series: (.*?)\}\)', source, re.DOTALL))
    result = re.findall(r'({.*?})', result, re.DOTALL)
    for res in result:
        name = ''.join(re.findall(r"name : '(.*?)'", res, re.DOTALL))
        datas = re.findall(r'\[Date.UTC\((.*?)\), (.*?)\]', res, re.DOTALL)
        for data in datas:
            date = data[0].replace(', ', '-')
            value = data[1]
            item = {
                'name': name,
                'date': date,
                'value': value
            }
            # print(item)
            writer.writerow(item)

    f.close()


def plot_tiobe():
    df = pd.read_csv('tiobe.csv')
    fig = px.bar(df,
                 y='name',
                 x='value',
                 animation_frame='date',
                 range_x=[0, df.value.max()],
                 orientation='h',
                 text='value',
                 color='name')

    fig.update_layout(width=666,
                      height=666,
                      xaxis_showgrid=False,
                      yaxis_showgrid=False,
                      showlegend=False)

    fig.show()


if __name__ == '__main__':
    get_data()
    plot_tiobe()

