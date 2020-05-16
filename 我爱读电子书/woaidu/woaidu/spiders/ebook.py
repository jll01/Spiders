# -*- coding: utf-8 -*-
import scrapy
import re
import time

from woaidu.items import WoaiduItem


class EbookSpider(scrapy.Spider):
    name = 'ebook'
    allowed_domains = ['woaidu.org']

    start_url = 'https://www.woaidu.org/dushi_s1.html'
    start_urls = [start_url]

    def parse(self, response):
        '''获取每一页每本书的url'''
        count_url = {
            'xuanhuan': [1, 669, '玄幻奇幻'],
            'wuxia': [1, 195, '武侠仙侠'],
            'dushi': [1, 473, '现代都市'],
            'yanqing': [1, 1645, '精品言情'],
            'kehuan': [1, 237, '科幻灵异'],
            'wangyou': [1, 80, '网游竞技'],
            'tongren': [1, 67, '耽美同人'],
            'lishi': [1, 246, '历史军事'],
            'mingzhu': [1, 55, '中外名著'],
            'zhuanji': [1, 8, '人物传记'],
            'qita': [1, 493, '其他']
        }
        ebook_lists = response.xpath('//div[@class="goodBookList"]//ul/li')
        url = response.request.url  # 'https://www.woaidu.org/kehuan_s1.html'
        leixing = re.match(r'https://www.woaidu.org/(.*?)_s\d+?.html', url)[1]
        for ebook_list in ebook_lists:
            ebook_url = 'https://www.woaidu.org' + ebook_list.xpath('.//a[1]/@href').extract()[0]
            yield scrapy.Request(ebook_url, callback=self.get_detail, meta={'classify': count_url[leixing][2]})

        num_list = count_url[leixing]
        if num_list[0] < num_list[1]:
            num_list[0] += 1
            next_url = re.match(r'(.*)\d+?(.html)', url)
            ebook_url = next_url[1] + str(num_list[0]) + '.html'
            yield scrapy.Request(ebook_url, callback=self.parse)

    def get_detail(self, response):
        '''获取每本书的具体内容'''
        ebook = WoaiduItem()
        ebook['classify'] = response.meta['classify']
        # ebook['classify'] = '科幻灵异'
        ebook_content = response.xpath('//div[@class="index-section"]')
        title = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/h1/text()').extract()
        if len(title) == 0:
            ebook['title'] = ''
        else:
            ebook['title'] = title
        ebook['ebook_url'] = 'https://www.woaidu.org' + ebook_content.xpath('.//div[@class="commom-description fl"]/a/@href').extract()[0]
        ebook['author'] = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[2]/text()').extract()[0].strip()[3:]
        # ebook['type'] = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[3]/text()').extract()[0].strip()[3:]
        ebook['protagonist'] = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[4]/text()').extract()[0].strip()[5:]
        ebook['comment_count'] = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[5]/text()').extract()[0].strip()[3:]
        ebook['update_time'] = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[6]/text()').extract()[0].strip()[3:]
        ebook['profile'] = ebook_content.xpath('.//div[@class="production producct-Message"]/p/text()').extract()[0]

        about_urls = ebook_content.xpath('.//div[@class="production producct-Message"]/div[@class="booklist-top Prerelease"]/ul/li')
        urls_list = []
        for about_url in about_urls:
            urls_list.append('https://www.woaidu.org' + about_url.xpath('.//a[1]/@href').extract()[0])
        ebook['about_url'] = ','.join(urls_list)
        ebook['download_url'] = ebook_content.xpath('.//div[@class="production producct-Message"]/ul[@class="dataList"]/li[1]/a[2]/@href').extract()
        if len(ebook['download_url']) == 0:
            ebook['download_url'] = ''
        else:
            ebook['download_url'] = ebook['download_url'][0]

        wonderful_chapter_1 = ebook_content.xpath('.//div[@class="production producct-Message"][4]/p/text()').extract()
        wonderful_chapter_2 = ebook_content.xpath('.//div[@class="production producct-Message"]/div[@class="fold-box2"]/p/text()').extract()
        wonderful_chapter_1.extend(wonderful_chapter_2)
        ebook['wonderful_chapters'] = ''.join(wonderful_chapter_1).replace('\xa0','')

        latest_chapter_1 = ebook_content.xpath('.//div[@class="production producct-Message"][5]/p/text()').extract()
        latest_chapter_2 = ebook_content.xpath('.//div[@class="production producct-Message"][5]/div[@class="fold-box"]/p/text()').extract()
        latest_chapter_1.extend(latest_chapter_2)
        ebook['latest_chapters'] = ','.join(latest_chapter_1).replace('\xa0','')
        print(ebook['title'],ebook['ebook_url'])

        yield ebook
