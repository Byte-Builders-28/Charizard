import urllib.request
import re

req = urllib.request.Request('https://psi.nasa.gov/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    res = urllib.request.urlopen(req, timeout=10)
    html = res.read().decode('utf-8')
    links = set(re.findall(r'href=["\']([^"\']+)["\']', html))
    for l in sorted(links):
        if 'psi.nasa.gov' in l or l.startswith('/'):
            print(l)
except Exception as e:
    print('Error:', e)
