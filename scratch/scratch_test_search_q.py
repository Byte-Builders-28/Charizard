import urllib.request
import json

for q in ["q=Combustion", "q=FLEX", "q=Saffire", "q=BASS", "q=SPICE", "q=&size=500"]:
    url = f"https://psi.nasa.gov/geode-py/ws/repo/search?{q}&data_source=psi&data_type=investigation"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            d = json.loads(res.read().decode('utf-8'))
            total = d.get('hits', {}).get('total', {})
            hits = d.get('hits', {}).get('hits', [])
            print(f"Query {q}: total={total}, hits={len(hits)}")
            for h in hits[:3]:
                src = h.get('_source', {})
                print(f"   [{src.get('accession')}] {src.get('investigationAcronym')} - {src.get('title')}")
    except Exception as e:
        print(f"Query {q} error: {e}")
