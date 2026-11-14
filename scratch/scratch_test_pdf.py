import boto3
from botocore import UNSIGNED
from botocore.config import Config
import pypdf
import hashlib
import os

s3 = boto3.client('s3', region_name='us-west-2', config=Config(signature_version=UNSIGNED))
dest = "data/raw/PK4/PK4_Campaign01_Report_final.pdf"
os.makedirs("data/raw/PK4", exist_ok=True)
s3.download_file('nasa-psi', 'pk4/To_NASA_team/Campaign_Reports/PK4_Campaign01_Report_final.pdf', dest)
print("Downloaded bytes:", os.path.getsize(dest))

# Test text extraction with page numbers
reader = pypdf.PdfReader(dest)
print("Pages:", len(reader.pages))
txt_path = "data/raw/PK4/PK4_Campaign01_Report_final.txt"
with open(txt_path, "w", encoding="utf-8") as f:
    for idx, page in enumerate(reader.pages, start=1):
        f.write(f"--- Page {idx} ---\n{page.extract_text()}\n\n")

print("Wrote text to:", txt_path)
print("First 200 chars:\n", open(txt_path, "r", encoding="utf-8").read()[:200])
