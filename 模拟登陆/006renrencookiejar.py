import urllib.request
import http.cookiejar
from urllib import parse

cookie = http.cookiejar.CookieJar()
cookie_handle = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(cookie_handle)
my_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 7.0; Win64; x64) '
    }
url = 'http://www.renren.com/PLogin.do'

data = {
    'email':'****',
    'password':'****',
}
data = parse.urlencode(data).encode('utf-8')
req = urllib.request.Request(url,headers=my_headers,data=data)
con = opener.open(req).read()
print(con.decode('utf-8'))
