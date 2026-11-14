import urllib.request
import urllib.parse
import boto3
from botocore import UNSIGNED
from botocore.config import Config

# Test S3 bucket with prefix psi-data/
s3 = boto3.client('s3', region_name='us-west-2', config=Config(signature_version=UNSIGNED))
try:
    res = s3.list_objects_v2(Bucket='nasa-psi', Prefix='psi-data/', MaxKeys=5)
    print("S3 Prefix psi-data/ count:", len(res.get('Contents', [])))
    for obj in res.get('Contents', []):
        print("  Key:", obj['Key'])
except Exception as e:
    print("S3 error:", e)

# Test psi.nasa.gov datamanager endpoint
rel_path = "/datamanager/file/Home/psi-data/PSI-69/Experimental table/PSI-69_Experimental table_FLEX.csv"
url = "https://psi.nasa.gov" + urllib.parse.quote(rel_path)
print("Testing URL:", url)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read()
        print("HTTP Status:", resp.status)
        print("Downloaded bytes:", len(content))
        print("First 200 chars:\n", content[:200].decode('utf-8', errors='ignore'))
except Exception as e:
    print("HTTP error:", e)
