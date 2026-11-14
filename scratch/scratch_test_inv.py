import urllib.request

for pid in ["PSI-69", "PSI-60", "PSI-138", "PSI-98", "PSI-25"]:
    url = f"https://psi.nasa.gov/physci/repo/data/investigations/{pid}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            content = res.read().decode('utf-8')
            print(pid, "status:", res.status, "len:", len(content))
    except Exception as e:
        print(pid, "error:", e)
