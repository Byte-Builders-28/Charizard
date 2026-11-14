import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as res:
        content = res.read().decode('utf-8')
        print("Length:", len(content))
        # Find urls or endpoints
        endpoints = set(re.findall(r'["\'](/physci/repo/api/[^"\']+|api/[^"\']+|/api/[^"\']+)["\']', content))
        print("Endpoints:", endpoints)
        # Find any other api endpoints
        all_apis = set(re.findall(r'https?://[a-zA-Z0-9.-]+/api/[a-zA-Z0-9/_.-]+', content))
        print("All APIs:", all_apis)
        # Find references to PSI-
        psi_refs = set(re.findall(r'PSI-\d+', content))
        print("PSI refs:", list(psi_refs)[:10])
except Exception as e:
    print("Error:", e)
