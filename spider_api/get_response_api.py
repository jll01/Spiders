import requests
import hashlib
import json
import datetime
import socket

now = datetime.datetime.today()
data = {
    "token": hashlib.md5(f'spider_{now.year}-{now.month}-{now.day}'.encode('utf-8')).hexdigest(),
    "index_url": "http://www.jd.com/",
}
host = socket.gethostbyname(socket.gethostname())
url = f'http://{host}:8000/api_get_icp_nation'

res = requests.post(url, data=json.dumps(data))

print(res.text)
