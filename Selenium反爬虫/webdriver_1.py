import os
import time

from selenium import webdriver
from threading import Thread


def login():
    """
    创建模拟登陆所需的浏览器
    @return: 浏览器驱动对象
    """
    print('正在创建模拟浏览器，请稍后！')
    try:
        os.system('rd /s /q C:\Selenium')
    except:
        pass
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    # 防止服务器识别是模拟登陆
    webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 谷歌driver
    driver = webdriver.Chrome(executable_path=r'chromedriver.exe', options=options)
    # 浏览器窗口最大化
    driver.maximize_window()
    driver.delete_all_cookies()

    print('创建完成！')

    driver.get('https://www.baidu.com/')
    time.sleep(3)
    driver.quit()

    ret = os.popen("netstat -nao|findstr " + str(9222))
    str_list = ret.readlines()
    for i in str_list:
        if 'LISTENING' in i:
            pid = i.strip().split()[-1]
            os.popen(f'taskkill /pid {pid} /F')
            print("端口已被释放")


def open_browser():
    """
    打开本地代理的浏览器
    @return:
    """
    s = 'cd /d C:\Program Files (x86)\Google\Chrome\Application&&chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Selenium\AutomationProfile"'
    os.system(s)


if __name__ == '__main__':
    t1 = Thread(target=open_browser)
    t1.start()

    t2 = Thread(target=login)
    t2.start()

    t1.join()
    t2.join()
