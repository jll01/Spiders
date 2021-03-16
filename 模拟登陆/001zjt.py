import time
import xlwt, xlrd

from xlutils.copy import copy
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
from selenium.webdriver.chrome.options import Options


class Price(object):
    def __init__(self):
        # chrome_options = Options()
        # chrome_options.binary_location = r"D:\soft\Browser\Google\chrome.exe"
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--headless')
        # # browser = webdriver.Chrome(chrome_options=chrome_options)

        self.chrome_drive = '****'
        self.driver = webdriver.Chrome(executable_path=self.chrome_drive)

        self.name = input('请输入年份月份(如：201803)：')
        try:
            self.read = xlrd.open_workbook(self.name[:4] + '.xls', formatting_info=True)
            self.book = copy(self.read)
        except:
            self.book = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.book.add_sheet(self.name)
        self.head = ['名称', '型号', '单位', '价格/元', '日期', '涨跌', '走势图', '来源']  # 表头
        for h in range(len(self.head)):
            self.sheet.write(0, h, self.head[h])  # 写入表头

    def login(self):
        login_url = 'https://yn.zjtcn.com/ration/d{}_t_p1.html'.format(self.name)
        self.driver.get(login_url)
        # 最大界面
        self.driver.maximize_window()
        # 点击登陆进入登陆页面
        pages = self.driver.find_element_by_link_text("【 登录 】")
        self.driver.execute_script("arguments[0].click();", pages)

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
        # action.reset_actions()
        time.sleep(0.2)
        action.move_by_offset(340, 0).perform()  # 需要滑动的坐标
        time.sleep(1)
        action.release().perform()  # 释放鼠标
        # ActionChains(self.driver).drag_and_drop_by_offset(source, 340, 0).perform()

        # 点击登陆
        time.sleep(3)
        self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div[1]/div/div[5]/a').click()
        time.sleep(2)

    def download(self):
        num = 1
        while True:
            res = etree.HTML(self.driver.page_source)
            results = res.xpath('//div[@class="moudle-date-box"]/table[@id="rationTable"]//tr')[1:]

            for result in results:
                content = {}
                content['名称'] = result.xpath('./td[2]/a/@title')[0].strip()
                content['型号'] = result.xpath('./td[3]/text()')[0].strip()
                content['单位'] = result.xpath('./td[4]/text()')[0].strip()
                content['价格/元'] = float(result.xpath('./td[5]/text()')[0].strip())
                content['日期'] = result.xpath('./td[6]/text()')[0].strip()

                class_span = result.xpath('./td[7]/span/@class')
                if len(class_span) != 0:
                    if class_span[0] == 'icon-falling':
                        content['涨跌'] = '跌' + result.xpath('./td[7]/text()')[0]
                    elif class_span[0] == 'icon-rose':
                        content['涨跌'] = '涨' + result.xpath('./td[7]/text()')[0]
                else:
                    content['涨跌'] = result.xpath('./td[7]/span/text()')[0]

                content['走势图'] = 'https://yn.zjtcn.com' + result.xpath('./td[8]/a/@href')[0]
                content['来源'] = result.xpath('./td[9]/text()')[0].strip()
                # print(content)
                # self.write.append(content)
                self.write_xlsx(num, content)
                print('第{}条数据下载完成！'.format(num))
                num += 1

            if num < 1036:
                # num += 1
                self.driver.find_element_by_link_text("下一页").click()
                time.sleep(0.5)

                # pages = self.driver.find_element_by_link_text("下一页").click()
                # self.driver.execute_script("arguments[0].click();", pages)
            else:
                break

    def write_xlsx(self,num, content):
        # i = 1
        # for data_dict in self.write:
        j = 0
        for key, value in content.items():
            self.sheet.write(num, j, value)
            j += 1
        self.book.save(self.name[:4] + '.xls')


if __name__ == '__main__':
    p = Price()
    start = time.time()
    p.login()
    time.sleep(2)
    p.download()
    # p.write_xlsx()
    print(time.time()-start)
