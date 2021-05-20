"""
针对 requests 中使用代理 verify=False 对一些域名访问失败，报ssl错误
"""

"""
先卸载重装requests或更新requests版本看能不能解决，不能解决使用下面方法
"""

"""
第一种 requests 请求
"""
import ssl
import requests

from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager, ProxyManager


urllib3.disable_warnings()


# 代理ip
ip_port = ''


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = ProxyManager(
            f'http://{ip_port}',
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1
        )

headers = {
    'User-Agent': UserAgent(verify_ssl=False).random,
}
s = requests.session()
url = ''
s.mount('https://', MyAdapter())
r = s.get(url1,verify = False, headers=headers)
print(r.status_code)


"""
第二种 utllib3
"""
import urllib3
import ssl


# 代理ip
ip_port =  ''

ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')

http = urllib3.ProxyManager(
    f'http://{ip_port}',
    ssl_version=ssl.PROTOCOL_TLSv1,
    ssl_context=ctx,
)
url = ''
r = http.request("GET", url, preload_content=False)
print(r.status)
