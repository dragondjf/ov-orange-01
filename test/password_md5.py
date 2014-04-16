from Crypto.Hash import MD5
print(MD5.new(b'admin').hexdigest())

import requests

#setprotect
payload = {"did": 1, "pid":1, "enable":1}
response = requests.post('http://%s:%s/setprotect' % ("localhost", "8888"), params=payload, timeout=3)
print(response.text)