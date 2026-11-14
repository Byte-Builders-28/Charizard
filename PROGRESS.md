# 🔥 FlameScope — Technical Progress Report

**Project:** NASA PSI Microgravity Combustion & Spacecraft Fire Safety Data Connector  
**Repo:** `c:\cpp0pw\CODING\NASA\Charizard`  
**Last updated:** 2026-11-14 20:15 IST  
**Overall completion:** ██████████░░░░░ ~60% (Steps 0-2 done; Step 3 in progress; Steps 4-5 remain)

---

## 📊 At a Glance

| Metric                         | Value                                  |
| ------------------------------ | -------------------------------------- |
| Production source files        | **6**                                  |
| Total production lines of code | **1,952 lines**                        |
| Scratch / exploration scripts  | **22**                                 |
| Investigations targeted        | **11 PSI IDs + PK4**                   |
| Raw data ingested              | **7.43 MB** across 12 folders          |
| Combustion telemetry CSVs      | **11 files, 190 KB, 2,241 rows total** |
| Pydantic schema fields         | **15 FieldValue + 5 identity fields**  |
| Validation tests passing       | **6 / 6**                              |
| Steps completed                | **0, 1, 2 of 5**                       |

---

## 🗂️ Repository Structure (current state)

```
Charizard/
├── README.md                        (231 lines — full project guide)
├── HOW_to_RUN.md                    (quick-start cheat sheet)
├── LICENSE                          (Apache 2.0)
├── inventory.csv                    (300-row S3 bucket file listing)
├── ingest.log                       (timestamped ingestion run log)
├── fetch_combustion_data.py         (440 lines — targeted combustion fetcher)
│
├── data/
│   ├── raw/                         ← 7.43 MB of untouched source records
│   │   ├── PSI-69/   (FLEX)         investigation_metadata.json + FLEX.csv
│   │   ├── PSI-68/   (FLEX-2)       investigation_metadata.json + Flex2.csv
│   │   ├── PSI-98/   (SAFFIRE-I)    investigation_metadata.json + SAFFIRE-1.csv
│   │   ├── PSI-99/   (SAFFIRE-II)   investigation_metadata.json + SAFFIRE-2.csv
│   │   ├── PSI-25/   (BASS-II)      investigation_metadata.json (890 KB!) + BASS-II.csv
│   │   ├── PSI-26/   (BASS)         investigation_metadata.json + BASS.csv
│   │   ├── PSI-107/  (SPICE)        investigation_metadata.json + Spice.csv
│   │   ├── PSI-60/   (SPICE Anal.)  investigation_metadata.json only
│   │   ├── PSI-102/  (SAME)         investigation_metadata.json + SAME.csv
│   │   ├── PSI-159/  (ACME CFI-G)   investigation_metadata.json + 2 CSV files
│   │   ├── PSI-20/   (ACME BRE)     investigation_metadata.json + ACME BRE.csv
│   │   └── PK4/                     8 campaign PDFs + extracted TXTs + sensor IDs
│   │
│   ├── processed/                   ← POPULATED — 11 investigation JSON records + review CSVs
│   │   ├── investigations.json     (combined array of 11 validated records)
│   │   ├── PSI-*.json              (11 per-investigation structured records)
│   │   ├── PSI-*_review.csv        (11 human verification sheets)
│   │   └── .gitignore
│   │
│   └── combustion/                  ← 11 CSVs, summary_report.md, summary_report.json
│       ├── PSI-69_Experimental table_FLEX.csv        (274 rows, 15 cols)
│       ├── PSI-68_Experimental table_Flex2.csv       (8 rows, 7 cols)
│       ├── PSI-98_Experimental table_SAFFIRE-1.csv   (4 rows, 13 cols)
│       ├── PSI-99_Experimental table_SAFFIRE-2.csv   (15 rows, 17 cols)
│       ├── PSI-25_Experimental table_BASS-II.csv     (129 rows, 17 cols)
│       ├── PSI-26_Experimental table_BASS.csv        (122 rows, 6 cols)
│       ├── PSI-107_Experimental table_Spice.csv      (469 rows, 9 cols)
│       ├── PSI-102_Experimental table_SAME.csv       (8 rows, 5 cols)
│       ├── PSI-159_CFI-G_Normal Flames.csv           (179 rows, 18 cols)
│       ├── PSI-159_CFI-G_Inverse Flames.csv          (1,015 rows, 20 cols)
│       ├── PSI-20_Experimental table_ACME BRE.csv    (18 rows, 8 cols)
│       ├── summary_report.md                         (human-readable schema report)
│       └── summary_report.json                       (machine-readable for the app)
│
├── docs/
│   ├── core_investigations.csv      (15 investigations, DOIs, file types)
│   └── core_investigations.md       (Markdown table)
│
├── src/
│   ├── ingest/
│   │   ├── s3_inventory.py          (186 lines — S3 scanner)
│   │   └── ingest_psi.py            (443 lines — provenance ingestion engine)
│   └── extract/
│       ├── schema.py                (152 lines — Pydantic data model)
│       ├── extract_investigations.py (622 lines — LLM extraction pipeline)
│       └── generate_investigation_catalog.py (109 lines)
│
└── scratch/                         (22 exploration scripts — temporary)
    ├── api/           (scratch_api.py - scratch_api4.py)
    ├── chunk/         (scratch_chunk.py - scratch_chunk3.py)
    └── *.py           (15 other exploratory scripts)
```

---

## ✅ Step 0 — S3 Exploration & Investigation Catalog

**Status: COMPLETE**

### What was done

- Reverse-engineered the NASA PSI Angular SPA to find the hidden `/geode-py/ws/` REST backend
- Discovered the public `nasa-psi` S3 bucket (unsigned, us-west-2) has only 3 non-combustion prefixes (`DSI/`, `OASIS/`, `pk4/`) — combustion data is in the private `psi-repo-prod` bucket behind presigned URLs
- Identified the PSI search API: `GET https://psi.nasa.gov/geode-py/ws/repo/search` → 133 total investigations
- Selected **15 core combustion investigations** (FLEX, FLEX-2, SAFFIRE-I/II, BASS, BASS-II, SPICE, SAME, ACME CFI-G, ACME BRE, ACME FD, ACME Flame Design)

### Output files

| File                           | Description                                              |
| ------------------------------ | -------------------------------------------------------- |
| `inventory.csv`                | 300-row S3 file listing (key, size, extension)           |
| `docs/core_investigations.csv` | 15 investigations with DOI, source URL, file types       |
| `docs/core_investigations.md`  | Same as Markdown table                                   |
| `src/ingest/s3_inventory.py`   | 186-line CLI tool — `--prefix`, `--max-keys`, `--output` |

### Key API discovery

```
GET https://psi.nasa.gov/geode-py/ws/repo/investigations/<PSI-ID>
  → returns: title, doi, description, objective, approach, hypothesis,
             experimentHardware, factors, payloads, experimentalTable,
             publications, flightProgram, researchArea, subResearchArea

GET https://psi.nasa.gov/geode-py/ws/studies/<PSI-ID>/download?file=<name>&redirect=false
  → returns: presigned S3 URL (15-min TTL) to psi-repo-prod bucket
```

---

## ✅ Step 1 — Raw Data Ingestion with Provenance

**Status: COMPLETE**

### What was done

- Built a full provenance-tracked ingestion engine targeting 11 PSI investigations
- Downloaded investigation metadata JSON + experimental CSVs for all 11 IDs
- Ingested 8 campaign PDFs from the public `pk4/` S3 prefix
- Extracted plain text from every PDF with `--- Page N ---` delimiters for citation support
- Generated SHA-256 checksums for every file; logged to per-investigation `manifest.json`

### `src/ingest/ingest_psi.py` — 443 lines

| Feature             | Implementation                                                                            |
| ------------------- | ----------------------------------------------------------------------------------------- |
| Idempotency         | Skips files matching existing size + SHA-256                                              |
| Retry logic         | Exponential backoff on network errors (3 attempts)                                        |
| File size guard     | Hard skip for files > 25 MB                                                               |
| PDF text extraction | `pypdf` → companion `_extracted.txt` with page markers                                    |
| Failure logging     | `ingest_failures.log` with timestamp + URL                                                |
| Manifest format     | `source_url`, `s3_key`, `retrieved_at` (UTC ISO-8601), `size_bytes`, `sha256`, `category` |

### Data ingested

```
PSI-69  FLEX          40 KB metadata + 24 KB CSV (274 runs)
PSI-68  FLEX-2        39 KB metadata + 1 KB CSV  (8 runs)
PSI-98  SAFFIRE-I     175 KB metadata + 469 B CSV (4 burns)
PSI-99  SAFFIRE-II    12 KB metadata + 2 KB CSV  (15 burns)
PSI-25  BASS-II       890 KB metadata + 16 KB CSV (129 samples)
PSI-26  BASS          251 KB metadata + 5 KB CSV  (122 samples)
PSI-107 SPICE         423 KB metadata + 31 KB CSV (469 runs)
PSI-60  SPICE Anal.   8 KB metadata only
PSI-102 SAME          178 KB metadata + 331 B CSV (8 aerosol runs)
PSI-159 ACME CFI-G    metadata + 22 KB + 39 KB CSV (1,194 flame runs)
PSI-20  ACME BRE      21 KB metadata + 1 KB CSV  (18 runs)
PK4     dusty plasma  8 PDFs, campaign reports 1-8, extracted text
```

**Total raw data on disk: 7.43 MB**

---

## ✅ Combustion Telemetry Fetcher

**Status: COMPLETE** _(bonus deliverable)_

### `fetch_combustion_data.py` — 440 lines

- Targeted scanner for FLEX, Saffire, ACME, BASS, SPICE, SAME experiments
- Filters: downloads `.csv/.xlsx/.json/.txt/.pdf` under 25 MB; skips `.mp4/.avi/.bmp` raw video
- Downloaded all 11 structured telemetry CSVs into `data/combustion/`
- Auto-generated `summary_report.md` and `summary_report.json` with column names, units, row counts, and sample values for every file

### Telemetry coverage

| Investigation                | Rows      | Key measurement columns                                                                                                     |
| ---------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------- |
| FLEX (PSI-69)                | 274       | Ambient pressure (mmHg), O₂ mole fraction, He/N₂/CO₂ composition, droplet diameter (mm), burning rate (mm/s), burn time (s) |
| FLEX-2 (PSI-68)              | 8         | Fuel, pressure, oxygen, droplet size                                                                                        |
| SAFFIRE-I (PSI-98)           | 4         | % O₂, airflow (cm/s), sample dimensions (cm), heat release rate                                                             |
| SAFFIRE-II (PSI-99)          | 15        | O₂ %, airflow, mass loss rate, spread rate                                                                                  |
| BASS-II (PSI-25)             | 129       | Air flow, O₂ %, fuel type, burning rate                                                                                     |
| BASS (PSI-26)                | 122       | Airflow (cm/s), fuel, test conditions                                                                                       |
| SPICE (PSI-107)              | 469       | Fuel flow, O₂ %, smoke point height                                                                                         |
| SAME (PSI-102)               | 8         | Particle size, aerosol concentration                                                                                        |
| ACME CFI-G Normal (PSI-159)  | 179       | Flame temperature (K), pressure (bar), fuel mass flow (mg/s)                                                                |
| ACME CFI-G Inverse (PSI-159) | 1,015     | Flame temperature (K), pressure, fuel flow                                                                                  |
| ACME BRE (PSI-20)            | 18        | Fuel type, burning rate, droplet diameter                                                                                   |
| **TOTAL**                    | **2,241** |                                                                                                                             |

---

## ✅ Step 2 — Scientific Extraction Pipeline

**Status: COMPLETE — all 11 investigations extracted**

### What was built

#### `src/extract/schema.py` — 152 lines

Full Pydantic v2 data model with 20 fields per investigation. Every non-identity field is a `FieldValue`:

```json
{
	"value": "methanol",
	"unit": null,
	"status": "extracted",
	"evidence_quote": "Fuel: Methanol",
	"evidence_location": "PSI-69_Experimental table_FLEX.csv, header row"
}
```

**Validated enums (Pydantic enforced — 6/6 boundary tests pass ✅):**

| Field                    | Allowed values                                          |
| ------------------------ | ------------------------------------------------------- |
| `fuel_state`             | `solid` \| `liquid` \| `gas`                            |
| `gravity_condition`      | `microgravity` \| `normal_gravity` \| `partial_gravity` |
| `safety_category`        | list from `prevention` \| `detection` \| `suppression`  |
| `oxygen_percent_min/max` | numeric, **0-100 strictly enforced**                    |

#### `src/extract/extract_investigations.py` — 622 lines

```
build_context()  [per investigation]
  ├─ investigation_metadata.json → 16 labeled text fields (title, objective, hardware, …)
  ├─ *.csv → header + 8 sample rows + min/max column stats across all rows
  ├─ *_extracted.txt → PDF text with page markers (capped at 3,000 chars)
  └─ *.txt → plain text files
  → total capped at 28,000 chars (~7k tokens, keeps costs low)

call_llm()  [Gemini 2.5 Flash, temperature=0]
  ├─ system: "Use ONLY the text provided. Do not infer numbers…"
  ├─ schema description with unit-conversion rules
  │   (mole fraction × 100 → %, mmHg ÷ 51.715 → psi)
  └─ structured JSON response

Pydantic validate()
  ├─ PASS → data/processed/<PSI-ID>.json
  │          data/processed/<PSI-ID>_review.csv
  └─ FAIL → retry once with error appended to prompt
       ├─ PASS → saved
       └─ FAIL → <PSI-ID>.REVIEW_NEEDED.json
                  extraction_failures.log

(after all IDs) → data/processed/investigations.json  [combined array]
```

**Output files per investigation:**

| File                                 | Purpose                                                  |
| ------------------------------------ | -------------------------------------------------------- |
| `data/processed/<PSI-ID>.json`       | Validated structured record (20 fields)                  |
| `data/processed/<PSI-ID>_review.csv` | 15 rows, one per schema field — human verification sheet |
| `data/processed/investigations.json` | Combined array — direct feed for the app                 |
| `<PSI-ID>.REVIEW_NEEDED.json`        | Raw LLM output + error (only on double-failure)          |

**To run Step 2 (if re-extraction is needed):**

```powershell
$env:GEMINI_API_KEY = "your_key_here"   # get free at aistudio.google.com/apikey
python src/extract/extract_investigations.py
# specific subset:
python src/extract/extract_investigations.py --investigations PSI-69 PSI-98 PSI-25
# test pipeline structure without LLM (no API key needed):
python src/extract/extract_investigations.py --dry-run
# override model (if gemini-2.5-flash is deprecated):
python src/extract/extract_investigations.py --model gemini-3.8-flash
```

**Note:** The default `gemini-2.5-flash` model returned a 404 for new users; use `--model gemini-3.8-flash` if needed.

---

## 🔄 Remaining Steps

```
Step 3  Database & API Layer       ███░░░░░░░░  IN PROGRESS (data ready)
Step 4  Fire-Safety Web App        ░░░░░░░░░░  NOT STARTED
Step 5  Validation & Reporting     ░░░░░░░░░░  NOT STARTED
```

### Step 3 — Database & API Layer

FastAPI + SQLite backend serving extracted data. **All 11 investigation records are already in `data/processed/investigations.json`**, so the DB can be populated immediately on startup.

- `GET /investigations` — filterable list (fuel_type, safety_category, gravity_condition)
- `GET /investigations/{id}` — full record with all FieldValues
- `GET /investigations/{id}/telemetry` — raw CSV rows as JSON
- OpenAPI docs, CORS, error handling

**Est. effort:** 1-2 hours | **Target files:** `src/api/main.py`, `src/api/db.py`

### Step 3 — Database & API Layer

FastAPI + SQLite backend serving extracted data:

- `GET /investigations` — filterable list (fuel_type, safety_category, gravity_condition)
- `GET /investigations/{id}` — full record with all FieldValues
- `GET /investigations/{id}/telemetry` — raw CSV rows as JSON
- OpenAPI docs, CORS, error handling

**Est. effort:** 1-2 hours | **Target files:** `src/api/main.py`, `src/api/db.py`

### Step 4 — Fire-Safety Web App

Interactive frontend in `app/`:

- Investigation cards with safety classification badges (prevention / detection / suppression)
- Telemetry scatter plots (O₂ % vs. burn time, pressure vs. extinction diameter)
- Cross-investigation comparison view
- Filter sidebar (fuel type, gravity condition, hardware)

**Est. effort:** 2-3 hours | **Target files:** `app/index.html`, `app/main.js`, `app/style.css`

### Step 5 — Validation & Reporting

- Automated cross-check: extracted O₂/pressure values vs. raw CSV `min/max` stats
- Manual spot-check: PSI-69 (FLEX), PSI-98 (SAFFIRE-I), PSI-25 (BASS-II)
- Final `docs/validation_report.md`

**Est. effort:** 30-60 min

---

## 🧪 Exploration Work (scratch/ — 22 scripts)

| Script                            | Discovery                                                         |
| --------------------------------- | ----------------------------------------------------------------- |
| `scratch_geode.py`                | Found `/geode-py/ws/` REST backend by parsing minified Angular JS |
| `scratch_api.py - api4.py`        | Tested PSI search, download, and presigned URL flow               |
| `scratch_search_combustion.py`    | Identified 11 target PSI IDs from 133-investigation corpus        |
| `scratch_psi69.py`                | First inspection of PSI-69 metadata structure and CSV headers     |
| `scratch_parse_all_combustion.py` | Extracted min/max O₂, pressure, airflow across all CSVs           |
| `scratch_test_download_api.py`    | Reverse-engineered presigned URL download mechanism               |
| `scratch_chunk.py - chunk3.py`    | Prototyped context chunking strategies for the LLM                |

---

## 🛠️ Technical Stack

| Layer             | Technology                                           |
| ----------------- | ---------------------------------------------------- |
| Language          | Python 3.13.5                                        |
| S3 access         | `boto3` (unsigned/anonymous)                         |
| HTTP client       | `requests` with retry + backoff                      |
| PDF extraction    | `pypdf`                                              |
| Data manipulation | `pandas`, `csv` stdlib                               |
| Schema validation | `pydantic` v2.13.4                                   |
| LLM               | Google Gemini 2.5 Flash (`google-generativeai`)      |
| Data format       | JSON (manifests, extracted records), CSV (telemetry) |
| Docs              | Markdown                                             |

---

## ⚠️ Known Issues & Blockers

| Issue                                                         | Status                                                                            |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| PSI-60 has no experimental CSV (`experimentalTable` is empty) | Known — metadata-only record; extraction filled what was available                |
| PSI-25 metadata is 890 KB — context truncated to 28,000 chars | Mitigated — CSV stats + narrative fields fit well within budget                   |
| PK4 PDF text is sparse (1-3 KB extracted from 350 KB PDFs)    | Known — PDFs are image-heavy; OCR not implemented                                 |
| `nasa-psi` S3 bucket has no combustion data                   | Resolved — combustion data lives in private `psi-repo-prod`, accessed via PSI API |

---

_Generated automatically from live workspace state — 2026-11-14 20:15 IST_
