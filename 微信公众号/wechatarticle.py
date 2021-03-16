import requests
import time
import urllib3
import re

from lxml import etree


class WeChatArticle(object):
    def __init__(self, key):
        self.queryurl = 'https://weixin.sogou.com/weixin?query={}&type=2&page={}&ie=utf8'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            'Cookie': 'IPLOC=CN6211; SUID=50B3B6762013940A000000005D69E033; SUV=1567219761766858; ABTEST=0|1567219767|v1; weixinIndexVisited=1; usid=50B3B676AD3E990A000000005D6A3D61; sg_uuid=5527092104; sw_uuid=8760800765; ssuid=5768560160; ld=tlllllllll2Nz0CulllllVCsJ4DlllllNrz8Ulllll9lllllxllll5@@@@@@@@@@; LSTMV=576%2C396; LCLKINT=35278; SNUID=F81A1EDFA8AD391ADB70472EA9C7505C; JSESSIONID=aaa-Gqtzplr5bfXsFi7Yw; sct=18',
        }
        self.proxies = {
            'http': '39.137.69.7:8080',
        }
        self.session = requests.session()
        self.page = 1
        self.key = key
        self.req_url = 'https://weixin.sogou.com/weixin?query={}'

    def requestpage(self):
        pagenum = self.getpagenum()
        # pagenum = 1
        while pagenum >0 and self.page <= pagenum:
            url = self.queryurl.format(self.key, self.page)
            page = self.session.get(url, headers=self.headers, verify=False).text
            with open('test.html', 'w', encoding='utf-8') as f:
                f.write(page)
            num = ''.join(re.findall(r'<div class="mun">找到约(.*?)条结果',page)).replace(',','')
            print(num)
            title = re.findall(r'<h3>\n<a target="_blank" .*?">(.*?)</a>\n</h3>',page)
            url =  re.findall(r'<a target="_blank" .*?data-share="(.*)"',page)
            abstract = re.findall(r'<p class="txt-info" .*?>(.*?)</p>', page)
            name = re.findall(r'<a class="account" .*?>(.*?)</a>',page)
            pushtime = re.findall(r"document.write\(timeConvert\('(\d+)'\)\)",page)
            image = re.findall(r'<a data-z="art" .*?><img src="(.*?)".*',page)

            for title,url,abstract,name,pushtime,image in zip(title,url,abstract,name,pushtime,image):
                item = {}
                item['title'] = title.replace('<em><!--red_beg-->','').replace('<!--red_end--></em>','').replace('&ldquo','')
                item['url'] = url
                item['image'] = 'http:' + image
                item['abstract'] = abstract.replace('<em><!--red_beg-->','').replace('<!--red_end--></em>','').replace('&ldquo','').replace('&rdquo','')
                item['pushtime'] = self.changetime(pushtime)
                item['name'] = name
                wechat = self.wechatid(name)
                item.update(wechat)

                print(item)

            time.sleep(5)
            self.page += 1

    def changetime(self,old):
        unixtime = ''.join(old)
        try:
            if len(unixtime) != 0:
                return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(unixtime)))
            else:
                return ''
        except:
            return ''

    def getpagenum(self):
        url = self.queryurl.format(self.key, self.page)
        page = self.session.get(url, headers=self.headers, verify=False).text
        num = ''.join(re.findall(r'<div class="mun">找到约(.*?)条结果', page)).replace(',', '')
        try:
            return int(num)
        except:
            return 0

    def wechatid(self,name):
        pagecontent = requests.get(self.req_url.format(name), headers=self.headers, verify=False).text
        html = etree.HTML(pagecontent)
        contents = html.xpath('//div[@class="news-box"]/ul/li')

        we = {}
        for content in contents:
            wechatname = ''.join(content.xpath('./div[@class="gzh-box2"]/div[@class="txt-box"]/p[@class="tit"]/a/em/text()')) + ''.join(content.xpath('./div[@class="gzh-box2"]/div[@class="txt-box"]/p[@class="tit"]/a/text()'))
            if wechatname == name:
                item = {}
                item['wechatid'] = ''.join(content.xpath('./div[@class="gzh-box2"]/div[@class="txt-box"]/p[@class="info"]/label[@name="em_weixinhao"]/text()'))
                item['introduce'] = ''.join(content.xpath('./dl[1]/dd/em/text()')) + ''.join(content.xpath('./dl[1]/dd/text()'))
                item['renzheng'] = ''.join(content.xpath('//div[@class="news-box"]/ul/li[1]/dl[2]/dd/text()')).replace('\n', '')
                item['image'] = 'https:' + ''.join(content.xpath('./div[@class="gzh-box2"]/div[@class="img-box"]/a/img/@src'))
                return  item
            else:
                we['wechatid'] = ''
                we['introduce'] = ''
                we['renzheng'] = ''
                we['image'] = ''

        return we

    def main(self):
        self.requestpage()


if __name__ == '__main__':

    urllib3.disable_warnings()

    # key = input('请输入要查找到的文章名称：')
    key = '中国电信'
    wa = WeChatArticle(key)
    wa.main()

