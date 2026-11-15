# 🔥 FlameScope API — Usage Guide

**Base URL:** `http://127.0.0.1:8000`  
**Interactive docs:** `http://127.0.0.1:8000/docs` (Swagger UI)  
**Alternative docs:** `http://127.0.0.1:8000/redoc` (ReDoc)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Endpoints Reference](#endpoints-reference)
3. [Query Parameters & Filtering](#query-parameters--filtering)
4. [Response Schemas](#response-schemas)
5. [Examples](#examples)
6. [Telemetry Data](#telemetry-data)
7. [Error Handling](#error-handling)
8. [Development](#development)

---

## Quick Start

### 1. Start the server

From the repo root (`d:\CODE\byte_builders\Charizard`):

```powershell
# Set PYTHONPATH so `src.api` imports work
$env:PYTHONPATH = "src"

# Start with auto-reload (recommended for development)
python -m uvicorn api.main:app --reload --port 8000
```

Or using the virtualenv directly:

```powershell
& .venv/Scripts/python.exe -m uvicorn api.main:app --reload --port 8000
```

### 2. Verify it's running

```powershell
curl.exe http://127.0.0.1:8000/health
# → {"status": "ok", "records": 11}
```

### 3. Open the interactive docs

Browser: `http://127.0.0.1:8000/docs`

---

## Endpoints Reference

### `GET /` or `GET /health`

Health check. Returns API status and the number of investigation records loaded in the database.

**Response:**
```json
{
  "status": "ok",
  "records": 11
}
```

---

### `GET /investigations`

Returns a filterable, paginated list of investigations. Each item is lightweight (identity fields + denormalized filter columns only — no full `FieldValue` objects).

**Query parameters (all optional):**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `fuel_type` | string | Substring match on fuel type | `?fuel_type=methanol` |
| `fuel_state` | string | Exact match: `solid`, `liquid`, or `gas` | `?fuel_state=liquid` |
| `gravity_condition` | string | Exact match: `microgravity`, `normal_gravity`, or `partial_gravity` | `?gravity_condition=microgravity` |
| `safety_category` | string | Substring match on JSON array of safety categories | `?safety_category=suppression` |
| `oxygen_min` | number | Min O₂ percent (inclusive) | `?oxygen_min=20` |
| `oxygen_max` | number | Max O₂ percent (inclusive) | `?oxygen_max=21` |
| `pressure_min` | number | Min pressure in psi (inclusive) | `?pressure_min=10` |
| `pressure_max` | number | Max pressure in psi (inclusive) | `?pressure_max=15` |
| `sample_shape` | string | Substring match on sample shape | `?sample_shape=droplet` |
| `sample_size` | string | Substring match on sample size | `?sample_size=1.1` |
| `diluents` | string | Substring match on diluent names | `?diluents=He` |
| `hardware` | string | Substring match on experiment hardware | `?hardware=CIR` |
| `sensors_and_measurements` | string | Substring match on sensor types | `?sensors_and_measurements=temperature` |
| `objective` | string | Substring match on investigation objective | `?objective=flammability` |
| `limit` | int | Page size (1–500, default 50) | `?limit=10` |
| `offset` | int | Page offset (default 0) | `?offset=20` |

**Response:**
```json
{
  "count": 11,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "investigation_id": "PSI-69",
      "title": "Flame Extinguishment Experiment",
      "acronym": "FLEX",
      "doi": null,
      "source_url": "https://psi.nasa.gov/investigations/PSI-69",
      "fuel_type": "methanol",
      "fuel_state": "liquid",
      "gravity_condition": "microgravity",
      "oxygen_percent_min": 12.0,
      "oxygen_percent_max": 34.0,
      "pressure_psi": 14.7,
      "airflow_speed_min": null,
      "airflow_speed_max": null,
      "safety_category": null,
      "sample_shape": "droplet",
      "sample_size": "1.1 - 4.67",
      "diluents": ["CO2", "He", "SF6", "N2"],
      "hardware": ["Combustion Integrated Rack (CIR)", ...],
      "sensors_and_measurements": ["droplet burning rates", ...],
      "objective": "Map the flammability limits of liquid fuels..."
    }
  ]
}
```

---

### `GET /investigations/{investigation_id}`

Returns the **full** investigation record, including all 20 fields and every `FieldValue` object (with `value`, `unit`, `status`, `evidence_quote`, `evidence_location`).

**Path parameter:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `investigation_id` | string | Investigation ID (e.g. `PSI-69`) |

**Response:**
```json
{
  "investigation_id": "PSI-69",
  "title": "Flame Extinguishment Experiment",
  "acronym": "FLEX",
  "doi": "10.60555/mbq8-0451",
  "source_url": "https://psi.nasa.gov/investigations/PSI-69",
  "objective": {
    "value": "...",
    "unit": null,
    "status": "extracted",
    "evidence_quote": "...",
    "evidence_location": "..."
  },
  "hardware": { ... },
  "fuel_type": { ... },
  "fuel_state": { ... },
  "sample_shape": { ... },
  "sample_size": { ... },
  "oxygen_percent_min": { ... },
  "oxygen_percent_max": { ... },
  "pressure_psi": { ... },
  "airflow_speed_min": { ... },
  "airflow_speed_max": { ... },
  "diluents": { ... },
  "gravity_condition": { ... },
  "sensors_and_measurements": { ... },
  "safety_category": { ... }
}
```

**404** if the investigation ID does not exist.

---

### `GET /investigations/{investigation_id}/telemetry`

Returns raw telemetry CSV rows as JSON for a given investigation. Filenames are resolved via `data/combustion/summary_report.json` with a glob fallback.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | int | Max rows per CSV file (optional) |

**Response:**
```json
{
  "investigation_id": "PSI-69",
  "files": [
    {
      "filename": "PSI-69_Experimental table_FLEX.csv",
      "columns": ["FLEX Test #", "Fuel", "Ambient pressure", ...],
      "row_count": 274,
      "data": [
        { "FLEX Test #": "1", "Fuel": "Methanol", "Ambient pressure": "757.7", ... },
        { "FLEX Test #": "2", "Fuel": "Methanol", "Ambient pressure": "758.1", ... }
      ]
    }
  ]
}
```

- **PSI-159** returns two files (Normal Flames + Inverse Flames).
- **PSI-60** returns `"files": []` (metadata-only investigation, no CSV).
- Empty strings in CSV cells are converted to `null`.

---

### `POST /compare`

Compares 2–3 investigations side by side, returning aligned attributes plus what varied and what stayed the same.

**Request body:**
```json
{
  "investigation_ids": ["PSI-69", "PSI-98"]
}
```

**Constraints:** Must provide between 2 and 3 investigation IDs. All IDs must exist.

**Response:**
```json
{
  "investigations": [ {full record 1}, {full record 2} ],
  "aligned_table": [
    { "investigation_id": "PSI-69", "title": "...", "fuel_type": "...", ... },
    { "investigation_id": "PSI-98", "title": "...", "fuel_type": "...", ... }
  ],
  "what_varied": ["fuel_type", "oxygen_percent_min", "gravity_condition", ...],
  "what_stayed_same": ["acronym", "doi"],
  "telemetry_summary": [
    { "investigation_id": "PSI-69", "columns": { "Fuel": "likely varies", ... } },
    { "investigation_id": "PSI-98", "columns": { ... } }
  ]
}
```

- `aligned_table` includes all 20 schema fields with `value`, `unit`, and `status` sub-columns.
- `what_varied` lists attributes that differ across the selected investigations.
- `what_stayed_same` lists attributes identical across all selected investigations.
- `telemetry_summary` lists which telemetry columns likely vary row-to-row for each investigation.

**422** if fewer than 2 or more than 3 IDs provided.  
**404** if any investigation ID is not found.

---

### `GET /search`

Lightweight text search across investigation fields, with optional structured filters.

**Query parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `q` | string | **Required.** Text search query (space-separated terms) | `?q=liquid oxygen microgravity` |
| `fuel_type` | string | Substring match on fuel type | `&fuel_type=methanol` |
| `fuel_state` | string | Exact match: `solid`, `liquid`, or `gas` | `&fuel_state=liquid` |
| `gravity_condition` | string | Exact match: `microgravity`, `normal_gravity`, or `partial_gravity` | `&gravity_condition=microgravity` |
| `safety_category` | string | Exact match on safety category item | `&safety_category=suppression` |
| `limit` | int | Max results (1–50, default 10) | `&limit=5` |

**How scoring works:**
1. The query is split into lowercase terms (e.g. `"liquid oxygen"` → `["liquid", "oxygen"]`).
2. For each investigation, a text blob is built from: `title`, `acronym`, `doi`, `source_url`, `objective`, `hardware`, `fuel_type`, `fuel_state`, `gravity_condition`, `safety_category`, `sample_shape`, `sample_size`, `diluents`, `pressure_psi`, `sensors_and_measurements`, `airflow_speed_min`, `airflow_speed_max`.
3. Relevance = (matched terms) / (total terms). Investigations with 0 matches are excluded.
4. Structured filters are applied on top.
5. Results sorted by relevance descending.

**Response:**
```json
{
  "query": "liquid oxygen microgravity",
  "matches": [
    {
      "investigation_id": "PSI-69",
      "title": "Flame Extinguishment Experiment",
      "relevance": 1.0,
      "matched_terms": ["liquid", "oxygen", "microgravity"]
    }
  ],
  "count": 1
}
```

### `POST /chat`

Natural language research assistant bot translating user queries into FlameScope API calls via Gemini agent with minimal per-user context tracking.

**Query parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `user` | string | **Required.** Per-user identifier (1-100 characters) | `?user=researcher_01` |

**Request body:**
```json
{
  "msg": "search liquid oxygen experiments"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Found 5 experiments involving liquid oxygen: PSI-69 (Flame Extinguishment Experiment)... Would you like details on any?"
}
```

For complete bot behavior, context isolation, and tool calling documentation, see [docs/CHAT_BOT.md](file:///D:/CODE/byte_builders/Charizard/docs/CHAT_BOT.md).

---

### `POST /reload`

Re-loads all records from `data/processed/investigations.json` into SQLite without restarting the server. Useful after re-running Step 2 extraction.

**Response:**
```json
{
  "status": "reloaded",
  "records": 11
}
```

**404** if `data/processed/investigations.json` does not exist.

---

### `GET /docs` / `GET /redoc`

Interactive API documentation (Swagger UI / ReDoc). Try any endpoint directly from the browser.

---

### `GET /investigations/{investigation_id}`

Returns the **full** investigation record, including all 20 fields and every `FieldValue` object (with `value`, `unit`, `status`, `evidence_quote`, `evidence_location`).

**Path parameter:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `investigation_id` | string | Investigation ID (e.g. `PSI-69`) |

**Response:**
```json
{
  "investigation_id": "PSI-69",
  "title": "Flame Extinguishment Experiment",
  "acronym": "FLEX",
  "doi": null,
  "source_url": "https://psi.nasa.gov/investigations/PSI-69",
  "objective": {
    "value": "...",
    "unit": null,
    "status": "extracted",
    "evidence_quote": "...",
    "evidence_location": "..."
  },
  "hardware": { ... },
  "fuel_type": { ... },
  "fuel_state": { ... },
  "sample_shape": { ... },
  "sample_size": { ... },
  "oxygen_percent_min": { ... },
  "oxygen_percent_max": { ... },
  "pressure_psi": { ... },
  "airflow_speed_min": { ... },
  "airflow_speed_max": { ... },
  "diluents": { ... },
  "gravity_condition": { ... },
  "sensors_and_measurements": { ... },
  "safety_category": { ... }
}
```

**404** if the investigation ID does not exist.

---

### `GET /investigations/{investigation_id}/telemetry`

Returns raw telemetry CSV rows as JSON for a given investigation. Filenames are resolved via `data/combustion/summary_report.json` with a glob fallback.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | int | Max rows per CSV file (optional) |

**Response:**
```json
{
  "investigation_id": "PSI-69",
  "files": [
    {
      "filename": "PSI-69_Experimental table_FLEX.csv",
      "columns": ["FLEX Test #", "Fuel", "Ambient pressure", ...],
      "row_count": 274,
      "data": [
        { "FLEX Test #": "1", "Fuel": "Methanol", "Ambient pressure": "757.7", ... },
        { "FLEX Test #": "2", "Fuel": "Methanol", "Ambient pressure": "758.1", ... }
      ]
    }
  ]
}
```

- **PSI-159** returns two files (Normal Flames + Inverse Flames).
- **PSI-60** returns `"files": []` (metadata-only investigation, no CSV).
- Empty strings in CSV cells are converted to `null`.

---

### `POST /reload`

Re-loads all records from `data/processed/investigations.json` into SQLite without restarting the server. Useful after re-running Step 2 extraction.

**Response:**
```json
{
  "status": "reloaded",
  "records": 11
}
```

**404** if `data/processed/investigations.json` does not exist.

---

### `GET /docs` / `GET /redoc`

Interactive API documentation (Swagger UI / ReDoc). Try any endpoint directly from the browser.

---

## Query Parameters & Filtering

### Filter logic

| Filter | Operator | Notes |
|--------|----------|-------|
| `fuel_type` | `LIKE` (substring, case-sensitive) | Matches any fuel type containing the string |
| `fuel_state` | `=` (exact) | Must be exactly `solid`, `liquid`, or `gas` |
| `gravity_condition` | `=` (exact) | Must be exactly `microgravity`, `normal_gravity`, or `partial_gravity` |
| `safety_category` | `LIKE` on JSON text | Matches any category in the JSON array |
| `oxygen_min` | `oxygen_percent_max >= value` | Investigation's max O₂ must be ≥ your min |
| `oxygen_max` | `oxygen_percent_min <= value` | Investigation's min O₂ must be ≤ your max |
| `pressure_min` | `pressure_psi >= value` | Investigation's pressure must be ≥ your min |
| `pressure_max` | `pressure_psi <= value` | Investigation's pressure must be ≤ your max |

### Combined filters

Multiple filters are ANDed together. Example:

```powershell
curl.exe "http://127.0.0.1:8000/investigations?fuel_state=liquid&gravity_condition=microgravity&safety_category=suppression"
```

### Pagination

Use `limit` and `offset` to page through results. The `count` field in the response tells you the total number of matching records (before pagination).

```powershell
# Page 1: first 5 results
curl.exe "http://127.0.0.1:8000/investigations?limit=5&offset=0"

# Page 2: next 5 results
curl.exe "http://127.0.0.1:8000/investigations?limit=5&offset=5"
```

---

## Response Schemas

### Investigation list item (from `GET /investigations`)

| Field | Type | Description |
|-------|------|-------------|
| `investigation_id` | string | e.g. `"PSI-69"` |
| `title` | string | Human-readable title |
| `acronym` | string \| null | e.g. `"FLEX"` |
| `doi` | string \| null | DOI identifier |
| `source_url` | string | PSI investigation URL |
| `fuel_type` | string \| null | Fuel type(s), may be JSON array text |
| `fuel_state` | string \| null | `solid` \| `liquid` \| `gas` |
| `gravity_condition` | string \| null | `microgravity` \| `normal_gravity` \| `partial_gravity` |
| `oxygen_percent_min` | number \| null | Minimum O₂ percent |
| `oxygen_percent_max` | number \| null | Maximum O₂ percent |
| `pressure_psi` | number \| null | Ambient pressure in psi |
| `airflow_speed_min` | number \| null | Minimum airflow (cm/s) |
| `airflow_speed_max` | number \| null | Maximum airflow (cm/s) |
| `safety_category` | string \| null | JSON array text, e.g. `["prevention","detection"]` |

### FieldValue object (in full record)

Every non-identity field in the full record is a `FieldValue`:

| Field | Type | Description |
|-------|------|-------------|
| `value` | string \| number \| list \| null | The extracted value |
| `unit` | string \| null | Unit of measurement |
| `status` | string | `verified` \| `extracted` \| `inferred` \| `unavailable` |
| `evidence_quote` | string \| null | Verbatim quote from source |
| `evidence_location` | string \| null | Where the quote was found |
| `evidence_location` | string \\| null | Where the quote was found |

---

## Examples

### Get all investigations
```powershell
curl.exe http://127.0.0.1:8000/investigations
```

### Get only liquid-fuel investigations
```powershell
curl.exe "http://127.0.0.1:8000/investigations?fuel_state=liquid"
```

### Get investigations with O₂ between 20% and 25%
```powershell
curl.exe "http://127.0.0.1:8000/investigations?oxygen_min=20&oxygen_max=25"
```

### Get full detail for FLEX (PSI-69)
```powershell
curl.exe http://127.0.0.1:8000/investigations/PSI-69
```

### Get first 3 rows of FLEX telemetry
```powershell
curl.exe "http://127.0.0.1:8000/investigations/PSI-69/telemetry?limit=3"
```

### Re-load data after Step 2 re-run
```powershell
curl.exe -X POST http://127.0.0.1:8000/reload
```

---

## Telemetry Data

Telemetry CSVs live in `data/combustion/` and are indexed by `data/combustion/summary_report.json`.

| Investigation | File(s) | Rows |
|--------------|---------|------|
| PSI-69 (FLEX) | `PSI-69_Experimental table_FLEX.csv` | 274 |
| PSI-68 (FLEX-2) | `PSI-68_Experimental table_Flex2.csv` | 8 |
| PSI-98 (SAFFIRE-I) | `PSI-98_Experimental table_SAFFIRE-1.csv` | 4 |
| PSI-99 (SAFFIRE-II) | `PSI-99_Experimental table_SAFFIRE-2.csv` | 15 |
| PSI-25 (BASS-II) | `PSI-25_Experimental table_BASS-II.csv` | 129 |
| PSI-26 (BASS) | `PSI-26_Experimental table_BASS.csv` | 122 |
| PSI-107 (SPICE) | `PSI-107_Experimental table_Spice.csv` | 469 |
| PSI-102 (SAME) | `PSI-102_Experimental table_SAME.csv` | 8 |
| PSI-159 (ACME CFI-G) | 2 CSV files (Normal + Inverse Flames) | 179 + 1,015 |
| PSI-20 (ACME BRE) | `PSI-20_Experimental table_ACME BRE.csv` | 18 |
| PSI-60 (SPICE Anal.) | none (metadata-only) | 0 |

**Total:** 2,241 rows across 11 CSV files.
**Total:** 2,241 rows across 11 CSV files.

---

## Error Handling

| Status | Meaning |
|--------|---------|
| `200 OK` | Request succeeded |
| `404 Not Found` | Investigation ID not found, or `investigations.json` missing on `/reload` |
| `422 Unprocessable Entity` | Invalid query parameters (e.g. `limit` out of range) |
| `500 Internal Server Error` | Server error (check logs) |

All errors return JSON:
```json
{
  "detail": "Investigation PSI-999 not found"
}
```

---

## Development

### Project structure

```
src/api/
├── __init__.py      # Package marker
├── db.py            # SQLite DDL, load_records, list_investigations, get_investigation
└── main.py          # FastAPI app, all route handlers
```

### Database

- **File:** `data/flamescope.db` (SQLite, created on first startup)
- **Schema:** Hybrid — denormalized filter columns + `record_json` TEXT blob
- **Auto-load:** On startup, `load_records()` reads `data/processed/investigations.json` and upserts all 11 records

### Adding a new endpoint

1. Add the route handler to `src/api/main.py`
2. Add any needed query functions to `src/api/db.py`
3. Restart the server (or use `--reload`)

### Quick verification commands

```powershell
# Health check
curl.exe http://127.0.0.1:8000/health

# Verify all 11 records loaded
curl.exe http://127.0.0.1:8000/investigations | ConvertFrom-Json | Select-Object count

# Spot-check a detail record
curl.exe http://127.0.0.1:8000/investigations/PSI-69 | ConvertFrom-Json
```

---

## Related Files

| File | Purpose |
|------|---------|
| `src/api/db.py` | SQLite data access layer |
| `src/api/main.py` | FastAPI routes & app |
| `src/extract/schema.py` | Pydantic data model (`InvestigationExtracted`, `FieldValue`) |
| `data/processed/investigations.json` | Combined extracted records (Step 2 output) |
| `data/combustion/summary_report.json` | Telemetry CSV index |
| `PROGRESS.md` | Project progress report |