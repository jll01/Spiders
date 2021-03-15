import time
import cv2
import numpy as np
import random
import requests

from requests.packages import urllib3
from requests.adapters import DEFAULT_RETRIES
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait


urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3


class TianYanCha(object):
    def __init__(self, phone, password):
        """
        滑动 极验验证码
        @param phone: 登录手机号
        @param password: 登录密码
        """
        # 登录手机号
        self.phone = phone
        # 登陆密码
        self.password = password
        self.text_login = '请输入手机号'
        self.text_password = '请输入登录密码'
        # 电脑设置中的缩放比例, 识别极验验证码的时候用
        self.k = 1.25

    @staticmethod
    def get_track(distance):
        """
        根据偏移量获取移动轨迹
        @param distance: 偏移量
        @return: 移动轨迹(列表)
        """
        # 移动轨迹
        track = []
        # 间距
        v = int(distance/20)
        while True:
            in_t = random.randint(1, 10)

            if sum(track) - distance < 0:
                track.append(v + in_t)

            if sum(track) >= distance:
                break

        if sum(track) - distance > 0 and track:
            track[-1] = track[-1] + distance - sum(track)
        return track

    def match2img(self):
        """
        比对缺口的位置
        @return:
        """
        # 读取图像数据
        imgA = cv2.imread('captcha1.png')
        imgB = cv2.imread('captcha2.png')
        # 转换成灰色
        grayA = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imgB, cv2.COLOR_BGR2GRAY)

        # 获取图片的大小
        height, width = grayA.shape
        # 取局部图像，寻找匹配位置
        result_window = np.zeros((height, width), dtype=imgA.dtype)
        hh = int(100 * self.k)
        for start_y in range(0, height - hh, 10):
            for start_x in range(0, width - hh, 10):
                window = grayA[start_y:start_y + hh, start_x:start_x + hh]
                match = cv2.matchTemplate(grayB, window, cv2.TM_CCOEFF_NORMED)
                _, _, _, max_loc = cv2.minMaxLoc(match)
                matched_window = grayB[max_loc[1]:max_loc[1] + hh, max_loc[0]:max_loc[0] + hh]
                result = cv2.absdiff(window, matched_window)
                result_window[start_y:start_y + hh, start_x:start_x + hh] = result

        # 用四边形圈出不同部分
        _, result_window_bin = cv2.threshold(result_window, 30, 255, cv2.THRESH_BINARY)
        _, contours, _ = cv2.findContours(result_window_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        location_img = 0
        return_arr = [{'min_dis': np.nanmin(contour, 0), 'max_dis': np.nanmax(contour, 0), 'ar': cv2.contourArea(contour)} for contour in contours if cv2.contourArea(contour) >= hh and np.nanmin(contour, 0)[0][0] >= 10]
        sort_arr = sorted(return_arr, key=lambda x: x['ar'], reverse=True)

        if sort_arr:
            location_img = sort_arr[0]['min_dis'][0][0]
        return location_img

    def get_first_img(self, driver):
        """
        获取无缺口图片
        @param driver: 浏览器驱动对象
        @return:
        """
        # 获取图
        img = WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]'))
        time.sleep(1)
        location = img.location
        size = img.size
        x = location['x'] * self.k
        y = location['y'] * self.k
        h = size['height'] * self.k
        w = size['width'] * self.k
        top, bottom, left, right = y, y + h, x, x + w
        # 截取第一张图片(无缺口的)
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        captcha1 = screenshot.crop((left, top, right, bottom))
        captcha1.save('captcha1.png')

    def get_second_img(self, driver):
        """
        获取有缺口的图片
        @param driver: 浏览器驱动对象
        @return:
        """
        # 获取第二张图，先点击
        slider = WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]'))
        ActionChains(driver).click_and_hold(slider).perform()
        img1 = WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]'))
        # img1 = self.driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
        location1 = img1.location
        size1 = img1.size
        x = location1['x'] * self.k
        y = location1['y'] * self.k
        h = size1['height'] * self.k
        w = size1['width'] * self.k
        top1, bottom1, left1, right1 = y, y + h, x, x + w
        screenshot = driver.get_screenshot_as_png()
        screenshot1 = Image.open(BytesIO(screenshot))
        captcha2 = screenshot1.crop((left1, top1, right1, bottom1))
        captcha2.save('captcha2.png')

    @staticmethod
    def et_driver():
        """
        新建浏览器
        @return:
        """
        options = webdriver.ChromeOptions()
        # 防止服务器识别是模拟登陆
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option("useAutomationExtension", False)

        options.add_argument('--disable-gpu')

        # 谷歌driver
        driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        # 防止服务器识别是模拟登陆(新版)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
            """
        })

        # 浏览器窗口最大化
        driver.maximize_window()
        return driver

    def autologin(self, driver):
        """
        登陆并保存cookie
        @param driver: 浏览器对象
        @return:
        """
        driver.get('http://www.tianyancha.com')
        time.sleep(2)
        # 关底部
        try:
            driver.find_element_by_xpath('//*[@id="tyc_banner_close"]').click()
        except:
            pass

        try:
            driver.find_element_by_xpath('//*[contains(@class, "tic-guanbi1")]').click()
        except:
            pass

        # 点击右上角的登陆注册
        WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('//*[@id="web-content"]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[5]/a')).click()
        # 在弹框里面点击密码登陆
        WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('.//*[@class="sign-in"]/div[contains(@class, "title-tab")]/div[2]')).click()
        # 输入手机号
        WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_elements_by_xpath("//input[@placeholder='{}']".format(self.text_login))[-2]).send_keys(self.phone)
        # 输入密码
        WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_elements_by_xpath("//input[@placeholder='{}']".format(self.text_password))[-1]).send_keys(self.password)
        # 点击登陆
        time.sleep(3)
        WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('//div[@class="sign-in"]/div[contains(@class, "mobile_box")]/div[2]')).click()
        time.sleep(2)

        # 获取无缺口和有缺口的图片
        print('正在保存无缺口的图片')
        self.get_first_img(driver)
        print('正在保存有缺口的图片')
        self.get_second_img(driver)

        loc_img = self.match2img()
        print('缺口位置', loc_img)
        # 开始移动
        tracks = self.get_track(int(loc_img / self.k)-6)
        print('滑动轨迹', tracks)
        # 拖动滑块
        for track in tracks:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=random.randint(1, 10)).perform()
        # 等待验证
        time.sleep(1)
        # 释放鼠标
        ActionChains(driver).release().perform()
        try:
            WebDriverWait(driver, 5, 0.2).until(lambda x: x.find_element_by_class_name("nav-user-name"))
        except Exception as e:
            print('能找到滑块，重新试')
            driver.delete_all_cookies()
            driver.refresh()
            # 重新登陆
            self.autologin(driver)
        else:
            print('登陆成功')

        # 获取cookie
        cookie_dict = driver.get_cookies()
        cookie = {}
        for i in cookie_dict:
            cookie[i['name']] = i['value']
        cookie = [f'{item[0]}={item[1]}' for item in cookie.items()]
        cookie = '; '.join(cookie)
        print(cookie)

    def main(self):
        """
        判断本地是否保存有登录后的cookie值，没有则进行登录保存
        @return:
        """
        driver = self.et_driver()
        self.autologin(driver)
        driver.quit()


if __name__ == '__main__':
    login_phone = '****'
    login_passwd = '****'
    print(TianYanCha(login_phone, login_passwd).main())
