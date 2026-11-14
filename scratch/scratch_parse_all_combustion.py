import urllib.request
import json

url = "https://psi.nasa.gov/geode-py/ws/repo/search?q=&size=200&data_source=psi&data_type=investigation"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    d = json.loads(res.read().decode('utf-8'))

hits = d['hits']['hits']
print(f"Total hits: {len(hits)}")

all_combustion = []
for h in hits:
    src = h.get('_source', {})
    ra = src.get('Research Area', '')
    sub_ra = src.get('SubResearch Area', '')
    acc = src.get('Accession', '')
    title = src.get('Title', '')
    acronym = src.get('Acronym', '')
    ptype = src.get('Project Type', '')
    
    is_comb = (
        'Combustion' in str(ra) or 
        'Fire' in str(sub_ra) or 
        'Combustion' in str(sub_ra) or
        any(k in title.upper() for k in ['FLEX', 'SAFFIRE', 'ACME', 'BASS', 'SOFIE', 'SPICE', 'SAME', 'FLAME', 'FIRE', 'DROPLET']) or
        any(k in acronym.upper() for k in ['FLEX', 'SAFFIRE', 'ACME', 'BASS', 'SOFIE', 'SPICE', 'SAME'])
    )
    if is_comb:
        all_combustion.append({
            'Accession': acc,
            'Acronym': acronym,
            'Title': title,
            'Research Area': ra,
            'SubResearch Area': sub_ra,
            'Project Type': ptype,
            'Flight Platform': src.get('Flight Platform', '')
        })

print(f"\nFound {len(all_combustion)} combustion / fire-safety investigations:")
for c in sorted(all_combustion, key=lambda x: int(x['Accession'].replace('PSI-', '')) if x['Accession'].startswith('PSI-') else 999):
    print(f"  {c['Accession']}: [{c['Acronym']}] {c['Title']} | Area: {c['Research Area']} / {c['SubResearch Area']}")
