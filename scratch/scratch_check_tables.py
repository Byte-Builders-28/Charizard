import urllib.request
import json

test_ids = ["PSI-25", "PSI-26", "PSI-68", "PSI-100", "PSI-101", "PSI-102", "PSI-159", "PSI-10", "PSI-20"]
for pid in test_ids:
    url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{pid}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as res:
            d = json.loads(res.read().decode('utf-8'))
            tables = d.get('experimentalTable', []) + d.get('modelingTable', [])
            print(f"{pid} ({d.get('investigationAcronym')}): {len(tables)} tables")
            for t in tables:
                print(f"   -> {t.get('file_name')} ({t.get('file_size')} bytes)")
    except Exception as e:
        print(f"{pid} error: {e}")
