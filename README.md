# 平常练习的一些爬虫

|     网站/手机软件     |          爬虫          |     工具/库     |
| :-------------: | :-----------------------: | :--------------: |
| [3D福利彩票](https://github.com/jll01/Spiders/tree/master/3D%E7%A6%8F%E5%88%A9%E5%BD%A9%E7%A5%A8 "3D福利彩票")  | 获取3D福利彩票历年数据并简单的绘图 | threading、pymysql、re... |
| [小红书](https://github.com/jll01/Spiders/tree/master/APP%E6%8A%93%E5%8C%85/%E5%B0%8F%E7%BA%A2%E4%B9%A6 "小红书")  | 下载小红书视频并保存视频相关的数据 | threading、pymysql、queue、requests、Fiddler... |
| [快手](https://github.com/jll01/Spiders/tree/master/APP%E6%8A%93%E5%8C%85/%E5%BF%AB%E6%89%8B "快手")  | 下载快手短视频并保存视频相关的数据 | threading、requests、Fiddler... |
| [抖音](https://github.com/jll01/Spiders/tree/master/APP%E6%8A%93%E5%8C%85/%E6%8A%96%E9%9F%B3 "抖音")  | 通过app/分享url下载抖音短视频并保存视频相关的数据 | threading、pymysql、requests、Fiddler、夜神模拟器... |
| [斗鱼](https://github.com/jll01/Spiders/tree/master/APP%E6%8A%93%E5%8C%85/%E6%96%97%E9%B1%BC "斗鱼")  | 通过api获取斗鱼app主播房间号、时间等数据 | pymysql... |
| [百思不得其姐](https://github.com/jll01/Spiders/tree/master/APP%E6%8A%93%E5%8C%85/%E7%99%BE%E6%80%9D%E4%B8%8D%E5%BE%97%E5%85%B6%E5%A7%90 "百思不得其姐")  | 获取分享数、点赞数等| requests... |
| [美团](https://github.com/jll01/Spiders/tree/master/APP%E6%8A%93%E5%8C%85/%E7%BE%8E%E5%9B%A2 "美团")  | 先要获取到城市的ID, 根据输入的城市查询到ID后提取每个城市中餐厅的名称、地址等信息 | pymysql、requests... |
| [链家](https://github.com/jll01/Spiders/tree/master/APP%E6%8A%93%E5%8C%85/%E9%93%BE%E5%AE%B6 "链家")  | 通过输入城市名获取链家app上相应的住房地址、价格等信息 | pymysql、requests... |
| [CPA之家](https://github.com/jll01/Spiders/tree/master/CPA%E4%B9%8B%E5%AE%B6 "CPA之家")  | 获取cpa之家数据 | pymysql、requests... |
| [IP代理](https://github.com/jll01/Spiders/tree/master/IP%E6%B1%A0%E5%92%8CCookie%E6%B1%A0 "IP代理")  | ip代理池 | requests、re... |
| [ITCast老师](https://github.com/jll01/Spiders/tree/master/ITCast%E8%80%81%E5%B8%88 "ITCast老师")  | ITCast老师信息获取 | scrapy.Spider... |
| [Mikan动漫](https://github.com/jll01/Spiders/tree/master/Mikan "Mikan动漫")  | Mikan首页动漫信息获取(同步、分布式) | redis、requests、lxml、scrapy_redis分布式... |
| [QQ音乐评论](https://github.com/jll01/Spiders/tree/master/QQ%E9%9F%B3%E4%B9%90%E8%AF%84%E8%AE%BA "QQ音乐评论")  | celery爬虫 | pymongo、pymysql、requests、celery... |
| [TIOBE](https://github.com/jll01/Spiders/tree/master/TIOBE "TIOBE")  | 获取TIOBE网站上关于编程语言的排行，并绘制图形 | requests、re、pandas、plotly... |
| [下厨房菜谱](https://github.com/jll01/Spiders/tree/master/%E4%B8%8B%E5%8E%A8%E6%88%BF%E8%8F%9C%E8%B0%B1 "下厨房菜谱")  | 通过输入要搜索的菜谱名获取对应的菜谱 | requests、lxml... |
| [东方财富股票](https://github.com/jll01/Spiders/tree/master/%E4%B8%9C%E6%96%B9%E8%B4%A2%E5%AF%8C%E8%82%A1%E7%A5%A8 "东方财富股票")  | 获取股票的详细信息 | pymysql、requests、re、redis... |
| [东莞阳光问政平台](https://github.com/jll01/Spiders/tree/master/%E4%B8%9C%E8%8E%9E%E9%98%B3%E5%85%89%E9%97%AE%E6%94%BF%E5%B9%B3%E5%8F%B0 "东莞阳光问政平台")  | 获取东莞阳光问政平台问题与解决等信息 | CrawlSpider、pymysql... |
| [中国知网](https://github.com/jll01/Spiders/tree/master/%E4%B8%AD%E5%9B%BD%E7%9F%A5%E7%BD%91 "中国知网")  | 中国知网输入关键词后搜索文章,获取文章信息 | pymysql、requests、lxml... |
| [哔哩哔哩](https://github.com/jll01/Spiders/tree/master/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9 "哔哩哔哩")  | 哔哩哔哩弹幕、用户信息、评论、制作词云、搜索下载up主视频 | threading、pymysql、requests、matplotlib、numpy、PIL、queue... |
| [天气](https://github.com/jll01/Spiders/tree/master/%E5%A4%A9%E6%B0%94 "天气")  | 获取历年天气信息数据并简单的绘图 | pymysql、requests、re、threading、pandas... |
| [天眼查](https://github.com/jll01/Spiders/tree/master/%E5%A4%A9%E7%9C%BC%E6%9F%A5 "天眼查")  | 通过天眼查获取要查询的城市或者行业里面公司的信息 | requests、lxml... |
| [奇书网](https://github.com/jll01/Spiders/tree/master/%E5%A5%87%E4%B9%A6%E7%BD%91 "奇书网")  | 获取奇书网小说信息 | pymysql、requests、lxml、threading、re、gevent、pymongo、celery、redis... |
| [好奇心日报](https://github.com/jll01/Spiders/tree/master/%E5%A5%BD%E5%A5%87%E5%BF%83%E6%97%A5%E6%8A%A5 "好奇心日报")  | 获取好奇心日报所有文章信息并保存到数据库 | pymysql、requests、lxml、queue、threading、concurrent.futures... |
| [好知课程](https://github.com/jll01/Spiders/tree/master/%E5%A5%BD%E7%9F%A5%E8%AF%BE%E7%A8%8B "好知课程")  | 获取好知课程中课程和老师的信息 | scrapy的Spider类和CrawlSpider类... |
| [妹子图](https://github.com/jll01/Spiders/tree/master/%E5%A6%B9%E5%AD%90%E5%9B%BE "妹子图")  | 妹子图爬虫下载 | requests、lxml、threading... |
| [彼岸壁纸](https://github.com/jll01/Spiders/tree/master/%E5%BD%BC%E5%B2%B8%E5%A3%81%E7%BA%B8 "彼岸壁纸")  | 壁纸下载 | requests、re、scrapy的Spider类... |
| [微信公众号](https://github.com/jll01/Spiders/tree/master/%E5%BE%AE%E4%BF%A1%E5%85%AC%E4%BC%97%E5%8F%B7 "狗微信公众号")  | 通过搜狗微信公众号接口获取公众号信息和公众号文章 | requests、lxml、re... |
| [我爱读电子书](https://github.com/jll01/Spiders/tree/master/%E6%88%91%E7%88%B1%E8%AF%BB%E7%94%B5%E5%AD%90%E4%B9%A6 "我爱读电子书")  | 获取我爱读电子书网站所有的电子书信息 | scrapy的crawlspider类和Spider类、pymysql... |
| [携程](https://github.com/jll01/Spiders/tree/master/%E6%90%BA%E7%A8%8B "携程")  | 输入城市名称在携程中获取酒店信息 | pymysql、requests、re... |
| [新浪财经](https://github.com/jll01/Spiders/tree/master/%E6%96%B0%E6%B5%AA%E8%B4%A2%E7%BB%8F "新浪财经")  | 通过pandas获取网页中的表格数据 | pandas... |
| [无损音乐交流网站](https://github.com/jll01/Spiders/tree/master/%E6%97%A0%E6%8D%9F%E9%9F%B3%E4%B9%90%E4%BA%A4%E6%B5%81%E7%BD%91%E7%AB%99 "无损音乐交流网站")  | 获取音乐信息和下载链接和歌手的信息 | pymysql、CrawlSpider... |
| [有缘网](https://github.com/jll01/Spiders/tree/master/%E6%9C%89%E7%BC%98%E7%BD%91 "有缘网")  | 有缘网全国女性用户信息爬虫 | CrawlSpider类... |
| [牛人吐槽](https://github.com/jll01/Spiders/tree/master/%E7%89%9B%E4%BA%BA%E5%90%90%E6%A7%BD "牛人吐槽")  | 获取牛人吐槽信息并保存 | requests、re、lxml... |
| [猫眼电影](https://github.com/jll01/Spiders/tree/master/%E7%8C%AB%E7%9C%BC%E7%94%B5%E5%BD%B1 "猫眼电影")  | 猫眼电影信息、票房、评论 | pymysql、requests、re、threading、lxml... |
| [知乎](https://github.com/jll01/Spiders/tree/master/%E7%9F%A5%E4%B9%8E "知乎")  | 知乎首页爬虫 | selenium、pymysql、requests... |
| [笔趣阁](https://github.com/jll01/Spiders/tree/master/%E7%AC%94%E8%B6%A3%E9%98%81 "笔趣阁")  | 通过搜索小说名，选择要下载的小说到本地 | requests、lxml... |
| [精品图片](https://github.com/jll01/Spiders/tree/master/%E7%B2%BE%E5%93%81%E5%9B%BE%E7%89%87 "精品图片")  | 下载图片 | asyncio、aiohttp、re、lxml... |
| [纵横中文网](https://github.com/jll01/Spiders/tree/master/%E7%BA%B5%E6%A8%AA%E4%B8%AD%E6%96%87%E7%BD%91 "纵横中文网")  | 小说信息获取并下载 | Spider类、CrawlSpider类、asyncio、multiprocessing、<br>gevent、threading、selenium、celery... |
| [美拍](https://github.com/jll01/Spiders/tree/master/%E7%BE%8E%E6%8B%8D "美拍")  | 美拍视频下载 | pymysql、requests、queue、threading... |
| [虚拟手机号](https://github.com/jll01/Spiders/tree/master/%E8%99%9A%E6%8B%9F%E6%89%8B%E6%9C%BA%E5%8F%B7 "虚拟手机号")  | 获取虚拟手机号收到的短信 | pymysql、requests、re、Spider类... |
| [表情包](https://github.com/jll01/Spiders/tree/master/%E8%A1%A8%E6%83%85%E5%8C%85 "表情包")  | 表情包下载 | asyncio、aiohttp、re、lxml... |
| [豆瓣](https://github.com/jll01/Spiders/tree/master/%E8%B1%86%E7%93%A3 "豆瓣")  | 获取豆瓣网站中的电影和读书内容 | pymysql、requests、re、concurrent.futures、redis、Spider类、lxml... |
| [验证码](https://github.com/jll01/Spiders/tree/master/%E9%AA%8C%E8%AF%81%E7%A0%81 "验证码")  | 破解滑动验证码 | selenium、requests... |
| [京东商品信息](https://github.com/jll01/Spiders/tree/master/%E7%94%B5%E5%95%86%E5%B9%B3%E5%8F%B0/jingdong "京东商品信息")  | 京东商品信息 | scrapy.Spider、requests、re、pymysql... |
| [京东评论](https://github.com/jll01/Spiders/tree/master/%E7%94%B5%E5%95%86%E5%B9%B3%E5%8F%B0/jingdong_requests "京东评论")  | 京东评论和商品信息 | pymysql、requests、re、lxml、threading... |
| [淘宝](https://github.com/jll01/Spiders/tree/master/%E7%94%B5%E5%95%86%E5%B9%B3%E5%8F%B0/taobao "淘宝")  | 淘宝商品爬虫, selenium破解滑块验证 | selenium、pymysql、requests、re、lxml... |
| [天猫](https://github.com/jll01/Spiders/tree/master/%E7%94%B5%E5%95%86%E5%B9%B3%E5%8F%B0/tianmao "天猫")  | 天猫商品信息爬虫 | lxml、requests、re... |
| [唯品会](https://github.com/jll01/Spiders/tree/master/%E7%94%B5%E5%95%86%E5%B9%B3%E5%8F%B0/weipinhui "唯品会")  | 输入城市名称在携程中获取酒店信息 | pymysql、requests、re、threading... |
| [模拟登录](https://github.com/jll01/Spiders/tree/master/%E6%A8%A1%E6%8B%9F%E7%99%BB%E9%99%86 "模拟登录")  | 模拟登录(微信、微博、拉勾网、BOSS直聘、Github等) | selenium、bs4、requests、re、lxml、PIL... |
| [网易云音乐](https://github.com/jll01/Spiders/tree/master/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90 "网易云音乐")  | 网易云音乐歌曲下载 | requests、bs4、re、string、Crypto.Cipher... |
| [IT桔子网](https://github.com/jll01/Spiders/tree/master/IT%E6%A1%94%E5%AD%90%E7%BD%91 "IT桔子网")  | IT桔子网模拟登陆、获取事件库数据 | requests、json... |
