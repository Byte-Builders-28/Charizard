# 🔥 FlameScope — How to Run Guide

FlameScope is an open-science research workspace for NASA microgravity combustion science and spacecraft fire safety investigations.

---

## 1. Quick Start: Full Stack (Frontend + Backend)

### Terminal 1: Launch FastAPI Backend Server

```bash
# From repository root
python src/api/main.py
```
* Or via uvicorn directly:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
* **API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Terminal 2: Launch React + Tailwind + Plotly Frontend

```bash
cd app
npm run dev
```
* **Dashboard Web App:** [http://localhost:5173](http://localhost:5173)
* *Note:* The frontend has a built-in mock fallback, so it works seamlessly even if the backend is offline!

---

## 2. Running Data Pipelines

### Step 0: S3 Bucket Inventory Scan
Discovers public files in `s3://nasa-psi/` using anonymous, unsigned requests:
```bash
python src/ingest/s3_inventory.py --max-keys 100
```

### Step 1: Raw Data Ingestion with Provenance
Ingests raw PSI investigation metadata, flight reports, and PDF documents with SHA-256 manifests:
```bash
python src/ingest/ingest_psi.py
```

### Step 1 (Bonus): Combustion Telemetry Fetcher
Fetches tabular telemetry CSVs (< 25 MB) and builds `summary_report.md` & `summary_report.json`:
```bash
python fetch_combustion_data.py
```

### Step 2: Scientific LLM Extraction Pipeline
Extracts structured facts with exact citations & Pydantic validation:
```bash
# 1. Set your Gemini API key (free at aistudio.google.com/apikey)
$env:GEMINI_API_KEY = "your_api_key_here"

# 2. Run LLM extraction
python src/extract/extract_investigations.py

# Or test pipeline structure without API quota:
python src/extract/extract_investigations.py --dry-run
```

---

## 3. Frontend Pages Overview

| Page | Path | Key Capabilities |
|------|------|------------------|
| **Mission Control (Overview)** | `/` | Metric tiles, safety donut chart, research area breakdown, featured experiments |
| **Investigation Explorer** | `/explorer` | Live search, filter chips (safety category, fuel state, gravity, telemetry) |
| **Investigation Details** | `/investigation/:id` | 15 FieldValue cards with status badges (verified, extracted, inferred, unavailable), source quotes, telemetry table |
| **Comparative Analysis** | `/compare` | Side-by-side 2–3 investigation matrix, divergent parameter highlights, Plotly radar chart |
| **Scenario Analysis** | `/scenario` | Mission context scoring (ISS, Lunar Base, Mars Habitat, Rover) with transparent reason breakdown |
| **Scientific QA (Ask AI)** | `/ask` | Evidence-grounded conversational agent with exact investigation citations and starter prompts |
| **Research Gaps & Frontiers** | `/gaps` | Oxygen vs. Airflow scatter envelope, lunar/Mars partial-gravity gap alert, field coverage bars |
| **Data Export Gateway** | `/export` | Field selection, flat vs. nested JSON toggle, instant CSV / JSON downloads |
