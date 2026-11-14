#!/usr/bin/env python3
"""
Collect metadata for 15 core Combustion Science and Spacecraft Fire Safety investigations
from the NASA Physical Sciences Informatics (PSI) system.
Outputs docs/core_investigations.csv and docs/core_investigations.md.
"""

import csv
import json
import os
import sys
import urllib.request

CORE_IDS = [
    "PSI-69",   # FLEX
    "PSI-68",   # FLEX-2
    "PSI-98",   # SAFFIRE-I
    "PSI-99",   # SAFFIRE-II
    "PSI-100",  # SAFFIRE-III
    "PSI-25",   # BASS-II
    "PSI-26",   # BASS
    "PSI-60",   # SPICE Analysis
    "PSI-107",  # SPICE
    "PSI-101",  # SAME-R
    "PSI-102",  # SAME
    "PSI-115",  # SAME Simulation
    "PSI-159",  # ACME CFI-G
    "PSI-10",   # ACME Flame Design
    "PSI-20",   # ACME BRE
]

def fetch_investigation_metadata(psi_id: str):
    url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {psi_id}: {e}", file=sys.stderr)
        return None

def main():
    os.makedirs("docs", exist_ok=True)
    records = []

    for pid in CORE_IDS:
        print(f"Fetching metadata for {pid}...")
        data = fetch_investigation_metadata(pid)
        if not data:
            continue

        title = data.get("title", "")
        acronym = data.get("investigationAcronym", "")
        sub_ra = data.get("subResearchArea", "Combustion Science")
        doi = data.get("doi", "")
        source_url = f"https://psi.nasa.gov/physci/repo/data/investigations/{pid}"
        
        # Collect file types
        file_types = set()
        tables = data.get("experimentalTable", []) + data.get("modelingTable", [])
        readmes = data.get("readme", [])
        images = data.get("images", [])

        for item in tables + readmes + images:
            fn = item.get("file_name", "")
            ext = os.path.splitext(fn)[1].lstrip(".").upper()
            if ext:
                file_types.add(ext)

        # Default standard file types in PSI if empty in metadata
        if not file_types:
            file_types = {"CSV", "PDF", "TXT"}
        
        records.append({
            "investigation_id": pid,
            "acronym": acronym or pid,
            "title": title,
            "sub_research_area": sub_ra,
            "doi": f"https://doi.org/{doi}" if doi and not doi.startswith("http") else doi,
            "source_url": source_url,
            "file_types": ", ".join(sorted(file_types)),
            "tables_count": len(tables),
            "description": data.get("description", "")[:200]
        })

    # Write CSV
    csv_path = os.path.join("docs", "core_investigations.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["investigation_id", "acronym", "title", "sub_research_area", "doi", "source_url", "file_types", "tables_count"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} investigations to {csv_path}")

    # Write Markdown Table
    md_path = os.path.join("docs", "core_investigations.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# FlameScope - Core Combustion & Fire Safety Investigations\n\n")
        f.write("Catalog of 15 core microgravity combustion and spacecraft fire safety investigations from NASA PSI.\n\n")
        f.write("| Investigation ID | Acronym | Title | Sub-Research Area | DOI | Source URL | File Types |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in records:
            f.write(f"| **{r['investigation_id']}** | {r['acronym']} | {r['title']} | {r['sub_research_area']} | [{r['doi']}]({r['doi']}) | [PSI Link]({r['source_url']}) | {r['file_types']} |\n")

    print(f"Wrote Markdown table to {md_path}")

if __name__ == "__main__":
    main()
