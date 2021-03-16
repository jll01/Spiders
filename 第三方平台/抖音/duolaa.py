import requests

from fake_useragent import UserAgent


class DuoLaA(object):
    def __init__(self, keyword):
        """
        哆啦A数据分析平台
        @param keyword: 搜索的关键词
        """
        self.session = requests.Session()
        self.search_url = 'http://duolalive.com/api/uid_sou.php'
        self.detail_url = 'http://duolalive.com/api/uid_details/aweme_analysis.php?id={}&time=0&type=aweme_analysis'
        self.keyword = keyword

    def get_uid(self):
        """
        获取对应的唯一uid
        @return:
        """
        uid, nick_name = '', ''
        headers = {
            'Host': 'duolalive.com',
            'Origin': 'http://duolalive.com',
            'Referer': 'http://duolalive.com/forindex.php',
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        data = {
            'tab_type': '1',
            'value': self.keyword,
            'sou': '',
        }
        try:
            response = self.session.post(self.search_url, headers=headers, data=data, timeout=10).json()
            uid = response.get('list')[0].get('user_id', '')
            nick_name = response.get('list')[0].get('user_name')
        except:
            pass

        return uid, nick_name

    def get_detail(self, uid):
        """
        获取详细的数据
        @param uid: 唯一标识
        @return:
        """
        url = '''http://duolalive.com/api/uid_details/aweme_analysis.php?id={}&time=0&type=aweme_analysis'''
        headers_detail = {
            'Host': 'duolalive.com',
            'Referer': 'http://duolalive.com/forindex.php',
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        item = {
            'fans_num': 0,
            'like_count': 0,
            'video_count': 0
        }
        try:
            response_detail = self.session.get(url.format(uid), headers=headers_detail, timeout=10).json()
            item['fans_num'] = self.str2int(response_detail.get('aweme_data').get('user_fensi_arr').get('user_fensi', '0'))
            item['like_count'] = self.str2int(response_detail.get('aweme_data').get('aweme_digg_count_arr').get('aweme_digg_count', '0'))
            item['video_count'] = self.str2int(response_detail.get('aweme_data').get('aweme_count_arr').get('aweme_count', '0'))
        except:
            pass

        return item

    @staticmethod
    def str2int(in_str):
        try:
            if '万' in in_str:
                return int(eval(in_str.replace(',', '').split('万')[0]) * 10000)
            else:
                return int(eval(in_str))
        except:
            return in_str

    def main(self):
        uid, nick_name = self.get_uid()
        if uid:
            result = self.get_detail(uid)
            result.update({
                'uid': uid,
                'nick_name': nick_name,
            })
            print(result)


if __name__ == '__main__':
    DuoLaA('***').main()
