# FlameScope: NASA Microgravity Combustion Science & Spacecraft Fire Safety Data Connector

**FlameScope** is an open-science microgravity data platform built to explore, ingest, and analyze Combustion Science and Spacecraft Fire Safety investigations from **NASA Physical Sciences Informatics (PSI)** and the public AWS S3 bucket `nasa-psi` (`us-west-2`, unsigned access).

---

## 📁 Repository Structure

```text
├── README.md                      # Complete project documentation and guide
├── inventory.csv                  # S3 inventory catalog (prefix, key, size_bytes, extension)
├── fetch_combustion_data.py       # Specialized combustion & fire-safety telemetry fetcher
├── data/
│   ├── raw/                       # Untouched raw records with provenance manifests
│   │   ├── PSI-69/                # FLEX (Flame Extinguishment Experiment)
│   │   ├── PSI-68/                # FLEX-2
│   │   ├── PSI-98/                # SAFFIRE-I (Spacecraft Fire Safety Demonstration)
│   │   ├── PSI-99/                # SAFFIRE-II
│   │   ├── PSI-25/                # BASS-II (Burning and Suppression of Solids)
│   │   ├── PSI-26/                # BASS
│   │   ├── PSI-107/               # SPICE (Smoke Point In Co-flow Experiment)
│   │   ├── PSI-102/               # SAME (Smoke Aerosol Measurement Experiment)
│   │   ├── PSI-159/               # ACME CFI-G (Cool Flames Investigation with Gases)
│   │   ├── PSI-20/                # ACME BRE (Burning Rate Emulator)
│   │   └── pk4/                   # Campaign documentation PDFs & extracted text
│   ├── processed/                 # Standardized & cleaned datasets for application
│   └── combustion/                # Sample structured telemetry & sensor logs
│       ├── PSI-69_Experimental table_FLEX.csv
│       ├── PSI-68_Experimental table_Flex2.csv
│       ├── PSI-98_Experimental table_SAFFIRE-1.csv
│       ├── PSI-99_Experimental table_SAFFIRE-2.csv
│       ├── PSI-25_Experimental table_BASS-II.csv
│       ├── PSI-26_Experimental table_BASS.csv
│       ├── PSI-107_Experimental table_Spice.csv
│       ├── PSI-102_Experimental table_SAME.csv
│       ├── PSI-159_Experimental table_CFI-G_Normal Flames.csv
│       ├── PSI-159_Experimental table_CFI-G_Inverse Flames.csv
│       ├── PSI-20_Experimental table_ACME BRE.csv
│       ├── summary_report.md      # Formatted schema & unit report
│       └── summary_report.json    # Machine-readable telemetry report
├── docs/
│   ├── core_investigations.csv    # 15 core investigations with DOI, URLs, file types
│   └── core_investigations.md     # Markdown table of core investigations
├── src/
│   ├── ingest/
│   │   ├── s3_inventory.py        # S3 bucket inventory scanner (boto3 unsigned)
│   │   └── ingest_psi.py          # Provenance-tracked ingestion engine
│   ├── extract/
│   │   └── generate_investigation_catalog.py
│   └── api/                       # API integration connectors
└── app/                           # Fire-safety web application frontend/backend
```

---

## 🚀 Quick Start Guide

### 1. Requirements & Installation

Python 3.10+ is recommended with the following dependencies:

```bash
pip install boto3 pypdf openpyxl pandas
```

*Note: S3 bucket access uses anonymous/unsigned requests — **no AWS credentials or API keys are required**.*

---

## 🛰️ Step 0: S3 Exploration & Inventory (`s3_inventory.py`)

Scans public S3 prefixes of `s3://nasa-psi/` (region `us-west-2`) using anonymous requests, recording all files, byte sizes, and extensions into `inventory.csv`.

### How to Run

```bash
# Scan all discovered top-level prefixes with default settings:
python src/ingest/s3_inventory.py

# Scan a specific prefix (e.g., DSI/ or OASIS/):
python src/ingest/s3_inventory.py --prefix DSI/

# Scan multiple prefixes with a max-keys limit per prefix:
python src/ingest/s3_inventory.py --prefix DSI/ --prefix OASIS/ --prefix pk4/ --max-keys 100

# Specify custom output path:
python src/ingest/s3_inventory.py --output data/raw/custom_inventory.csv
```

### Command Line Arguments

| Argument | Description | Default |
|---|---|---|
| `--prefix` | S3 prefix to scan (can be specified multiple times). | Discovers all top-level prefixes (`DSI/`, `OASIS/`, `pk4/`) |
| `--max-keys` | Maximum objects to list per prefix (useful for rate-limiting). | `None` (all keys) |
| `--output` | Destination path for the inventory CSV file. | `inventory.csv` |

### Safeguards

- **50 MB Download Protection:** Any files larger than 50 MB are flagged in the logs to prevent excessive bandwidth consumption.
- **Unsigned Requests:** Uses `botocore.UNSIGNED` signature version to connect to public buckets without requiring AWS credentials.

---

## 🔬 Core Combustion & Fire Safety Investigations

A selection of 15 core microgravity combustion and spacecraft fire safety investigations cataloged from NASA PSI:

| Investigation ID | Acronym | Title | Sub-Research Area | DOI | File Types |
|---|---|---|---|---|---|
| **PSI-69** | FLEX | Flame Extinguishment Experiment | Spacecraft Fire Safety | [10.60555/mbq8-0451](https://doi.org/10.60555/mbq8-0451) | CSV |
| **PSI-68** | FLEX-2 | Flame Extinguishment Experiment - 2 | Spacecraft Fire Safety | [10.60555/byp8-h018](https://doi.org/10.60555/byp8-h018) | CSV |
| **PSI-98** | SAFFIRE-I | Spacecraft Fire Safety Experiment-I | Spacecraft Fire, Smoke Distribution | [10.60555/0t15-1z43](https://doi.org/10.60555/0t15-1z43) | CSV |
| **PSI-99** | SAFFIRE-II | Spacecraft Fire Experiment-II | Surface Combustion | [10.60555/2chp-m469](https://doi.org/10.60555/2chp-m469) | CSV |
| **PSI-100** | SAFFIRE-III | Spacecraft Fire Experiment-III | Spacecraft Fire Safety | [10.60555/040q-4h36](https://doi.org/10.60555/040q-4h36) | CSV |
| **PSI-25** | BASS-II | Burning and Suppression of Solids - II | Spacecraft Fire Safety | [10.60555/4qc4-de67](https://doi.org/10.60555/4qc4-de67) | CSV |
| **PSI-26** | BASS | Burning and Suppression of Solids | Spacecraft Fire Safety | [10.60555/58h4-dy80](https://doi.org/10.60555/58h4-dy80) | CSV |
| **PSI-60** | SPICE-Analysis | Computational and Experimental Analysis of SPICE Data Sets | Gaseous Combustion | [10.60555/mzjm-yv57](https://doi.org/10.60555/mzjm-yv57) | CSV, PDF, TXT |
| **PSI-107** | SPICE | Smoke Point In Co-flow Experiment | Fire Safety | [10.60555/9kbh-e962](https://doi.org/10.60555/9kbh-e962) | CSV |
| **PSI-101** | SAME-R | Smoke Aerosol Measurement Experiment-Reflight | Spacecraft Fire Safety | [10.60555/2np7-jv14](https://doi.org/10.60555/2np7-jv14) | CSV |
| **PSI-102** | SAME | Smoke and Aerosol Measurement Experiment | Spacecraft Fire Safety | [10.60555/gd4k-8h62](https://doi.org/10.60555/gd4k-8h62) | CSV |
| **PSI-115** | SAME-Sim | Advanced Modeling & Simulation of Smoke Generation | Smoke Aerosol Simulation | [10.60555/q0v5-1v28](https://doi.org/10.60555/q0v5-1v28) | CSV, PDF, TXT |
| **PSI-159** | ACME CFI-G | Cool Flames Investigation with Gases | Flames of Gaseous Fuels | [10.60555/cyt1-kh64](https://doi.org/10.60555/cyt1-kh64) | CSV |
| **PSI-10** | ACME Flame Design | ACME / Flame Design | Flames of Gaseous Fuels | [10.60555/w4zy-bt45](https://doi.org/10.60555/w4zy-bt45) | CSV |
| **PSI-20** | ACME BRE | ACME - Burning Rate Emulator | Flames of Gaseous Fuels | [10.60555/vb93-3y72](https://doi.org/10.60555/vb93-3y72) | CSV |

---

## 🔥 Combustion Telemetry Fetcher (`fetch_combustion_data.py`)

Targeted connector designed specifically for combustion and fire-safety experiments.

### How to Run

```bash
python fetch_combustion_data.py
```

### What It Does

1. **Scans Target Investigations:** Queries the NASA PSI repository for FLEX, Saffire, ACME, BASS, SPICE, and SAME.
2. **Filters Lightweight Data (< 25 MB):** Downloads structured tabular sensor logs (`.csv`, `.xlsx`, `.json`) while safely skipping heavy raw high-speed video recordings (`.mp4`, `.avi`, `.mpg`, `.bmp` frame sequences).
3. **Stores Datasets in `./data/combustion/`:**
   - `PSI-69_Experimental table_FLEX.csv` (274 rows, 15 columns)
   - `PSI-68_Experimental table_Flex2.csv` (8 rows, 7 columns)
   - `PSI-98_Experimental table_SAFFIRE-1.csv` (4 rows, 13 columns)
   - `PSI-99_Experimental table_SAFFIRE-2.csv` (15 rows, 17 columns)
   - `PSI-25_Experimental table_BASS-II.csv` (129 rows, 17 columns)
   - `PSI-26_Experimental table_BASS.csv` (122 rows, 6 columns)
   - `PSI-107_Experimental table_Spice.csv` (469 rows, 9 columns)
   - `PSI-102_Experimental table_SAME.csv` (8 rows, 5 columns)
   - `PSI-159_Experimental table_CFI-G_Normal Flames.csv` (179 rows, 18 columns)
   - `PSI-159_Experimental table_CFI-G_Inverse Flames.csv` (1015 rows, 20 columns)
   - `PSI-20_Experimental table_ACME BRE.csv` (18 rows, 8 columns)
4. **Auto-Generates Telemetry Summary Reports:**
   - `data/combustion/summary_report.md`: Markdown summary detailing every column, physical unit (e.g., `mmHg`, `mole fraction`, `mm`, `s`, `cm/s`, `K`, `bar`, `mg/s`), row count, and sample values.
   - `data/combustion/summary_report.json`: JSON report for direct ingestion into the FlameScope web UI.

---

## 📦 Step 1: Raw Data Ingestion with Provenance (`src/ingest/ingest_psi.py`)

Ingests raw investigations and S3 prefixes with full cryptographic provenance.

### How to Run

```bash
# Ingest default suite of core investigations and S3 campaign documentation:
python src/ingest/ingest_psi.py

# Ingest specific PSI investigations:
python src/ingest/ingest_psi.py --investigations PSI-69 PSI-98 PSI-25

# Ingest specific S3 prefixes:
python src/ingest/ingest_psi.py --s3-prefixes pk4/To_NASA_team/Campaign_Reports/
```

### Key Engineering Features

- **Provenance Tracking:** Every downloaded item is registered in `data/raw/<PSI-ID>/manifest.json` with:
  ```json
  {
    "source_url": "https://psi-repo-prod.s3.amazonaws.com/...",
    "retrieved_at": "2026-11-14T09:17:04.945600+00:00",
    "size_bytes": 24776,
    "sha256": "37c88ce8ae9391b7544ff630a45ce87543d04d317cdbfbed104fe7d5c27e1b96",
    "category": "experimental_table"
  }
  ```
- **Idempotency:** Re-running the script detects existing files matching file size and checksum, preventing redundant downloads.
- **Resilient Retries:** Employs exponential backoff retry on network timeouts or transient errors.
- **Failure Logging:** Unresolved issues are logged to `ingest_failures.log` with timestamps and URLs.
- **PDF Text Extraction with Page Numbers:** For documentation PDFs, plain text is extracted to `<name>_extracted.txt` alongside the PDF with `--- Page <N> ---` delimiters, allowing downstream modules to cite exact page references.

---

## 📄 License

Apache License 2.0. Open-access NASA microgravity research data.
