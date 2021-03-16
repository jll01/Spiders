import requests
import urllib3
import re
import random
import time
import os

from lxml import etree
from fontTools.ttLib import TTFont
from fake_useragent import UserAgent


class Movie(object):
    def __init__(self, page_num):
        # 网页每次请求变化偏差值
        self.offset = 0
        # 总共要提取的页数
        self.page = page_num
        # 请求url
        self.url = 'https://maoyan.com/films?showType=3&offset={}'
        self.headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'maoyan.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': UserAgent().random,
        }

    def movie_url(self):
        # 发起请求正则提取到每部电影的详情url
        req = requests.get(self.url.format(self.offset), headers=self.headers, verify=False)
        urls = re.findall(r'''<a href="(.*?)" target="_blank" data-act="movie-click" data-val="{movieid:\d+}">''', req.text)
        return urls

    def fonts_file(self, url):
        # 正则提取字体文件
        response = requests.get(url, headers=self.headers, verify=False).text
        # 正则匹配字体文件
        try:
            font_file = re.findall(r'''vfile\.meituan\.net\/colorstone\/(\w+\.woff)''', response)[0]
        except Exception as err:
            print('字体文件匹配错误：{}'.format(err))
            return '', ''
        else:
            return font_file, response

    def detail_data(self, resp, new_num):
        # 获取电影详情数据
        item = {}
        html = etree.HTML(resp)
        # 标题
        item['title'] = ''.join(html.xpath('//div[@class="movie-brief-container"]/h3/text()'))
        # 其他名称
        item['rename'] = ''.join(html.xpath('//div[@class="movie-brief-container"]/div[@class="ename ellipsis"]/text()'))
        # 剧情分类
        item['classify'] = ''.join(html.xpath('//li[@class="ellipsis"][1]/text()'))
        # 地区和电影时长
        time_addr = self.get_movie_time(html.xpath('//li[@class="ellipsis"][2]/text()'))
        item['addr'] = time_addr[0]
        item['movie_time'] = time_addr[1]
        # 上映地区和时间
        item['show_addr'] = ''.join(html.xpath('//li[@class="ellipsis"][3]/text()'))
        # 演员
        item['actor'] = '|'.join(html.xpath('//div[@class="module"]/div[@class="mod-content"]//div[@class="celebrity-group"]//a[@class="name"]/text()')).replace('\n', '').replace(' ', '')
        # 评分
        star = ''.join(re.findall(r'''<span class="index-left info-num ">\s+<span class="stonefont">(.*?)</span>\s+</span>''', resp))
        item['star'] = self.change_num(star, new_num)
        # 评论的人数
        people = ''.join(re.findall(r'''<span class='score-num'><span class="stonefont">(.*?)</span>.*?</span>''', resp))
        item['people'] = self.change_num(people, new_num)
        # 累计票房
        ticket_number = re.findall(r'''<span class="stonefont">(.*?)</span><span class="unit">(.*?)</span>''', resp)
        if len(ticket_number) != 0:
            item['ticket_number'] = self.change_num(''.join(ticket_number[0]), new_num)
        else:
            item['ticket_number'] = 'Null'
        # 简介
        item['brief_introduction'] = ''.join(html.xpath('//div[@class="module"]/div[@class="mod-content"]/span[@class="dra"]/text()'))
        # 海报
        item['image'] = ''.join(html.xpath('//div[@class="celeInfo-left"]/div[@class="avatar-shadow"]/img/@src'))

        return item

    @staticmethod
    def get_movie_time(res):
        # 提取电影地区和电影时长
        res = ''.join(res).split()
        if len(res) > 1:
            return res[0], res[-1]
        else:
            return res[0], ''

    @staticmethod
    def create_font(font_file):
        # 下载字体文件并保存到xml格式
        headers = {
            'User-Agent': UserAgent().random,
        }
        # 列出已下载文件
        file_list = os.listdir('./fonts')
        # 判断是否已下载
        if font_file not in file_list:
            # 未下载则下载新库
            url = 'http://vfile.meituan.net/colorstone/' + font_file
            new_file = requests.get(url, headers=headers, verify=False).content
            with open('./fonts/' + font_file, 'wb') as f:
                f.write(new_file)

        # 打开字体文件和保存
        new_font = TTFont('./fonts/' + font_file)
        new_font.saveXML('./fonts/{}.xml'.format(font_file))
        return new_font

    def modify_html(self, new_font):
        # 解密新字体文件中的加密字体代表的数值
        # 作为基准字体
        basefont = TTFont(r'.\base_font.woff')
        # 获取到uni节点
        uni_list = new_font['cmap'].tables[0].ttFont.getGlyphOrder()
        # 基准字体文件中数字和对应的编码
        base_num = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        base_unicode = [
            'uniE817', 'uniE52C', 'uniF083', 'uniE52F', 'uniEB37', 'uniEE1C', 'uniE902', 'uniE647', 'uniE5ED', 'uniF438'
        ]
        # 存储新字体文件中最后的编码和对应的数值
        finally_all = {}
        # 剔除掉前两个没用的编码
        for i in range(2, len(uni_list)):
            # glyf是字形表，记录文字笔画等， 获取新字体的笔画坐标和对应的0(弧形区域)和1(矩形区域)
            new_glyph = new_font['glyf'][uni_list[i]].coordinates
            new_flag = new_font['glyf'][uni_list[i]].flags
            # 保存新文件中各个字体编码与基准字体坐标相同或者坐标差值在一定范围内的个数
            num_list = []
            for j in range(len(base_unicode)):
                # 基准字体文件的字体坐标和0、1
                base_glyph = basefont['glyf'][base_unicode[j]].coordinates
                base_flag = basefont['glyf'][base_unicode[j]].flags
                # 获取新文件中各个字体编码与基准字体坐标相同或者坐标差值在一定范围内的个数
                num = self.compare(new_glyph, new_flag, base_glyph, base_flag)
                num_list.append({'name': base_unicode[j], 'num': num})

            # 对num_list按照字典的num值排序，选出num最大的值对应的编码在字体基准文件中对应的名称
            finally_tag = sorted(num_list, key=lambda x:x['num'])[-1].get('name')
            # 获取finally_tag在基准文件中对应的数字
            number = base_num[base_unicode.index(finally_tag)]
            # 将字体文件中的编码替换为html中的格式
            finally_all.update({uni_list[i].replace('uni', '&#x').lower() + ";": number})

        return finally_all

    @staticmethod
    def change_num(con, new_num):
        # 将html中加密的字体替换为对应的数字
        for key, value in new_num.items():
            if key in con:
                con = con.replace(key, new_num[key])
        return con

    @staticmethod
    def compare(new_glyph, new_flag, base_glyph, base_flag):
        # 获取新文件中各个字体编码与基准字体坐标相同或者坐标差值在一定范围内的个数
        num = 0
        for i in range(len(base_flag)):
            for j in range(len(new_flag)):
                if new_flag[j] == base_flag[i] and abs(new_glyph[j][0]-base_glyph[i][0]) <= 15 and abs(new_glyph[j][1]-base_glyph[i][1]) <= 15:
                    num += 1
        return num

    def main(self):
        while self.offset <= (self.page-1) * 30:
            # 获取详情url
            urls = self.movie_url()
            for url in urls:
                # 获取字体文件
                font_file, response = self.fonts_file('https://maoyan.com' + url)
                if font_file == '' or response == '':
                    break
                # 下载保存字体文件
                new_font = self.create_font(font_file)
                # 解密字体
                new_num = self.modify_html(new_font)
                # 获取详情
                data = self.detail_data(response, new_num)
                print(data)
            print('----------第{}页提取完成！----------'.format(int(self.offset/30 + 1)))
            self.offset += 30
            time.sleep(random.uniform(3, 5))


if __name__ == '__main__':
    urllib3.disable_warnings()

    page = input('请输入爬取的页数：').strip()
    if page.isalnum():
        mv = Movie(int(page))
        mv.main()
    else:
        print('请检查输入是否是数字！')
