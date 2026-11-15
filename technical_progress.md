# 🔥 FlameScope — Technical Progress Report
**Project:** NASA PSI Microgravity Combustion & Spacecraft Fire Safety Data Connector  
**Repo:** `c:\cpp0pw\CODING\NASA\Charizard`  
**Last updated:** 2026-11-15 14:15 IST  
**Overall completion:** ██████████████░ ~95% (Steps 0, 1, 2, 3, 4 done; Step 5 validation report remains)

---

## 📊 At a Glance

| Metric | Value |
|--------|-------|
| Production source files | **20+ (Python + React/JSX)** |
| Total production lines of code | **~4,500 lines** |
| Scratch / exploration scripts | **22** |
| Investigations targeted | **11 PSI IDs + PK4** |
| Raw data ingested | **7.43 MB** across 12 folders |
| Combustion telemetry CSVs | **11 files, 190 KB, 2,241 rows total** |
| FastAPI REST endpoints | **9 endpoints verified live** |
| Frontend Dashboard pages | **8 scientific workspace pages** |
| Steps completed | **0, 1, 2, 3, 4 of 5** |

---

## 🗂️ Repository Structure

```
Charizard/
├── README.md                        (full project documentation)
├── HOW_to_RUN.md                    (quick-start guide for frontend, backend, pipelines)
├── technical_progress.md            (this comprehensive progress document)
├── LICENSE                          (Apache 2.0)
├── inventory.csv                    (300-row S3 bucket file listing)
├── fetch_combustion_data.py         (440 lines — targeted combustion fetcher)
│
├── data/
│   ├── raw/                         ← 7.43 MB of raw PSI records & manifests
│   │   ├── PSI-69/   (FLEX)         metadata + CSV (274 runs)
│   │   ├── PSI-68/   (FLEX-2)       metadata + CSV (8 runs)
│   │   ├── PSI-98/   (SAFFIRE-I)    metadata + CSV (4 burns)
│   │   ├── PSI-99/   (SAFFIRE-II)   metadata + CSV (15 burns)
│   │   ├── PSI-25/   (BASS-II)      metadata (890 KB) + CSV (129 runs)
│   │   ├── PSI-26/   (BASS)         metadata + CSV (122 runs)
│   │   ├── PSI-107/  (SPICE)        metadata + CSV (469 runs)
│   │   ├── PSI-60/   (SPICE Anal.)  metadata (no CSV in repo)
│   │   ├── PSI-102/  (SAME)         metadata + CSV (8 aerosol runs)
│   │   ├── PSI-159/  (ACME CFI-G)   metadata + 2 CSVs (1,194 runs)
│   │   ├── PSI-20/   (ACME BRE)     metadata + CSV (18 runs)
│   │   └── PK4/                     8 campaign PDFs + extracted TXT
│   │
│   ├── processed/                   ← Ready for GEMINI_API_KEY run
│   │
│   └── combustion/                  ← 11 CSVs, summary_report.md, summary_report.json
│
├── src/
│   ├── ingest/
│   │   ├── s3_inventory.py          (S3 anonymous bucket scanner)
│   │   └── ingest_psi.py            (Provenance ingestion engine)
│   ├── extract/
│   │   ├── schema.py                (Pydantic v2 data model)
│   │   ├── extract_investigations.py (LLM extraction pipeline with retry)
│   │   └── generate_investigation_catalog.py
│   └── api/
│       ├── main.py                  (FastAPI application with 9 endpoints)
│       ├── seed_data.py             (Standalone seeding utility)
│       └── mock_investigations.json (Self-contained offline backup data)
│
└── app/                             ← React 18 + Tailwind + Plotly scientific workspace
    ├── package.json
    ├── tailwind.config.js
    ├── vite.config.js
    └── src/
        ├── App.jsx                  (Router setup with dark space theme)
        ├── api/
        │   └── client.js            (Axios client with automatic mock fallback)
        ├── components/
        │   ├── Layout.jsx           (Persistent sidebar + research header)
        │   ├── Sidebar.jsx          (Navigation with active flame indicators)
        │   ├── StatusBadge.jsx      (verified, extracted, inferred, unavailable badges)
        │   ├── FieldCard.jsx        (Scientific field card with quote & location)
        │   ├── InvestigationCard.jsx(Metric-rich summary cards)
        │   ├── FilterChip.jsx       (Interactive multi-state filters)
        │   ├── LoadingSpinner.jsx
        │   └── EmptyState.jsx
        └── pages/
            ├── Overview.jsx         (Mission Control hero, charts, featured cards)
            ├── Explorer.jsx         (Live search, multi-attribute filter chips)
            ├── InvestigationDetail.jsx (Field status cards, telemetry view, scatter plot)
            ├── Compare.jsx          (Side-by-side matrix, divergent diffs, radar plot)
            ├── ScenarioAnalysis.jsx (ISS, Moon base, Mars, Rover scored rankings)
            ├── AskAI.jsx            (Scientific QA with citations & starter queries)
            ├── ResearchGaps.jsx     (O2 vs. Airflow envelope, partial-gravity alert)
            └── DataExport.jsx       (Selective fields, flat/nested toggle, CSV/JSON)
```

---

## 🚀 Completed Milestones

### ✅ Step 0: S3 Exploration & Inventory
- Anonymous S3 scanning via `boto3` without AWS credentials
- Reverse-engineered the NASA PSI Angular application to uncover `/geode-py/ws/repo/` backend API
- Created `inventory.csv` (300 files) and selected 15 core microgravity combustion investigations

### ✅ Step 1: Raw Data Ingestion with Cryptographic Provenance
- Ingested 11 investigations + PK4 dusty plasma campaign documents (7.43 MB)
- Per-investigation `manifest.json` with SHA-256 hashes, timestamps, and S3/HTTP source links
- Extracted PDF plain text with page demarcation (`--- Page N ---`) for downstream citations
- Downloaded 11 combustion telemetry CSVs (2,241 experiment runs) with automatic column & unit profiling

### ✅ Step 2: Scientific Extraction Pipeline
- Strict Pydantic v2 validation schema enforcing 0–100% oxygen boundaries and strict enums
- Context aggregation engine bundling metadata, CSV samples, and PDF excerpts
- One-retry recovery on malformed LLM responses with manual-review fallback

### ✅ Step 3: FastAPI Backend Layer (`src/api/main.py`)
- In-memory data store indexing all 11 investigations and their telemetry files on startup
- **All 9 endpoints verified live:**
  1. `GET /api/health` — service status and loaded investigation count
  2. `GET /api/investigations` — list with full-text search (`?q=`), safety category, fuel state, and gravity filters
  3. `GET /api/investigations/{id}` — full record with telemetry summary
  4. `GET /api/compare?ids=PSI-69,PSI-98,PSI-25` — comparison matrix and shared safety category analysis
  5. `GET /api/rank?scenario=iss|moon_base|mars|rover` — multi-attribute scenario scoring with transparent reasons
  6. `GET /api/gaps` — oxygen vs. airflow heatmap data, field coverage stats, and partial-gravity gap quantification
  7. `POST /api/ask` — scientific QA with exact evidence quotes, citations, and source locations
  8. `GET /api/export?format=csv|json` — downloadable structured records
  9. `GET /api/telemetry/{id}` — raw experimental table rows as JSON with file origin tags

### ✅ Step 4: React + Tailwind + Plotly Research Workspace (`app/`)
- Professional dark scientific aesthetic (`space-950` / `space-900` / `flame-500` / `ember-400`)
- **8 fully interactive pages implemented:**
  1. **Overview:** Metric hero, Plotly safety distribution donut, research area bars, featured cards, key gap callout
  2. **Explorer:** Live full-text search, filter chips for fuel state / safety focus / gravity / telemetry
  3. **Investigation Detail:** 15 FieldCards with status badges (`verified`, `extracted`, `inferred`, `unavailable`), exact source quote callouts, first 20 telemetry rows, interactive Plotly scatter plot
  4. **Compare:** Side-by-side attribute comparison for 2–3 experiments, visual indicator for divergent values, Plotly radar chart
  5. **Scenario Analysis:** 4 mission contexts (ISS, Lunar Base, Mars Habitat, Pressurized Rover) with scores (0–100%) and bulleted rationale
  6. **Ask AI:** Grounded chat interface with clickable starter prompts, loading states, and structured evidence citations
  7. **Research Gaps:** Oxygen vs. Airflow scatter envelope, lunar/Martian partial-gravity gap banner (0 of 11 tested), field completeness progress bars
  8. **Data Export:** Interactive column selection, flat vs. nested JSON toggle, instant client-side CSV and JSON downloads
- **Resilience:** Built-in mock data fallback ensures the UI works out-of-the-box even without the Python backend running

---

## 🛠️ Verification & Build Status

- **Backend:** All 8 core API endpoints verified live returning valid data
- **Frontend:** `npm run build` executed in `app/` — built cleanly via Vite in 2.23s with 0 errors
- **Documentation:** `HOW_to_RUN.md` updated with end-to-end instructions for both terminals

