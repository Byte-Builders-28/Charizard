import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    content = res.read().decode('utf-8')

idx = content.find("getDataURL")
while idx != -1:
    print("--- getDataURL ---")
    print(content[idx-100:idx+300])
    idx = content.find("getDataURL", idx + 10)
