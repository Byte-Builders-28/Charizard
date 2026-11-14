import urllib.request
import json

url = "https://psi.nasa.gov/geode-py/ws/repo/search?q=&data_source=psi&data_type=investigation"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=15) as res:
    data = json.loads(res.read().decode('utf-8'))

hits = data.get('hits', {}).get('hits', [])
print(f"Total hits returned: {len(hits)}")

combustion_invs = []
for h in hits:
    source = h.get('_source', {})
    ra = source.get('researchArea', '')
    sub_ra = source.get('subResearchArea', '')
    title = source.get('title', '')
    acronym = source.get('investigationAcronym', '')
    acc = source.get('accession', '')
    doi = source.get('doi', '')
    if 'Combustion' in str(ra) or 'Fire' in str(sub_ra) or any(k in title.upper() for k in ['FLEX', 'SAFFIRE', 'ACME', 'BASS', 'SOFIE', 'SPICE', 'SAME']):
        combustion_invs.append({
            'id': acc,
            'title': title,
            'acronym': acronym,
            'researchArea': ra,
            'subResearchArea': sub_ra,
            'doi': doi
        })

print(f"Total Combustion / Fire Safety investigations found: {len(combustion_invs)}")
for c in combustion_invs:
    print(f"[{c['id']}] {c['acronym']} - {c['title']} ({c['subResearchArea']}) DOI: {c['doi']}")
