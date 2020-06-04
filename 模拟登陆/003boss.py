#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   017boss.py
# @Time    :   2019/11/25 12:44:33
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from bs4 import BeautifulSoup
from selenium import webdriver
import json, time


service_args = [
  '--proxy=112.87.68.89:9999',  # 代理 IP：prot  （eg：192.168.0.28:808）
  '--proxy-type=http',      # 代理类型：http/https
  '--load-images=no',      # 关闭图片加载（可选）
  '--disk-cache=yes',      # 开启缓存（可选）
  '--ignore-ssl-errors=true'  # 忽略https错误（可选）
]
driver = webdriver.PhantomJS(service_args=service_args)

driver.get("https://www.zhipin.com/?ka=header-home")

search_content = input("请输入要找的工作岗位:")
driver.find_element_by_xpath('//input[@name="query"]').send_keys(search_content)
driver.find_element_by_class_name("btn-search").click()

num = 1
while True:
    soup = BeautifulSoup(driver.page_source,'lxml')
    driver.save_screenshot("017boss.png")
    # 岗位名称
    jobs = soup.find_all(name='div',class_='job-title') 
    # 工资
    moneys = soup.find_all(name='span',class_='red')
    # 公司名称
    companys = soup.select('.info-company div h3 a')
    # 联系人
    links = soup.select('.info-publis h3')
    print("正在下载第%d页" % num)
    for job,money,company,link in zip(jobs,moneys,companys,links):
        items = {
            "工作岗位:": job.get_text().strip(),
            "工资:": money.get_text().strip(),
            "公司:": company.get_text().strip(),
            "联系人:": link.get_text().strip(),
        }
        with open('day01-03/017boss.json','a', encoding='utf-8') as f:
            f.write(json.dumps(items, ensure_ascii=False) + '\n')
    print("第%d页下载完成！" % num)
    time.sleep(60)
    if driver.page_source.find("next disabled") != -1:
        break
    driver.find_element_by_class_name("next").click()
    num += 1
