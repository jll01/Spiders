#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   滑动条(无缺口).py
# @Time    :   2019/8/7 10:19
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

class YanZheng(object):
    '''以下代码主要破解淘宝访问次数过多弹出访问验证窗口'''
    def __init__(self,url):
        self.count = 1  # 最多识别次数
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_drive = r'D:\soft\Chrome\chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chrome_drive,options=chrome_options)
        self.driver.get(url)

    def get_track(self, distance):
        '''拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速'''
        # 初速度
        '''拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速'''
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        t_a = 0.2
        t1 = 1.5
        t2 = 0.5
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 加速度(计划3秒内完成滑动)
        a1 = 2 * distance / 3
        # 减速度（3秒内完成，公式推导）
        a2 = -6 * distance
        while True:
            if t_a <= t1:
                # 初速度
                v0 = v
                # 0.2秒时间内的位移
                s = v0 * t + 0.5 * a1 * (t ** 2)
                tracks.append(round(s))
                # 下次的初速度
                v = v0 + a1 * t
                # 总用时
                t_a += t
            elif t1 < t_a and t_a <= t1 + t2:
                v0 = a1 * t1
                s = v0 * t + 0.5 * a2 * (t ** 2)
                tracks.append(round(s))
                v = v0 + a2 * t
                t_a += t
            else:
                break

        tracks.append(distance - sum(tracks))
        return tracks

    def main_check_code(self, element):
        """拖动识别验证码"""
        # 获得移动轨迹
        track_list = self.get_track(260)
        print('第一步,点击滑动按钮')
        ActionChains(self.driver).click_and_hold(on_element=element).perform()  # 点击鼠标左键，按住不放
        time.sleep(1)
        print('第二步,拖动元素')
        for track in track_list:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
            time.sleep(0.002)
        # print('第三步,释放鼠标')
        # ActionChains(self.driver).release(on_element=element).perform()

    def main(self):
        while self.count <= 6:
            print('----------第{}次识别!----------'.format(self.count))
            try:
                iframe = self.driver.find_element_by_xpath('//iframe[contains(@src,"rate.tmall.com:443")]')
                self.driver.switch_to.frame(iframe)
                element = self.driver.find_element_by_xpath('//span[@id="nc_1_n1z"]')  # 需要滑动的元素
                self.main_check_code(element)
            except Exception as e:
                self.driver.switch_to.default_content()
                self.driver.refresh()
                time.sleep(3)

            text = self.driver.find_element_by_xpath('div[@id="nc_1__scale_text"]/span[@class="nc-lang-cnt"]').text
            print(text)
            if text.startswitch('请按住'):
                print('第{}次验证失败！'.format(self.count))
                self.count += 1
            else:
                print('验证成功！')
                break
            time.sleep(3)


if __name__ == '__main__':
    url = ''
    yz = YanZheng(url)
    yz.main()

