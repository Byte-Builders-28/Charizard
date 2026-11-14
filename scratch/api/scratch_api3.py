import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    content = res.read().decode('utf-8')

# Search for HttpClient methods like .get(
gets = re.findall(r'\.get\(([^)]+)\)', content)
for g in gets[:20]:
    print("GET:", g)
