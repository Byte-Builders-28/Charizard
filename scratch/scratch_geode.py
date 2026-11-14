import urllib.request
import json

urls_to_test = [
    "https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-69",
    "https://psi.nasa.gov/geode-py/ws/repo/studies/PSI-69",
    "https://psi.nasa.gov/geode-py/ws/repo/investigation/PSI-69",
    "https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-60",
    "https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-98",
    "https://psi.nasa.gov/geode-py/ws/search?q=&data_source=psi&data_type=investigation",
    "https://psi.nasa.gov/geode-py/ws/repo/search?q=&data_source=psi&data_type=investigation"
]

for url in urls_to_test:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            content = res.read().decode('utf-8')
            print(f"SUCCESS {url} -> Status {res.status}, Len {len(content)}")
            try:
                data = json.loads(content)
                print("   Keys:", list(data.keys()) if isinstance(data, dict) else len(data))
                if isinstance(data, dict):
                    for k in ['title', 'investigationTitle', 'name', 'investigation_title', 'id', 'doi']:
                        if k in data:
                            print(f"   {k}: {data[k]}")
            except:
                print("   Not JSON:", content[:150])
    except Exception as e:
        print(f"FAIL {url} -> {e}")
