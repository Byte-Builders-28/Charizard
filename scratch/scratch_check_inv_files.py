import urllib.request
import json

targets = [
    "PSI-69", "PSI-68", "PSI-98", "PSI-99", "PSI-100", 
    "PSI-25", "PSI-26", "PSI-60", "PSI-107", "PSI-102", 
    "PSI-159", "PSI-10", "PSI-20", "PSI-21", "PSI-22", "PSI-23"
]

for pid in targets:
    url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{pid}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            title = data.get('title', '')
            acronym = data.get('investigationAcronym', '')
            doi = data.get('doi', '')
            exp_tables = data.get('experimentalTable', [])
            mod_tables = data.get('modelingTable', [])
            readmes = data.get('readme', [])
            images = data.get('images', [])
            assays = data.get('assays', [])
            
            print(f"\n==================== {pid}: [{acronym}] {title} ====================")
            print(f"DOI: {doi}")
            print(f"Experimental Tables ({len(exp_tables)}):")
            for t in exp_tables:
                print(f"  - {t.get('file_name')} ({t.get('file_size')} bytes, v{t.get('version')})")
            print(f"Modeling Tables ({len(mod_tables)}):")
            for t in mod_tables:
                print(f"  - {t.get('file_name')} ({t.get('file_size')} bytes)")
            print(f"Readme files ({len(readmes)}):")
            for r in readmes:
                print(f"  - {r.get('file_name')} ({r.get('file_size')} bytes)")
    except Exception as e:
        print(f"Error fetching {pid}: {e}")

