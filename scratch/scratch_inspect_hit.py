import urllib.request
import json

url = "https://psi.nasa.gov/geode-py/ws/repo/search?q=&size=5&data_source=psi&data_type=investigation"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as res:
    d = json.loads(res.read().decode('utf-8'))
    hit = d['hits']['hits'][0]
    print("Hit keys:", list(hit.keys()))
    print("Hit content:\n", json.dumps(hit, indent=2))

