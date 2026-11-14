import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    content = res.read().decode('utf-8')

with open("scratch_main.js", "w", encoding="utf-8") as f:
    f.write(content)

idx = content.find("studiesList")
while idx != -1:
    print("--- studiesList ---")
    print(content[max(0, idx-100):min(len(content), idx+200)])
    idx = content.find("studiesList", idx + 10)
