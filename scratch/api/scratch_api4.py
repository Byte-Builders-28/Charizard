import urllib.request
import re

url = 'https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    content = res.read().decode('utf-8')

# Search for strings containing 'combustion' or 'Combustion'
matches = set(re.findall(r'["\']([^"\']*[Cc]ombustion[^"\']*)["\']', content))
print("Combustion matches:", matches)

# Search for json files or endpoints loaded
json_files = set(re.findall(r'["\']([^"\']+\.json[^"\']*)["\']', content))
print("JSON files:", json_files)
