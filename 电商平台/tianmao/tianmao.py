import requests
import urllib3
import time
import re
import json
import xlwt, xlrd
import random

from xlutils.copy import copy
from lxml import etree


class TianMao(object):
    def __init__(self, kw):
        # 必须有cookie，隔一段时间需要更换一次
        self.cookie = [
            # 'cna=353FFR0e5FsCAXa3WpLq0giz; lid=%E6%98%8E%E5%A4%A9%E4%B8%89%E5%8D%81%E4%BA%8C%E5%8F%B7; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _med=dw:1536&dh:864&pw:1920&ph:1080&ist:0; cq=ccp%3D1; _uab_collina=156440721124660449999582; enc=z0TfWvQ9HWXGg%2FRoa2MY2HYj2UfgrfgniIYK%2FEv2r%2FGt32csHyi8iBOmGabkyql62Uuf9%2BYrgcukKLieAnE%2FjA%3D%3D; _m_h5_tk=ae06e022ecd37ed837f8c6ccabdcff51_1564482053942; _m_h5_tk_enc=65b0453c52adae2ed1757fb84b5f10bb; OZ_1U_2061=vid=vd4005c2246af6.0&ctime=1564477834&ltime=1564477830; t=4a67cf0f54b38a06b12baa6d7011ac01; _tb_token_=ea53e6e85735e; cookie2=14a620e53b251ee3677e81d3172c3afa; x5sec=7b22746d616c6c7365617263683b32223a223739383534643662613432666337343063646138303437333431376135653738434a4f76674f6f46454b2f5774356d4477646d6536514561447a49794d444d774e7a49324d7a597a4d7a41374f413d3d227d; res=scroll%3A1519*5980-client%3A1519*722-offset%3A1519*5980-screen%3A1536*864; pnm_cku822=098%23E1hvuvvUvbpvUvCkvvvvvjiPRFFpgjimn2Fy0jivPmPWljtERFL9ljnhnLLhtjlPvphvC9mvphvvvvyCvhQvZvgRjc7NV1Iwwhdy0C9XHF%2BSBiVvVE01%2B2n79W9OjLeAnhjEKBmAdBIaUExrV8Tr%2B3%2BKacZ7%2Bu6fjoCn6Le6nqnKmWeYruh6%2B2E1Kphv8vvvphvvvvvvvvCVB9vvv7yvvhXVvvmCWvvvByOvvUhwvvCVB9vv9BAEvpvVvpCmpYspuphvmvvvpo6EFOyB2QhvCvvvMMGtvpvhvvCvp8wCvvpvvhHh; isg=BENDsMTmGuoYHdbDzFQUdrgA0gctENaSSYchWnUgHKIZNGJW_IulSmfmroTfry_y; l=cBSl_5s7qPUMADnbBOfZIuI8Ls7OoIRb8lVzw4OGjICP9Hf65JkGWZFYCHLBCnGVK6WBJ3oWYJ1kB2TNDyCqi7T2kX98ERC..',
            'cna=353FFR0e5FsCAXa3WpLq0giz; lid=%E6%98%8E%E5%A4%A9%E4%B8%89%E5%8D%81%E4%BA%8C%E5%8F%B7; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _med=dw:1536&dh:864&pw:1920&ph:1080&ist:0; cq=ccp%3D1; _uab_collina=156440721124660449999582; enc=z0TfWvQ9HWXGg%2FRoa2MY2HYj2UfgrfgniIYK%2FEv2r%2FGt32csHyi8iBOmGabkyql62Uuf9%2BYrgcukKLieAnE%2FjA%3D%3D; _m_h5_tk=ae06e022ecd37ed837f8c6ccabdcff51_1564482053942; _m_h5_tk_enc=65b0453c52adae2ed1757fb84b5f10bb; OZ_1U_2061=vid=vd4005c2246af6.0&ctime=1564477834&ltime=1564477830; t=4a67cf0f54b38a06b12baa6d7011ac01; _tb_token_=ea53e6e85735e; cookie2=14a620e53b251ee3677e81d3172c3afa; x5sec=7b22746d616c6c7365617263683b32223a226634383861306562386663636235666638313730383765366466623937396561434a2f41674f6f46454e766879746d67714a717361686f504d6a49774d7a41334d6a597a4e6a4d7a4d447334227d; res=scroll%3A1519*5914-client%3A1519*722-offset%3A1519*5914-screen%3A1536*864; pnm_cku822=098%23E1hvzvvUvbpvUvCkvvvvvjiPRFFpgj3RPsFWsjljPmPwsj18RsLv6j1Hn2Sv6jrPiQhvChCvCCpPvpvhvv2MMQhCvvXvppvvvvvEvpCWp8gov8WcbhyKoaV351rlBcanzWkfeeQ4b64B9CkaU6UsxI2hVB6AxsBCAfyprj6OVAdvaBTAVA6aWqVxnqW6cjYR1WoX5jiPahLv%2BbyCvm3vpvvvvvCvphCvVvvvvh8pphvOvvvvpAnvpC9vvvC2J6CvVvvvvhnquphvmhCvCbh3SIpDkphvCyEmmvofVFyCvvBvpvvv; l=cBSl_5s7qPUMANnoBOCN5uI8Ls7tjIRYjuPRwC0Xi_5dH686nJ7OkSEA8FJ6cjWd9rTp40tUd_v9-etksxToScGHtBUV.; isg=BISEd6xGhTc6gjGm5xFbG3PdVQK2NalvMgoGP54lGc8SySSTx69ilo9jCSG0auBf',
            # 'cna=353FFR0e5FsCAXa3WpLq0giz; lid=%E6%98%8E%E5%A4%A9%E4%B8%89%E5%8D%81%E4%BA%8C%E5%8F%B7; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _med=dw:1536&dh:864&pw:1920&ph:1080&ist:0; cq=ccp%3D1; _uab_collina=156440721124660449999582; enc=z0TfWvQ9HWXGg%2FRoa2MY2HYj2UfgrfgniIYK%2FEv2r%2FGt32csHyi8iBOmGabkyql62Uuf9%2BYrgcukKLieAnE%2FjA%3D%3D; _m_h5_tk=ae06e022ecd37ed837f8c6ccabdcff51_1564482053942; _m_h5_tk_enc=65b0453c52adae2ed1757fb84b5f10bb; OZ_1U_2061=vid=vd4005c2246af6.0&ctime=1564477834&ltime=1564477830; t=4a67cf0f54b38a06b12baa6d7011ac01; _tb_token_=ea53e6e85735e; cookie2=14a620e53b251ee3677e81d3172c3afa; res=scroll%3A1519*6098-client%3A1519*228-offset%3A1519*6098-screen%3A1536*864; pnm_cku822=098%23E1hvz9vUvbpvUpCkvvvvvjiPRFFpgjrPPsMUgjYHPmPpAjlEPFzZsjnvPLSvsjDPRsyCvvpvvvvvmphvLvkEM9vjOez9a4AAdcHCafmDYE9XJZFZ%2BneYr2E9ZRAn3w0AhjEUAXcBlLyzOvxr6jc6idv6cV0xfakKde3C%2BExr08TJEcqpaNmge34tvpvIvvvvvhCvvvvvvvWvphvvyQvvvQCvpvACvvv2vhCv2RvvvvWvphvWg8yCvv9vvUv0vyTsHIyCvvOUvvVva6WCvpvVvmvvvhCv2QhvCPMMvvm5vpvhvvmv99%3D%3D; isg=BEZGIXk-ZxGfkzOoydv5fcXHlzwID4sJBCCEsTBvc2lEM-dNnjXNcXyBCy9aoIJ5; l=cBSl_5s7qPUMALpBBOCwIuI8Ls79tIR4juPRwC0Xi_5pr1TskdQOkSe0Ne96cjWd94LM40tUd_v9-etlirV7OLcHtBUV.',
            # 'cna=353FFR0e5FsCAXa3WpLq0giz; lid=%E6%98%8E%E5%A4%A9%E4%B8%89%E5%8D%81%E4%BA%8C%E5%8F%B7; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _med=dw:1536&dh:864&pw:1920&ph:1080&ist:0; cq=ccp%3D1; _uab_collina=156440721124660449999582; enc=z0TfWvQ9HWXGg%2FRoa2MY2HYj2UfgrfgniIYK%2FEv2r%2FGt32csHyi8iBOmGabkyql62Uuf9%2BYrgcukKLieAnE%2FjA%3D%3D; _m_h5_tk=ae06e022ecd37ed837f8c6ccabdcff51_1564482053942; _m_h5_tk_enc=65b0453c52adae2ed1757fb84b5f10bb; OZ_1U_2061=vid=vd4005c2246af6.0&ctime=1564477834&ltime=1564477830; t=4a67cf0f54b38a06b12baa6d7011ac01; _tb_token_=ea53e6e85735e; cookie2=14a620e53b251ee3677e81d3172c3afa; res=scroll%3A1519*5980-client%3A1519*228-offset%3A1519*5980-screen%3A1536*864; pnm_cku822=098%23E1hvmvvUvbpvUpCkvvvvvjiPRFFpgjrPRLLW1jD2PmPW0jYERFcZlj3URFsp0jEjRLyCvvpvvvvv2QhvCPMMvvvCvpvVvmvvvhCvuphvmvvv92OmLsyDkphvC99vvOCzpqyCvm9vvvvvphvvvvvvvQCvpvmLvvv2vhCv2UhvvvWvphvWgvvvvQCvpvs9mphvLvBgOQvjwf0DyOvO5onmsX7vACyaWDNBlwethbUf8jc6D70XderESf7U%2BboJwyLZ%2BneYr2E9ZRAn3w0AhjECTWex6fItb9TxfwLwdiT5vpvhvvmv99%3D%3D; isg=BDs7w3cl4gIqNt7rtCyczvDYyh9lOE76EW8pMi34XjpRjFpusmEj4huOpmxnl6eK; l=cBSl_5s7qPUMApEsBOCwIuI8Ls7TtIR4juPRwC0Xi_5dP1TsFT_OkSe0xe96cjWd94Yw40tUd_v9-etlirV7OLcHtBUV.',
            # 'cna=353FFR0e5FsCAXa3WpLq0giz; lid=%E6%98%8E%E5%A4%A9%E4%B8%89%E5%8D%81%E4%BA%8C%E5%8F%B7; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _med=dw:1536&dh:864&pw:1920&ph:1080&ist:0; cq=ccp%3D1; _uab_collina=156440721124660449999582; enc=z0TfWvQ9HWXGg%2FRoa2MY2HYj2UfgrfgniIYK%2FEv2r%2FGt32csHyi8iBOmGabkyql62Uuf9%2BYrgcukKLieAnE%2FjA%3D%3D; _m_h5_tk=ae06e022ecd37ed837f8c6ccabdcff51_1564482053942; _m_h5_tk_enc=65b0453c52adae2ed1757fb84b5f10bb; OZ_1U_2061=vid=vd4005c2246af6.0&ctime=1564477834&ltime=1564477830; t=4a67cf0f54b38a06b12baa6d7011ac01; _tb_token_=ea53e6e85735e; cookie2=14a620e53b251ee3677e81d3172c3afa; res=scroll%3A1519*5914-client%3A1519*228-offset%3A1519*5914-screen%3A1536*864; pnm_cku822=098%23E1hvspvUvbpvUvCkvvvvvjiPRFFpgjrPn2FhQjthPmPwtjYEnLFUzjrPRsLy1j1EKphv8vvvphvvvvvvvvCVB9vvvjUvvhXVvvmCWvvvByOvvUhwvvCVB9vv9BAEvpvVvpCmpYspuphvmvvvpo6EnayHmphvLUCBQGWaaXp7%2Bul1B5c6%2Bu0Oe160D70Oe4g78BLUsEIfHF%2BSBiVvVE01%2B2n79WoOjLeAnhjEKBmAdBIaUU31K3kOeAXTlwmOVdhKnpZCvpvVvvBvpvvv2QhvCvvvMMGtvpvhvvCvp8wCvvpvvhHh; isg=BEpKJpw8I8XkBq80rfe9KemTmzAsk8_9mHR4TdSDVh0oh-hBvMropey1l7P-TEYt; l=cBSl_5s7qPUMAh7sBOfZCuI8Ls7OPIRbzlVzw4OGjICP9Z165JHdWZFYegLBCnGVK6VJR3oWYJ1kBfTFQyCqi7T2kX98ERC..',
        ]
        self.agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        ]
        self.headers = {
            'referer': 'https://www.tmall.com/',
            'user-agent': random.choice(self.agent),
            'cookie': random.choice(self.cookie),
        }
        # IP代理
        self.ip = [
            '117.191.11.110:8080',
            '39.137.69.6:80',
            '39.137.69.6:8080',
            '39.137.69.7:80',
            '39.137.69.6:8080',
        ]
        self.proxies = {
            'http': random.choice(self.ip)
        }
        # 简化后的搜索url
        self.shop_url = 'https://list.tmall.com/search_product.htm?q={keyword}&s={page}'
        # 搜索的商品
        self.keyword = kw
        self.page = 0

    def write_head(self):
        '''excel中写入表头'''
        try:
            self.read = xlrd.open_workbook('tianmao.xls', formatting_info=True)
            self.book = copy(self.read)
        except:
            self.book = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.book.add_sheet(self.keyword)
        self.head = ['详情链接', '商品', '店名', '价格/元', '月销量', '累计评论','评论标签','描述相符', '服务态度','物流评价','颜色选择','其他信息']  # 表头
        for h in range(len(self.head)):
            self.sheet.write(0, h, self.head[h])  # 写入表头

    def get_page_num(self):
        '''获取当前商品总共有多少个页面'''
        response = requests.get(self.shop_url.format(keyword=self.keyword,page=self.page),headers=self.headers,proxies=self.proxies,verify=False).content
        html = etree.HTML(response)
        try:
            page = html.xpath('//div[@id="J_Filter"]/p[@class="ui-page-s"]/b[@class="ui-page-s-len"]/text()')[0]
        except Exception as e:
            return 0
        else:
            # 提取的格式为 1/80
            return page.split('/')[1]

    def get_detail_url(self):
        '''获取页面中每个商品的链接'''
        pagenum = int(self.get_page_num())
        print('{}商品总共有{}页'.format(self.keyword,pagenum))
        if pagenum != 0:
            count = 1
            for page in range(0,pagenum):
                response = requests.get(self.shop_url.format(keyword=self.keyword,page=page*60),headers=self.headers,proxies=self.proxies,verify=False).content
                html = etree.HTML(response)
                infos = html.xpath('//*[@id="J_ItemList"]/div[contains(@class,"product")]')
                for info in infos:
                    item = {}
                    # 商店url
                    item['url'] = 'https:' + self.join_info(info.xpath('.//div[@class="productImg-wrap"]/a/@href'))
                    # 商品
                    item['goods'] = self.join_info(info.xpath('.//*[contains(@class,"productTitle")]/a/text()'))
                    # 店名
                    item['shop_name'] = self.join_info(info.xpath('.//div[@class="productShop"]/a/text()'))
                    # 价格
                    item['price'] = self.str2num(self.join_info(info.xpath('.//p[@class="productPrice"]/em/@title')))
                    # 销售量
                    item['sale'] = self.join_info(info.xpath('.//p[@class="productStatus"]/span/em/text()'))

                    self.get_detail_page(item,count)
                    time.sleep(0.5)
                    count += 1

                print('{}商品第{}页下载完成！'.format(self.keyword,page+1))
        else:
            print('未查找到输入的商品！')

    def get_detail_page(self,item,count):
        # 商品详情页提取信息
        response = requests.get(item['url'],headers=self.headers,proxies=self.proxies,verify=False).content
        content = etree.HTML(response)
        # 获取商品id
        id = re.match(r'https://detail.tmall.com/item.htm\?id=(\d+)&', item['url']).group(1)
        # # 评论数
        item['comment'] = self.str2num(self.get_comment_count(id))
        # 评论标签
        item['comment_tag'] = self.get_comment_info(id)

        comment_shop = content.xpath('//div[@id="shop-info"]//div[@class="shopdsr-item"]//span/text()')
        # 描述
        if len(comment_shop) == 0:
            comment_shop = ['','','']
        item['desc'] = self.str2num(comment_shop[0])
        # 服务
        item['service'] = self.str2num(comment_shop[1])
        # 快递
        item['express'] = self.str2num(comment_shop[2])
        # 颜色选择
        item['color'] = self.join_list(content.xpath('//div[@id="J_DetailMeta"]//div[@class="tb-property"]//div[@class="tb-sku"]/dl[@class="tb-prop tm-sale-prop tm-clear tm-img-prop "]//li//span/text()'))
        # 其他信息
        item['other_info'] = self.join_list(content.xpath('//div[@id="J_DetailMeta"]//div[@class="tb-property"]//div[@class="tb-sku"]/dl[@class="tb-prop tm-sale-prop tm-clear "]//ul/li//span/text()'))

        self.write_xlsx(item,count)
        print(item)

    def get_comment_count(self,id):
        '''获取累计评论总数'''
        count_url = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId={}&spuId=1158440898&sellerId=1842930643&groupId&_ksTS=1564400577489_236&callback=jsonp237'.format(id)
        response = requests.get(count_url, headers=self.headers,proxies=self.proxies,verify=False).text
        count = self.join_info(re.findall(r'"rateTotal":(\d+)', response))
        return count

    def get_comment_info(self,id):
        '''获取评论中大家都写到的内容'''
        comment_url = 'https://rate.tmall.com/listTagClouds.htm?itemId={}&isAll=true&isInner=true&t={}&groupId=&callback=jsonp1454'.format(id,int(time.time()*1000))
        response = requests.get(comment_url, headers=self.headers,proxies=self.proxies,verify=False).text
        try:
            com = json.loads(re.findall(r'jsonp1454\({"tags":(.*)}\)',response)[0])
        except Exception as e:
            return ''
        else:
            tagclouds = com.get('tagClouds')
            tags = []
            for tagcloud in tagclouds:
                tags.append(tagcloud.get('tag'))
            return self.join_list(tags)

    @staticmethod
    def join_list(res):
        '''对提取到的列表信息进行拼接'''
        return '|'.join(res)

    @staticmethod
    def join_info(res):
        '''对提取到的列表信息进行拼接'''
        return ''.join(res).strip()

    @staticmethod
    def str2num(res):
        '''对提取到的信息进行数据转换'''
        if len(res) != 0:
            return float(res)
        else:
            return 0

    def write_xlsx(self,content,num):
        '''将数据写入到excel中'''
        j = 0
        for key, value in content.items():
            self.sheet.write(num, j, value)
            j += 1
        self.book.save('tianmao.xls')

    def main(self):
        self.write_head()
        self.get_detail_url()


if __name__ == '__main__':
    urllib3.disable_warnings()
    key = input('请输入商品名：')
    tm = TianMao(key)
    tm.main()
