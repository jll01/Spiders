# 平常练习的一些爬虫

|     网站/手机软件     |          爬虫          |     工具/库     |
| :-------------: | :-----------------------: | :--------------: |
| [3D福利彩票](./3D福利彩票 "3D福利彩票")  | 获取3D福利彩票历年数据并简单的绘图 | threading、pymysql、re... |
| [小红书](./APP抓包/小红书 "小红书")  | 下载小红书视频并保存视频相关的数据 | threading、pymysql、queue、requests、Fiddler... |
| [快手](./APP抓包/快手 "快手")  | 下载快手短视频并保存视频相关的数据 | threading、requests、Fiddler... |
| [抖音](./APP抓包/抖音 "抖音")  | 通过app/分享url下载抖音短视频并保存视频相关的数据 | threading、pymysql、requests、Fiddler、夜神模拟器... |
| [斗鱼](./APP抓包/斗鱼 "斗鱼")  | 通过api获取斗鱼app主播房间号、时间等数据 | pymysql... |
| [百思不得其姐](./APP抓包/百思不得其姐 "百思不得其姐")  | 获取分享数、点赞数等| requests... |
| [美团](./APP抓包/美团 "美团")  | 先要获取到城市的ID, 根据输入的城市查询到ID后提取每个城市中餐厅的名称、地址等信息 | pymysql、requests... |
| [链家](./APP抓包/链家 "链家")  | 通过输入城市名获取链家app上相应的住房地址、价格等信息 | pymysql、requests... |
| [CPA之家](./CPA之家 "CPA之家")  | 获取cpa之家数据 | pymysql、requests... |
| [IP代理](./IP池和Cookie池 "IP代理")  | ip代理池 | requests、re... |
| [ITCast老师](./ITCast老师 "ITCast老师")  | ITCast老师信息获取 | scrapy.Spider... |
| [Mikan动漫](./Mikan "Mikan动漫")  | Mikan首页动漫信息获取(同步、分布式) | redis、requests、lxml、scrapy_redis分布式... |
| [QQ音乐评论](./QQ音乐评论 "QQ音乐评论")  | celery爬虫 | pymongo、pymysql、requests、celery... |
| [TIOBE](./TIOBE "TIOBE")  | 获取TIOBE网站上关于编程语言的排行，并绘制图形 | requests、re、pandas、plotly... |
| [下厨房菜谱](./下厨房菜谱 "下厨房菜谱")  | 通过输入要搜索的菜谱名获取对应的菜谱 | requests、lxml... |
| [东方财富股票](./东方财富股票 "东方财富股票")  | 获取股票的详细信息 | pymysql、requests、re、redis... |
| [东莞阳光问政平台](./东莞阳光问政平台 "东莞阳光问政平台")  | 获取东莞阳光问政平台问题与解决等信息 | CrawlSpider、pymysql... |
| [中国知网](./中国知网 "中国知网")  | 中国知网输入关键词后搜索文章,获取文章信息 | pymysql、requests、lxml... |
| [哔哩哔哩](./哔哩哔哩 "哔哩哔哩")  | 哔哩哔哩弹幕、用户信息、评论、制作词云、搜索下载up主视频 | threading、pymysql、requests、matplotlib、numpy、PIL、queue... |
| [天气](./天气 "天气")  | 获取历年天气信息数据并简单的绘图 | pymysql、requests、re、threading、pandas... |
| [天眼查](./天眼查 "天眼查")  | 通过天眼查获取要查询的城市或者行业里面公司的信息 | requests、lxml... |
| [奇书网](./奇书网 "奇书网")  | 获取奇书网小说信息 | pymysql、requests、lxml、threading、re、gevent、pymongo、celery、redis... |
| [好奇心日报](./好奇心日报 "好奇心日报")  | 获取好奇心日报所有文章信息并保存到数据库 | pymysql、requests、lxml、queue、threading、concurrent.futures... |
| [好知课程](./好知课程 "好知课程")  | 获取好知课程中课程和老师的信息 | scrapy的Spider类和CrawlSpider类... |
| [妹子图](./妹子图 "妹子图")  | 妹子图爬虫下载 | requests、lxml、threading... |
| [彼岸壁纸](./彼岸壁纸 "彼岸壁纸")  | 壁纸下载 | requests、re、scrapy的Spider类... |
| [微信公众号](./微信公众号 "微信公众号")  | 通过搜狗微信公众号接口获取公众号信息和公众号文章 | requests、lxml、re... |
| [我爱读电子书](./我爱读电子书 "我爱读电子书")  | 获取我爱读电子书网站所有的电子书信息 | scrapy的crawlspider类和Spider类、pymysql... |
| [携程](./携程 "携程")  | 输入城市名称在携程中获取酒店信息 | pymysql、requests、re... |
| [新浪财经](./新浪财经 "新浪财经")  | 通过pandas获取网页中的表格数据 | pandas... |
| [无损音乐交流网站](./无损音乐交流网站 "无损音乐交流网站")  | 获取音乐信息和下载链接和歌手的信息 | pymysql、CrawlSpider... |
| [有缘网](./有缘网 "有缘网")  | 有缘网全国女性用户信息爬虫 | CrawlSpider类... |
| [牛人吐槽](./牛人吐槽 "牛人吐槽")  | 获取牛人吐槽信息并保存 | requests、re、lxml... |
| [猫眼电影](./猫眼电影 "猫眼电影")  | 猫眼电影信息、票房、评论 | pymysql、requests、re、threading、lxml... |
| [知乎](./知乎 "知乎")  | 知乎首页爬虫 | selenium、pymysql、requests... |
| [笔趣阁](./笔趣阁 "笔趣阁")  | 通过搜索小说名，选择要下载的小说到本地 | requests、lxml... |
| [精品图片](./精品图片 "精品图片")  | 下载图片 | asyncio、aiohttp、re、lxml... |
| [纵横中文网](./纵横中文网 "纵横中文网")  | 小说信息获取并下载 | Spider类、CrawlSpider类、asyncio、multiprocessing、<br>gevent、threading、selenium、celery... |
| [美拍](./美拍 "美拍")  | 美拍视频下载 | pymysql、requests、queue、threading... |
| [虚拟手机号](./虚拟手机号 "虚拟手机号")  | 获取虚拟手机号收到的短信 | pymysql、requests、re、Spider类... |
| [表情包](./表情包 "表情包")  | 表情包下载 | asyncio、aiohttp、re、lxml... |
| [豆瓣](./豆瓣 "豆瓣")  | 获取豆瓣网站中的电影和读书内容 | pymysql、requests、re、concurrent.futures、redis、Spider类、lxml... |
| [验证码](./验证码 "验证码")  | 破解滑动验证码 | selenium、requests... |
| [京东商品信息](./电商平台/jingdong "京东商品信息")  | 京东商品信息 | scrapy.Spider、requests、re、pymysql... |
| [京东评论](./电商平台/jingdong_requests "京东评论")  | 京东评论和商品信息 | pymysql、requests、re、lxml、threading... |
| [淘宝](./电商平台/taobao "淘宝")  | 淘宝商品爬虫, selenium破解滑块验证 | selenium、pymysql、requests、re、lxml... |
| [天猫](./电商平台/tianmao "天猫")  | 天猫商品信息爬虫 | lxml、requests、re... |
| [唯品会](./电商平台/weipinhui "唯品会")  | 输入城市名称在携程中获取酒店信息 | pymysql、requests、re、threading... |
| [模拟登录](./模拟登陆 "模拟登录")  | 模拟登录(微信、微博、拉勾网、BOSS直聘、Github等) | selenium、bs4、requests、re、lxml、PIL... |
| [网易云音乐](./网易云音乐 "网易云音乐")  | 网易云音乐歌曲下载 | requests、bs4、re、string、Crypto.Cipher... |
| [IT桔子网](./IT桔子网 "IT桔子网")  | IT桔子网模拟登陆、获取事件库数据 | requests、json... |
| [云听斗罗大陆音频下载](./云听斗罗大陆音频下载 "云听斗罗大陆音频下")  | 云听斗罗大陆音频下载 | requests、concurrent.futures、re... |
| [笑话网](./模板 "笑话网爬虫")  | 不同方法对笑话网进行爬虫 | requests、concurrent.futures、celery、gevent、multiprocessing、urllib3... |
| [腾讯视频弹幕](./腾讯视频弹幕 "斗罗大陆弹幕")  | 斗罗大陆弹幕 | requests、pymysql、re... |
| [ICP域名信息备案管理系统](./ICP域名信息备案管理系统幕 "ICP域名信息备案管理系统")  | 获取域名ICP(js) | requests、opencv... |
| [OCR](./OCR "百度飞桨")  | 百度飞桨 | paddleocr... |
| [Selenium反爬虫](./Selenium反爬虫 "Selenium反爬虫")  | 防止识别Selenium和极验滑动验证码 | requests、selenium、numpy... |
| [Selenium获取response_headers](./Selenium获取response_headers "Selenium获取response_headers")  | Selenium获取response headers | selenium... |
| [spider_api](./spider_api "spider_api")  | Flask,域名ICP | flask、requests、socket... |
| [各个应用市场app下载](./各个应用市场app下载 "各个应用市场app下载")  | 各个应用市场app下载 | requests、re、lxml... |
| [小鹅通视频下载](./小鹅通视频下载 "小鹅通视频下载")  | 输入视频url下载 | requests、getopt... |
| [文件目录结构](./文件目录结构 "文件目录结构")  | 文件目录结构 | typing、re... |
| [第三方平台](./第三方平台 "第三方平台")  | 第三方平台获取抖音、公众号等 | requests、hashlib... |
