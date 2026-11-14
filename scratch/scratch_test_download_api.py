import urllib.request
import urllib.parse
import json

base = "https://psi.nasa.gov/geode-py/ws/studies/PSI-69/download"
params = {
    "file": "PSI-69_Experimental table_FLEX.csv",
    "version": "1",
    "redirect": "false"
}
url = base + "?" + urllib.parse.urlencode(params)
print("Testing URL (redirect=false):", url)

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as res:
        print("Status:", res.status)
        content = res.read().decode('utf-8')
        print("Response (len", len(content), "):", content[:300])
except Exception as e:
    print("Error:", e)

# Test with redirect=true
params["redirect"] = "true"
url_redir = base + "?" + urllib.parse.urlencode(params)
print("\nTesting URL (redirect=true):", url_redir)
req = urllib.request.Request(url_redir, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as res:
        print("Status:", res.status)
        print("Final URL:", res.geturl())
        content = res.read(500)
        print("Content sample:\n", content[:200].decode('utf-8', errors='ignore'))
except Exception as e:
    print("Error:", e)
