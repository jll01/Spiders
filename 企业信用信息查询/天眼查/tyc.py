import re
import os
import time
import cv2
import numpy as np
import random
import requests
import socket
import json
import cpca

from requests.packages import urllib3
from requests.adapters import DEFAULT_RETRIES
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent
from dateutil.parser import parse


urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3


class TianYanCha(object):
    """
    通过cmd输入的参数获取公司信息
    """
    def __init__(self, phone, password, keyword):
        """
        @param keyword: 公司名 
        """
        # 登录手机号
        self.phone = phone
        # 登陆密码
        self.password = password
        # 搜索关键词
        self.search_key = keyword
        # 公司名称
        # self.keyword = company_name
        # 查找url
        self.search_url = '''https://www.tianyancha.com/search?key={}'''
        # 内容url
        self.info_url = '''https://www.tianyancha.com/company/{}'''
        # 获取变更信息
        self.page_count = 1
        self.text_login = '请输入手机号'
        self.text_password = '请输入登录密码'
        # cookie
        self.cookie = ''
        # cookie名
        self.cookie_name = f'tyc_cookie.json'
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
        imgA = cv2.imread(f'./captcha/captcha1.png')
        imgB = cv2.imread(f'./captcha/captcha2.png')
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
        captcha1.save(f'./captcha/captcha1.png')

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
        captcha2.save(f'./captcha/captcha2.png')

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

        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        # 谷歌driver
        driver = webdriver.Chrome(executable_path='../driver/chromedriver.exe', options=options)
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
            # WebDriverWait(self.driver, 10, 0.2).until(lambda x: x.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]'))
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
        # print(cookie)
        cookie = [f'{item[0]}={item[1]}' for item in cookie.items()]
        self.cookie = '; '.join(cookie)
        with open(f'tyc_cookie.json', 'w', encoding='utf-8') as f:
            ip_port = f'{socket.gethostbyname(socket.gethostname())}:{"0000"}'
            cookie_data = {ip_port: [
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                self.cookie
            ]}
            f.write(json.dumps(cookie_data, ensure_ascii=False))

    def get_company_url(self):
        """
        获取天眼查中查找到的公司id，拼接url
        @return: 公司的id
        """
        num = 0
        while True:
            headers = {
                'User-Agent': UserAgent(verify_ssl=False).random,
                'cookie': self.cookie,
            }
            try:
                res = requests.get(self.search_url.format(f'{self.search_key}'), headers=headers, verify=False, timeout=10)

                if res.status_code != 200:
                    num += 1
                    continue
                res_text = res.text
                if '没有找到' in res.text:
                    return {}

                if '天眼校验' in res_text:
                    print('需要校验，换账号重新登录！请稍后！')
                    driver_s = self.et_driver()
                    self.autologin(driver_s)
                    self.main()

                company_id = ''.join(re.findall(r'relatedHumanSearchGraphId=(.*?);', str(res.headers)))
                if company_id:
                    return self.get_company_info(company_id)
                else:
                    company_id = self.merge_list(re.findall(r'href=[\'"]https://www.tianyancha.com/company/(\d+)[\'"]', res_text))
                    if company_id:
                        return self.get_company_info(company_id)
                    else:
                        num += 1
            except Exception as e:
                time.sleep(2)
                num += 1

            if num >= 3:
                return {}

    def get_company_info(self, com_id):
        """
        获取公司的具体信息
        @param com_id: 公司id
        @return:
        """
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random,
            'cookie': self.cookie
        }
        item = dict()

        try:
            response = requests.get(self.info_url.format(com_id), headers=headers, verify=False, timeout=10)
        except Exception as e:
            pass
        else:
            content = response.text.replace(' ', '').replace('\n', '').replace(r'\s', '')
            if '天眼校验' in content:
                print('需要校验，换账号重新登录！请稍后！')
                driver_s = self.et_driver()
                self.autologin(driver_s)
                self.main()

            # 公司名称
            item['company_name'] = self.merge_list(re.findall(r'<h\d+\s?class="name">(.*?)</h\d+>', content))
            # 法定代表人
            item['legal'] = self.merge_list(re.findall(r'法定代表人</td>.*?<a.*?>(.*?)</a>', content))
            # 电话
            item['phone'] = self.merge_list(re.findall(r'<input\s?type="hidden"\s?id="phoneNumber"\s?value="(.*?)">', content))
            if '*' in item['phone']:
                print('未登录！重新登录！')
                driver_s = self.et_driver()
                self.autologin(driver_s)
                self.main()
            # 邮箱
            item['email'] = self.merge_list(re.findall(r'([0-9a-zA-Z-]{1,}@[0-9a-zA-Z-.]{1,}(?:[comnet]{1,3}))', content))
            # 状态
            item['register_status'] = self.merge_list(re.findall(r'<td.*?>经营状态</td><td.*?>(.*?)</td>', content, re.DOTALL))
            # 公司网址
            item['official_url'] = self.merge_list(re.findall(r'<span\s?class=["\']label["\']>网址[:：]</span><a\s?class=["\']company-link["\']\s?target=["\']_blank["\']\s?href="(.*?)"\s?rel', content))
            # 注册资本
            item['register_capital'], item['register_currency'] = self.money(self.merge_list(re.findall(r'注册资本</td><td\s?width=["\'].*?["\']><div\s?title=["\'](.*?)["\']>', content)))
            # 实缴资本
            item['real_capital'], item['real_currency'] = self.money(self.merge_list(re.findall(r'实缴资本</td><td\s?width=["\'].*?["\']>(.*?)</td><td>', content)))
            # 统一社会信用代码
            credit_code = self.merge_list(re.findall(r'统一社会信用代码<div\s?class=["\']data-describe.*?<td.*?>(.*?)</td>', content))
            item['credit_code'] = re.sub(r'[\n ：:-]', '', credit_code, re.DOTALL)
            # 工商注册号
            business_number = self.merge_list(re.findall(r'<td\s?>工商注册号</td><td\s?>(.*?)</td>', content))
            item['business_number'] = re.sub(r'[\n ：:-]', '', business_number, re.DOTALL)
            # 登记机关
            item['reg_address_name'] = self.merge_list(re.findall(r'登记机关</td><td\s?colspan=".*?">(.*?)</td>', content))
            # 行业
            item['industry'] = self.merge_list(re.findall(r'行业</td><td.*?>(.*?)</td>', content))
            # 企业类型
            item['business_type'] = self.merge_list(re.findall(r'公司类型</td><td.*?>(.*?)</td>', content))
            # 注册地址
            item['address'] = self.merge_list(re.findall(r'注册地址</td><td.*?>(.*?)<', content))
            # 省 市 区
            item['province'], item['city'], item['area'] = cpca.transform([item['address']]).loc[0, ['省', '市', '区']]
        return item

    @staticmethod
    def money(mo):
        """
        分离钱和币种
        @param mo: 获取到的公司注册资金
        @return: 数字，币种(100000, 人民币)
        """
        change_value = {
            '元': '人民币',
            '元人民币': '人民币',
        }
        if not mo or mo.strip() == '-':
            register_capital = '-'
            register_currency = '人民币'
        else:
            s = mo.replace(',', '').replace('(', '').replace(')', '')
            try:
                if '万' in s:
                    value = s.split('万')
                else:
                    value = re.findall(r'(\d+)(\w+)', s)[0]
            except:
                value = [0, '人民币']
            register_capital = int(eval(value[0]) * 10000)
            register_currency = change_value.get(value[1], value[1])

        return register_capital, register_currency

    @staticmethod
    def merge_list(in_list):
        """
        从列表中提取元素
        """
        if len(in_list) >= 1:
            return in_list[0].strip()
        else:
            return ''

    def main(self):
        """
        判断本地是否保存有登录后的cookie值，没有则进行登录保存
        @return:
        """
        # 判断是否有保存cookie的文件，没有模拟登陆
        if not os.path.exists('tyc_cookie.json'):
            driver = self.et_driver()
            self.autologin(driver)
            driver.quit()
        else:
            # 有的话打开文件读取内容
            with open(f'tyc_cookie.json', 'r', encoding='utf-8') as f:
                read_cookie = json.loads(f.read())
                # 本机ip和port
                ip_port = f'{socket.gethostbyname(socket.gethostname())}:{"0000"}'
                ip_port = read_cookie.get(ip_port, '')
                # 如果文件中存在以当前ip和port为字典的键的值
                if ip_port:
                    now_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    # 判断保存时间和当前时间的时间差
                    time_c = parse(now_str) - parse(ip_port[0])
                    # 大于7天的时间，重新获取cookie
                    if time_c.days >= 7:
                        driver = self.et_driver()
                        self.autologin(driver)
                        driver.quit()
                    else:
                        # 满足时间条件，则获取cookie
                        self.cookie = ip_port[1]
                else:
                    # ip和port提取失败的时候直接模拟登陆
                    driver = self.et_driver()
                    self.autologin(driver)
                    driver.quit()

        company_info = self.get_company_url()

        return company_info


if __name__ == '__main__':
    login_phone = '****'
    login_passwd = '****'
    company_name = '****'
    print(TianYanCha(login_phone, login_passwd, company_name).main())
