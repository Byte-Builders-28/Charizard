How to Run
S3 Inventory Scan:
bash
python src/ingest/s3_inventory.py --max-keys 100
Fetch Combustion Telemetry & Generate Summary Report:
bash
python fetch_combustion_data.py
Execute Provenance Raw Ingestion Pipeline:
bash
python src/ingest/ingest_psi.py