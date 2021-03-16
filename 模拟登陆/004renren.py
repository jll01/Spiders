import requests

sess = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
data = {
    "email":'****',
    "password":"****",
}

sess.post('http://www.renren.com/PLogin.do',headers=headers,data=data)

res = sess.get('http://www.renren.com/971271882/profile')
print(res.text)
with open('renren.html','w', encoding='utf-8') as f:
    f.write(res.text)
