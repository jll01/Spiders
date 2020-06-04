
import time
import requests

from requests.cookies import RequestsCookieJar
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree


class Price(object):
    def __init__(self):
        self.chrome_drive = r'****'
        self.driver = webdriver.Chrome(executable_path=self.chrome_drive)
        self.session = requests.session()
        self.login_url = 'https://member.zjtcn.com/common/login.html'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
        }


    def login(self):
        self.driver.get(self.login_url)
        # 最大界面
        self.driver.maximize_window()
        # 点击登陆进入登陆页面
        # pages = self.driver.find_element_by_link_text("【 登录 】")
        # self.driver.execute_script("arguments[0].click();", pages)

        # 输入账号
        self.driver.find_element_by_xpath('//div[@class="login_one"]//div//div/input[@id="memberID"]').send_keys(18866674071)
        time.sleep(1)
        # 输入密码
        self.driver.find_element_by_xpath('//div[@class="login_one"]//div//div/input[@id="pwd"]').send_keys('haijidema')
        time.sleep(1)
        # 验证码
        # 鼠标模拟操作
        action = ActionChains(self.driver)
        source = self.driver.find_element_by_xpath('//div[@class="login_one"]//div/div[@class="demo1"]/div[@class="slider"]/div/div[2]')  # 需要滑动的元素
        action.click_and_hold(source).perform()  # 鼠标左键按下不放
        time.sleep(0.5)
        action.move_by_offset(340, 0).perform()  # 需要滑动的坐标
        time.sleep(1)
        action.release().perform()  # 释放鼠标

        # 点击登陆
        time.sleep(2)
        self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div[1]/div/div[5]/a').click()
        time.sleep(2)
        for cookie in self.driver.get_cookies():
            self.driver.add_cookie(cookie)

    def request(self):

        url = 'https://member.zjtcn.com/getCurrentUser.json?t=%d' % (time.time()*1000)

        # data = {
        #     'method': 'login',
        #     'uid': '****',
        #     'pwd': '****',
        #     'remUser': '',
        #     'rememberMe': 'false',
        #     'isKick': '',
        #     'jsessionid': 'null',
        #     'domain': 'member.zjtcn.com',
        #     'flag': '1',
        #     'rollcode': '04S4lfTYe5',
        #     'date': 'Sat Jul 06 2019 09:58:27 GMT 0800 (中国标准时间)',
        # }

        cookies = {}
        for cookie in self.driver.get_cookies():
            cookies[cookie['name']] = cookie['value']
        cookies['UM_distinctid'] = '16bbcd39794598-0e8805cd158a6a-f353163-144000-16bbcd39795783'
        cookies['CNZZDATA1253678773'] = '2125991752-1562237545-https%253A%252F%252Fmember.zjtcn.com%252F%7C1562237545'
        cookies['SCLOSEDIALOG'] = '1'
        cookies['user_name'] = '****'
        cookies['Hm_lvt_a01b74f783ea1eda2c633ceefd483123'] = '1562237867,1562291638,1562336093,1562338363'

        self.result = self.session.post(url, headers=self.headers,cookies=cookies, verify=False).content

        with open('test.html', 'wb') as f:
            f.write(self.result)


if __name__ == '__main__':
    price = Price()
    price.login()
    price.request()



