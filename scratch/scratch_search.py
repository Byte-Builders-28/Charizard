import urllib.request
import json
import re

url = 'https://psi.nasa.gov/physci/repo/search?q=&data_source=psi&data_type=investigation'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as res:
        content = res.read().decode('utf-8')
        print("Status:", res.status)
        print("Content-Type:", res.headers.get('content-type'))
        print("Length:", len(content))
        print("First 1000 chars:\n", content[:1000])
except Exception as e:
    print("Error:", e)
