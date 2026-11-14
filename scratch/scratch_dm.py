import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    content = res.read().decode('utf-8')

matches = [m.start() for m in re.finditer(r'datamanager', content, re.IGNORECASE)]
print("Total occurrences of 'datamanager':", len(matches))
for idx in matches[:10]:
    start = max(0, idx - 100)
    end = min(len(content), idx + 200)
    print("--- SNIPPET ---")
    print(content[start:end])
