#!/usr/bin/env python3
"""
FlameScope - Combustion Science & Spacecraft Fire Safety Data Connector
Target: NASA Physical Sciences Informatics (PSI) & S3 repository

Specifically targets:
- FLEX / FLEX-2 (Flame Extinguishment Experiment: PSI-69, PSI-68)
- Saffire (Spacecraft Fire Safety Demonstration: PSI-98, PSI-99, PSI-100)
- ACME (Advanced Combustion via Microgravity Experiments: PSI-159, PSI-10, PSI-20)
- BASS / BASS-II (Burning and Suppression of Solids: PSI-25, PSI-26)
- SPICE (Smoke Point in Co-flow Experiment: PSI-60, PSI-107)
- SAME (Smoke Aerosol Measurement Experiment: PSI-102, PSI-101, PSI-115)

Filters:
- Tabular data, sensor logs, telemetry, descriptions (.csv, .txt, .json, .xlsx, .pdf < 25 MB)
- Skips heavy raw high-speed video files (.mp4, .avi, .mpg, .mov, .bmp sequences)

Output:
- Downloads files into ./data/combustion/
- Generates a summary report (columns, units, row counts) in ./data/combustion/summary_report.md
  and ./data/combustion/summary_report.json
"""

import argparse
import csv
import datetime
import io
import json
import logging
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("fetch_combustion")

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
DEST_DIR = os.path.join(".", "data", "combustion")

# Core target investigations for Combustion Science and Spacecraft Fire Safety
CORE_COMBUSTION_TARGETS = [
    {
        "id": "PSI-69",
        "name": "FLEX",
        "title": "Flame Extinguishment Experiment",
        "sub_area": "Spacecraft Fire Safety",
    },
    {
        "id": "PSI-68",
        "name": "FLEX-2",
        "title": "Flame Extinguishment Experiment - 2",
        "sub_area": "Spacecraft Fire Safety",
    },
    {
        "id": "PSI-98",
        "name": "SAFFIRE-I",
        "title": "Spacecraft Fire Safety Experiment-I",
        "sub_area": "Spacecraft Fire, Smoke Distribution",
    },
    {
        "id": "PSI-99",
        "name": "SAFFIRE-II",
        "title": "Spacecraft Fire Experiment-II",
        "sub_area": "Surface Combustion",
    },
    {
        "id": "PSI-25",
        "name": "BASS-II",
        "title": "Burning and Suppression of Solids - II",
        "sub_area": "Spacecraft Fire Safety",
    },
    {
        "id": "PSI-26",
        "name": "BASS",
        "title": "Burning and Suppression of Solids",
        "sub_area": "Spacecraft Fire Safety",
    },
    {
        "id": "PSI-107",
        "name": "SPICE",
        "title": "Smoke Point In Co-flow Experiment",
        "sub_area": "Fire Safety",
    },
    {
        "id": "PSI-60",
        "name": "SPICE-Analysis",
        "title": "Computational and Experimental Analysis of SPICE Data Sets",
        "sub_area": "Gaseous Combustion",
    },
    {
        "id": "PSI-102",
        "name": "SAME",
        "title": "Smoke and Aerosol Measurement Experiment",
        "sub_area": "Spacecraft Fire Safety",
    },
    {
        "id": "PSI-159",
        "name": "ACME CFI-G",
        "title": "ACME - Cool Flames Investigation with Gases",
        "sub_area": "Flames of Gaseous Fuels",
    },
    {
        "id": "PSI-20",
        "name": "ACME BRE",
        "title": "ACME - Burning Rate Emulator",
        "sub_area": "Flames of Gaseous Fuels",
    },
]


def extract_unit_from_header(header_text: str) -> Tuple[str, str]:
    """
    Extracts the clean column name and the physical unit from header text.
    Handles NASA PSI conventions such as:
    - 'Ambient pressure; mmHg' -> ('Ambient pressure', 'mmHg')
    - 'Sample Thickness (cm)' -> ('Sample Thickness', 'cm')
    - 'Burning rate [mm/s]' -> ('Burning rate', 'mm/s')
    - 'Percent O2' -> ('Percent O2', '%')
    - 'Temperature / K' -> ('Temperature', 'K')
    """
    header = header_text.strip()

    # Match semicolon notation (very common in FLEX / BASS tables)
    if ";" in header:
        parts = header.split(";", 1)
        return parts[0].strip(), parts[1].strip()

    # Match bracket notation [unit]
    bracket_match = re.search(r"^(.*?)\s*\[(.*?)\]$", header)
    if bracket_match:
        return bracket_match.group(1).strip(), bracket_match.group(2).strip()

    # Match parenthesis notation (unit)
    paren_match = re.search(r"^(.*?)\s*\((.*?)\)$", header)
    if paren_match:
        candidate_unit = paren_match.group(2).strip()
        # Verify candidate unit looks like a unit or abbreviation
        if len(candidate_unit) <= 15 or candidate_unit.lower() in ["mole fraction", "vol%", "s", "k", "cm", "mm", "w", "cm/s"]:
            return paren_match.group(1).strip(), candidate_unit

    # Check for Percent or % in name
    if "percent" in header.lower() or "%" in header:
        return header, "%"

    return header, "dimensionless / unspecified"


def get_presigned_url(psi_id: str, filename: str, version: int = 1) -> str:
    """Gets signed S3 download URL from NASA PSI studies download API."""
    params = {
        "file": filename,
        "version": str(version),
        "redirect": "false"
    }
    url = f"https://psi.nasa.gov/geode-py/ws/studies/{psi_id}/download?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 FlameScope/1.0"})
    with urllib.request.urlopen(req, timeout=25) as res:
        download_url = res.read().decode("utf-8").strip()
        return download_url


def fetch_investigation_tables(psi_id: str) -> List[Dict[str, Any]]:
    """Retrieves experimental and modeling tables for a given PSI investigation."""
    url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 FlameScope/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode("utf-8"))
            tables = data.get("experimentalTable", []) + data.get("modelingTable", [])
            return tables
    except Exception as e:
        logger.warning(f"Failed to fetch metadata for {psi_id}: {e}")
        return []


def download_file(url: str, dest_path: str, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> bool:
    """Downloads a remote file with size check."""
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        logger.info(f"File already exists locally: {dest_path}")
        return True

    temp_path = dest_path + ".tmp"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 FlameScope/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_length = resp.headers.get("Content-Length")
            if content_length and int(content_length) > max_size_bytes:
                logger.warning(f"File size {content_length} exceeds limit of {max_size_bytes}. Skipping.")
                return False

            downloaded = 0
            with open(temp_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    if downloaded > max_size_bytes:
                        logger.warning(f"Stream exceeded max size {max_size_bytes}. Aborting.")
                        f.close()
                        os.remove(temp_path)
                        return False
                    f.write(chunk)

            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(temp_path, dest_path)
            return True
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False


def analyze_file(filepath: str, meta_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Analyzes a downloaded tabular file, extracting schema, units, row counts, and sample values."""
    fname = os.path.basename(filepath)
    ext = os.path.splitext(fname)[1].lower()
    size_bytes = os.path.getsize(filepath)

    analysis = {
        "filename": fname,
        "investigation_id": meta_info.get("id", ""),
        "investigation_name": meta_info.get("name", ""),
        "sub_area": meta_info.get("sub_area", ""),
        "size_bytes": size_bytes,
        "extension": ext,
        "row_count": 0,
        "column_count": 0,
        "columns": [],
    }

    try:
        if ext == ".csv":
            # Attempt reading with pandas, auto-detecting encoding
            for encoding in ["utf-8", "latin1", "cp1252"]:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                logger.error(f"Could not decode {fname} with standard encodings.")
                return None

            analysis["row_count"] = len(df)
            analysis["column_count"] = len(df.columns)

            col_details = []
            for col in df.columns:
                clean_name, unit = extract_unit_from_header(str(col))
                # Non-null count & sample value
                non_null = int(df[col].notna().sum())
                sample_val = str(df[col].dropna().iloc[0]) if non_null > 0 else "N/A"
                if len(sample_val) > 40:
                    sample_val = sample_val[:37] + "..."

                col_details.append({
                    "raw_header": str(col),
                    "clean_name": clean_name,
                    "unit": unit,
                    "data_type": str(df[col].dtype),
                    "non_null_count": non_null,
                    "sample_value": sample_val
                })
            analysis["columns"] = col_details

        elif ext == ".xlsx":
            excel_file = pd.ExcelFile(filepath)
            sheet_name = excel_file.sheet_names[0]
            df = excel_file.parse(sheet_name)
            analysis["row_count"] = len(df)
            analysis["column_count"] = len(df.columns)
            analysis["sheet_name"] = sheet_name

            col_details = []
            for col in df.columns:
                clean_name, unit = extract_unit_from_header(str(col))
                col_details.append({
                    "raw_header": str(col),
                    "clean_name": clean_name,
                    "unit": unit,
                    "data_type": str(df[col].dtype),
                    "non_null_count": int(df[col].notna().sum()),
                })
            analysis["columns"] = col_details

        elif ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                d = json.load(f)
            analysis["row_count"] = len(d) if isinstance(d, list) else 1
            analysis["column_count"] = len(d.keys()) if isinstance(d, dict) else (len(d[0].keys()) if isinstance(d, list) and d and isinstance(d[0], dict) else 1)

        return analysis
    except Exception as e:
        logger.error(f"Error analyzing {fname}: {e}")
        return None


def generate_summary_report(analyses: List[Dict[str, Any]], out_dir: str):
    """Generates both Markdown and JSON summary reports for the downloaded telemetry."""
    md_path = os.path.join(out_dir, "summary_report.md")
    json_path = os.path.join(out_dir, "summary_report.json")

    # Save JSON report
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analyses, f, indent=2)

    # Generate Markdown Report
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# NASA Combustion Science & Spacecraft Fire Safety Telemetry Report\n\n")
        f.write(f"**Generated at:** {datetime.datetime.now(datetime.timezone.utc).isoformat()} UTC\n\n")
        f.write(f"**Dataset Location:** `{out_dir}`\n\n")
        f.write("This report summarizes structured sensor logs, flammability measurements, and microgravity combustion telemetry ")
        f.write("downloaded from the NASA Physical Sciences Informatics (PSI) repository for the FlameScope fire-safety application.\n\n")

        # Table of Files
        f.write("## 1. Downloaded Telemetry & Sensor Datasets Overview\n\n")
        f.write("| Investigation | Mission / Acronym | File Name | Rows | Columns | Size (KB) |\n")
        f.write("|---|---|---|---|---|---|\n")
        for a in analyses:
            f.write(f"| **{a['investigation_id']}** | {a['investigation_name']} | `{a['filename']}` | {a['row_count']} | {a['column_count']} | {a['size_bytes'] / 1024:.1f} KB |\n")

        f.write("\n## 2. Detailed Dataset Schemas & Unit Dictionaries\n\n")
        for a in analyses:
            f.write(f"### {a['investigation_id']}: {a['investigation_name']} — `{a['filename']}`\n\n")
            f.write(f"- **Sub-Research Area:** {a['sub_area']}\n")
            f.write(f"- **Total Rows:** {a['row_count']}\n")
            f.write(f"- **Total Columns:** {a['column_count']}\n")
            f.write(f"- **File Size:** {a['size_bytes']:,} bytes\n\n")

            if a.get("columns"):
                f.write("| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |\n")
                f.write("|---|---|---|---|---|\n")
                for c in a["columns"]:
                    sample = c.get("sample_value", "N/A")
                    f.write(f"| `{c['raw_header']}` | **{c['clean_name']}** | `{c['unit']}` | {c['data_type']} | {sample} |\n")
                f.write("\n")

    logger.info(f"Summary reports generated successfully:\n  - {md_path}\n  - {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch combustion science and spacecraft fire safety telemetry from NASA PSI"
    )
    parser.add_argument(
        "--dest-dir",
        default=DEST_DIR,
        help=f"Directory to store combustion data (default: {DEST_DIR})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of investigations to process",
    )
    args = parser.parse_args()

    os.makedirs(args.dest_dir, exist_ok=True)
    logger.info("=== NASA PSI Combustion Science & Spacecraft Fire Safety Data Connector ===")
    logger.info(f"Output directory: {os.path.abspath(args.dest_dir)}")

    targets = CORE_COMBUSTION_TARGETS[:args.limit] if args.limit else CORE_COMBUSTION_TARGETS
    logger.info(f"Targeting {len(targets)} combustion investigations: {[t['id'] for t in targets]}")

    downloaded_files = []

    for target in targets:
        psi_id = target["id"]
        logger.info(f"\n--- Processing {psi_id} [{target['name']}: {target['title']}] ---")
        tables = fetch_investigation_tables(psi_id)
        if not tables:
            logger.info(f"No experimental/modeling tables found directly for {psi_id}.")
            continue

        for table_meta in tables:
            fname = table_meta.get("file_name", "")
            fsize = table_meta.get("file_size", 0)
            version = table_meta.get("version", 1)

            if not fname:
                continue

            ext = os.path.splitext(fname)[1].lower()
            if ext not in [".csv", ".xlsx", ".txt", ".json", ".pdf"]:
                logger.info(f"Skipping non-tabular file: {fname}")
                continue

            if fsize > MAX_FILE_SIZE_BYTES:
                logger.info(f"Skipping {fname} ({fsize} bytes > {MAX_FILE_SIZE_BYTES} limit)")
                continue

            dest_path = os.path.join(args.dest_dir, fname)
            logger.info(f"Resolving download URL for {fname} ({fsize} bytes)...")
            try:
                download_url = get_presigned_url(psi_id, fname, version)
                if download_url:
                    success = download_file(download_url, dest_path)
                    if success:
                        downloaded_files.append((dest_path, target))
            except Exception as e:
                logger.error(f"Error fetching {fname}: {e}")

    logger.info(f"\nTotal files retrieved/verified: {len(downloaded_files)}")

    # Analyze files and generate summary report
    analyses = []
    print("\n" + "=" * 90)
    print(f"{'INVESTIGATION':<12} | {'ACRONYM':<12} | {'ROWS':<6} | {'COLS':<6} | {'FILE NAME':<35} | {'SAMPLE UNITS'}")
    print("=" * 90)

    for fpath, meta in downloaded_files:
        analysis = analyze_file(fpath, meta)
        if analysis:
            analyses.append(analysis)
            sample_units = [c['unit'] for c in analysis.get('columns', []) if c['unit'] != 'dimensionless / unspecified']
            units_summary = ", ".join(list(dict.fromkeys(sample_units))[:3]) or "None specified"
            print(f"{analysis['investigation_id']:<12} | {analysis['investigation_name']:<12} | {analysis['row_count']:<6} | {analysis['column_count']:<6} | {analysis['filename'][:35]:<35} | {units_summary}")

    print("=" * 90 + "\n")

    generate_summary_report(analyses, args.dest_dir)


if __name__ == "__main__":
    main()
