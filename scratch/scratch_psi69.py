import urllib.request
import json

url = "https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-69"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as res:
    data = json.loads(res.read().decode('utf-8'))

print("Accession:", data.get('accession'))
print("Title:", data.get('title'))
print("Acronym:", data.get('investigationAcronym'))
print("Research Area:", data.get('researchArea'))
print("Sub Research Area:", data.get('subResearchArea'))
print("DOI:", data.get('doi'))
print("Source Link:", data.get('sourceLink'))
print("Experimental Tables:", data.get('experimentalTable'))
print("Experiments count:", len(data.get('experiments', [])))
if data.get('experiments'):
    print("Sample Experiment keys:", list(data['experiments'][0].keys()))
    print("Sample Experiment:", json.dumps(data['experiments'][0], indent=2)[:500])

print("Assays count:", len(data.get('assays', [])))
if data.get('assays'):
    print("Sample Assay:", json.dumps(data['assays'][0], indent=2)[:500])
