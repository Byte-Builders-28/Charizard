import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    content = res.read().decode('utf-8')

# Search for patterns where requests are made
matches = set(re.findall(r'(\/[a-zA-Z0-9_\-\/]*investigation[a-zA-Z0-9_\-\/]*)', content))
print("Investigation paths:", matches)

matches_s3 = set(re.findall(r'(https?:\/\/[a-zA-Z0-9\.\-\/]*s3[a-zA-Z0-9\.\-\/]*)', content))
print("S3 urls:", matches_s3)

matches_http = set(re.findall(r'["\'](https?:\/\/[^"\']+)["\']', content))
for h in sorted(matches_http):
    if 'nasa.gov' in h:
        print("NASA URL:", h)
