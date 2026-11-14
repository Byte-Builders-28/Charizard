import urllib.request
import json
import sys

test_ids = ["PSI-25", "PSI-68", "PSI-159", "PSI-102", "PSI-20"]
for pid in test_ids:
    url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{pid}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as res:
            d = json.loads(res.read().decode('utf-8'))
            tables = d.get('experimentalTable', []) + d.get('modelingTable', [])
            print(f"{pid} ({d.get('investigationAcronym')}): {len(tables)} tables", flush=True)
            for t in tables:
                print(f"   -> {t.get('file_name')} ({t.get('file_size')} bytes)", flush=True)
    except Exception as e:
        print(f"{pid} error: {e}", flush=True)
