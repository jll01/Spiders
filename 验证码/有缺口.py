from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
import requests
import time
import re
import random
from io import BytesIO


class JiYanCode(object):
    def __init__(self):
        self.count = 1  # 最多识别6次
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_drive = r'D:\soft\Chrome\chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chrome_drive,options=chrome_options)
        self.driver.get('http://www.cnbaowen.net/api/geetest/')

    def merge_image(self,image_file, location_list):
        """拼接图片"""
        im = Image.open(image_file)
        im.save('code.jpg')
        new_im = Image.new('RGB', (260, 116))
        # 把无序的图片 切成52张小图片
        im_list_upper = []
        im_list_down = []
        for location in location_list:
            if location['y'] == -58:  # 上半边
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 116)))
            if location['y'] == 0:  # 下半边
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))  # 把小图片放到 新的空白图片上
            x_offset += im.size[0]

        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]
        return new_im

    def get_image(self, div_path):
        '''下载无序的图片  然后进行拼接 获得完整的图片'''
        time.sleep(2)
        background_images = self.driver.find_elements_by_xpath(div_path)
        location_list = []
        for background_image in background_images:
            location = {}
            result = re.findall('background-image: url\("(.*?)"\); background-position: (.*?)px (.*?)px;',background_image.get_attribute('style'))
            location['x'] = int(result[0][1])
            location['y'] = int(result[0][2])

            image_url = result[0][0].replace('webp', 'jpg')
            location_list.append(location)

        image_result = requests.get(image_url).content
        image_file = BytesIO(image_result)  # 是一张无序的图片
        image = self.merge_image(image_file, location_list)

        return image

    def get_track(self,distance):
        '''拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速'''
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(3, 5)  # 加速运动
            else:
                a = -random.randint(1, 3)  # 减速运动
            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))
            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t
        # 反着滑动到大概准确位置
        tracks.append(distance - sum(tracks) + random.randint(-3, 3))
        return tracks

    def get_distance(self,image1, image2):
        '''拿到滑动验证码需要移动的距离'''
        threshold = 50
        for i in range(0, image1.size[0]):  # 260
            for j in range(0, image1.size[1]):  # 160
                pixel1 = image1.getpixel((i, j))
                pixel2 = image2.getpixel((i, j))
                res_R = abs(pixel1[0] - pixel2[0])  # 计算RGB差
                res_G = abs(pixel1[1] - pixel2[1])  # 计算RGB差
                res_B = abs(pixel1[2] - pixel2[2])  # 计算RGB差
                if res_R > threshold and res_G > threshold and res_B > threshold:
                    return i  # 需要移动的距离

    def main_check_code(self, element):
        """拖动识别验证码"""
        image1 = self.get_image('//div[@class="gt_cut_bg gt_show"]/div')
        image2 = self.get_image('//div[@class="gt_cut_fullbg gt_show"]/div')
        # 对比两张图片的所有RBG像素点，得到不一样像素点的x值，即要移动的距离
        l = self.get_distance(image1, image2)
        print('缺口距离{}'.format(l))
        # 获得移动轨迹
        track_list = self.get_track(l)
        print('第一步,点击滑动按钮')
        ActionChains(self.driver).click_and_hold(on_element=element).perform()  # 点击鼠标左键，按住不放
        time.sleep(1)
        print('第二步,拖动元素')
        for track in track_list:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
        ActionChains(self.driver).move_by_offset(xoffset=-random.randint(3, 5), yoffset=0).perform()
        time.sleep(1)
        print('第三步,释放鼠标')
        ActionChains(self.driver).release(on_element=element).perform()
        time.sleep(1.5)

    def main_check_slider(self):
        """检查滑动按钮是否加载"""
        try:
            element = WebDriverWait(self.driver, 10, 0.5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'gt_slider_knob')))
            if element:
                return element
        except Exception as e:
            print('错误{}'.format(e))

    def main(self):
        try:
            # 等待滑动按钮加载完成
            element = self.main_check_slider()
            while self.count <= 6:
                print('-----第{}次识别!-----'.format(self.count))
                self.main_check_code(element)
                try:
                    success_element = (By.CSS_SELECTOR, '.gt_holder .gt_ajax_tip.gt_success')
                    success_images = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(success_element))
                    if success_images:
                        print('成功识别！！！！！！')
                        break
                except Exception as e:
                    print('识别错误，继续')
                    self.count += 1
                    time.sleep(1)
            else:
                print('too many attempt check code ')
                exit('退出程序')
        except Exception as e:
            print('出错了!请检查程序!')


if __name__ == '__main__':
    jy = JiYanCode()
    jy.main()
