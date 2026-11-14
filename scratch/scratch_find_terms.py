import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    content = res.read().decode('utf-8')

for term in ['experimentalTable', 'experimentalTables', 's3_path', 'remote_path', 'remote_url', 'downloadFile']:
    matches = [m.start() for m in re.finditer(re.escape(term), content)]
    print(f"Term '{term}': {len(matches)} occurrences")
    for idx in matches[:3]:
        print(f"  {content[max(0, idx-80):min(len(content), idx+120)]}")
