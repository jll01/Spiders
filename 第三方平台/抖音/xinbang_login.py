import time
import json
import datetime
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from threading import Thread


def open_browser():
    """
    打开本地代理的浏览器
    @return:
    """
    s = 'cd /d C:\Program Files (x86)\Google\Chrome\Application&&chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Selenium\AutomationProfile"'
    os.system(s)


def login(l_phone, password):
    print('正在创建模拟浏览器，请稍后！')
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    # 防止服务器识别是模拟登陆
    webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 谷歌driver
    driver = webdriver.Chrome(executable_path=r'./driver/chromedriver.exe', options=options)
    # 浏览器窗口最大化
    driver.maximize_window()
    print('创建完成！')
    while True:
        driver.get('https://www.newrank.cn/user/login')
        time.sleep(3)
        WebDriverWait(driver, 20, 0.05).until(lambda x: x.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[2]/div/div[1]/div[3]/span[1]')).click()
        WebDriverWait(driver, 20, 0.05).until(lambda x: x.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[1]/input')).send_keys(l_phone)
        WebDriverWait(driver, 20, 0.05).until(lambda x: x.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/span/input')).send_keys(password)
        WebDriverWait(driver, 20, 0.05).until(lambda x: x.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[4]/button')).click()

        # 拖动滑块
        action = ActionChains(driver)
        # 滑块的id
        start = WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('//*[contains(@id, "n1z")]'))
        # 长按
        action.click_and_hold(start)
        # 滑动滑块
        action.drag_and_drop_by_offset(start, 286, 0).perform()
        ActionChains(driver).release().perform()
        time.sleep(2)
        try:
            WebDriverWait(driver, 5, 0.05).until(lambda x: x.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[4]/button'))
        except:
            get_cookie_driver = driver.get_cookies()
            cookie_dict = {}
            for cookie in get_cookie_driver:
                cookie_dict[cookie['name']] = cookie['value']
            cookie = [f'{item[0]}={item[1]}' for item in cookie_dict.items()]
            cookie = '; '.join(cookie)
            break
        else:
            time.sleep(2)

    date = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    with open(f'xinbang_cookie.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps({'date': date, 'cookie': cookie}, ensure_ascii=False))


def main(phone, passwd):
    t1 = Thread(target=open_browser)
    t1.start()

    t2 = Thread(target=login, args=(phone, passwd))
    t2.start()

    t1.join()
    t2.join()
