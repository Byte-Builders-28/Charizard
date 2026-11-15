"""
seed_data.py — Generate mock_investigations.json for offline frontend development.

Reads all raw investigation metadata and combustion CSVs, then writes
src/api/mock_investigations.json so the frontend can be developed without
the FastAPI server running.

Usage:
    python src/api/seed_data.py
"""

from __future__ import annotations

import glob
import json
import pathlib
import re
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Paths (resolve relative to this script's location → project root)
# ---------------------------------------------------------------------------
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent.parent  # Charizard/
RAW_DIR = BASE_DIR / "data" / "raw"
COMBUSTION_DIR = BASE_DIR / "data" / "combustion"
OUT_FILE = SCRIPT_DIR / "mock_investigations.json"


# ---------------------------------------------------------------------------
# Shared helpers (duplicated here so seed_data.py is standalone)
# ---------------------------------------------------------------------------

def _derive_fuel_state(sub_research_area: str, title: str = "") -> str:
    s = sub_research_area.lower()
    t = title.lower()
    if "droplet" in s or "droplet" in t:
        return "liquid"
    if "solid" in s or "surface combustion" in s or "solid" in t or "bass" in t:
        return "solid"
    return "gas"


def _derive_safety_category(sub_research_area: str) -> List[str]:
    s = sub_research_area.lower()
    if "fire" in s:
        return ["detection", "suppression"]
    if "safety" in s:
        return ["prevention", "detection"]
    return ["prevention"]


def _extract_first_number(val: Any) -> Optional[float]:
    if val is None:
        return None
    text = str(val)
    match = re.search(r"[-+]?\d*\.?\d+", text)
    if match:
        return float(match.group())
    return None


def _safe_numeric(series: pd.Series) -> Optional[tuple]:
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        return None
    return float(cleaned.min()), float(cleaned.max())


def _parse_csv_telemetry(csv_path: pathlib.Path) -> Dict[str, Any]:
    try:
        df = pd.read_csv(csv_path, encoding="latin-1")
    except Exception as e:
        return {"row_count": 0, "columns": [], "error": str(e)}

    result: Dict[str, Any] = {
        "row_count": len(df),
        "columns": list(df.columns),
        "file": csv_path.name,
    }
    cols = {c.strip().lower(): c for c in df.columns}

    ox_col = None
    ox_multiplier = 1.0
    for candidate in [
        "o initial ambient composition; mole fraction",
        "oxygen mole fraction",
        "xo2",
        " xo2 before test",
        "xo2  after test",
        "percent o2",
        "percent o2 (note 1)",
        "calibrated  initial o2 % by vol ",
        "oxygen conc (percent)",
    ]:
        if candidate in cols:
            ox_col = cols[candidate]
            if "mole fraction" in candidate or candidate.startswith("xo2") or candidate.strip().startswith("xo2"):
                ox_multiplier = 100.0
            break

    if ox_col:
        series = df[ox_col].apply(lambda v: _extract_first_number(v))
        series = pd.to_numeric(series, errors="coerce").dropna() * ox_multiplier
        if not series.empty:
            result["oxygen_percent_min"] = round(float(series.min()), 3)
            result["oxygen_percent_max"] = round(float(series.max()), 3)

    for candidate in ["ambient pressure; mmhg"]:
        if candidate in cols:
            pr = _safe_numeric(df[cols[candidate]])
            if pr:
                result["pressure_mmhg_min"] = round(pr[0], 3)
                result["pressure_mmhg_max"] = round(pr[1], 3)
            break

    for candidate in ["air flow (cm/s)", "airflow (cm/s)", "flow velocity (cm/s)"]:
        if candidate in cols:
            af = _safe_numeric(df[cols[candidate]])
            if af:
                result["airflow_min"] = round(af[0], 3)
                result["airflow_max"] = round(af[1], 3)
            break

    return result


def load_investigation(psi_dir: pathlib.Path) -> Optional[Dict[str, Any]]:
    psi_id = psi_dir.name
    meta_file = psi_dir / "investigation_metadata.json"
    if not meta_file.exists():
        print(f"  [skip] {psi_id}: no investigation_metadata.json")
        return None

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception:
        try:
            meta = json.loads(meta_file.read_text(encoding="latin-1"))
        except Exception as e:
            print(f"  [error] {psi_id}: could not parse JSON — {e}")
            return None

    sub_ra = meta.get("subResearchArea", "") or ""
    obj_text = meta.get("objective", "") or ""
    desc_text = meta.get("description", "") or ""

    inv: Dict[str, Any] = {
        "investigation_id": psi_id,
        "title": meta.get("title", ""),
        "acronym": meta.get("investigationAcronym", ""),
        "doi": meta.get("doi", ""),
        "source_url": f"https://psi.nasa.gov/investigations/{psi_id}",
        "research_area": meta.get("researchArea", ""),
        "sub_research_area": sub_ra,
        "hardware": meta.get("experimentHardware", ""),
        "flight_program": meta.get("flightProgram", ""),
        "objective": obj_text[:400],
        "description": desc_text[:500],
        "fuel_state": _derive_fuel_state(sub_ra, meta.get("title", "")),
        "gravity_condition": "microgravity",
        "safety_category": _derive_safety_category(sub_ra),
        "has_telemetry": False,
        "telemetry_row_count": 0,
        "telemetry_files": [],
        "oxygen_percent_min": None,
        "oxygen_percent_max": None,
        "pressure_mmhg_min": None,
        "pressure_mmhg_max": None,
        "airflow_min": None,
        "airflow_max": None,
    }

    csv_pattern = str(COMBUSTION_DIR / f"{psi_id}_*.csv")
    csv_files = glob.glob(csv_pattern)
    if csv_files:
        inv["has_telemetry"] = True
        inv["telemetry_files"] = [pathlib.Path(f).name for f in sorted(csv_files)]
        total_rows = 0
        for csv_path in csv_files:
            telem = _parse_csv_telemetry(pathlib.Path(csv_path))
            total_rows += telem.get("row_count", 0)
            for field in ("oxygen_percent_min", "pressure_mmhg_min", "airflow_min"):
                v = telem.get(field)
                if v is not None:
                    cur = inv[field]
                    inv[field] = v if cur is None else min(cur, v)
            for field in ("oxygen_percent_max", "pressure_mmhg_max", "airflow_max"):
                v = telem.get(field)
                if v is not None:
                    cur = inv[field]
                    inv[field] = v if cur is None else max(cur, v)
        inv["telemetry_row_count"] = total_rows
    else:
        print(f"  [info] {psi_id}: no CSV telemetry (gracefully handled)")

    return inv


def main() -> None:
    print(f"FlameScope seed_data.py")
    print(f"  RAW_DIR:        {RAW_DIR}")
    print(f"  COMBUSTION_DIR: {COMBUSTION_DIR}")
    print(f"  OUT_FILE:       {OUT_FILE}")
    print()

    psi_dirs = sorted(RAW_DIR.glob("PSI-*"))
    investigations = []
    issues = []

    for psi_dir in psi_dirs:
        print(f"Processing {psi_dir.name}...")
        inv = load_investigation(psi_dir)
        if inv:
            investigations.append(inv)
            print(
                f"  OK: {inv['title'][:50]!r} | fuel={inv['fuel_state']}"
                f" | sc={inv['safety_category']}"
                f" | telem={inv['has_telemetry']} ({inv['telemetry_row_count']} rows)"
                f" | O2=[{inv['oxygen_percent_min']},{inv['oxygen_percent_max']}]"
            )
        else:
            issues.append(psi_dir.name)

    print()
    print(f"Loaded {len(investigations)} investigations, {len(issues)} skipped: {issues}")

    # Write output
    output = {
        "_meta": {
            "generated_by": "seed_data.py",
            "source": "data/raw/ + data/combustion/",
            "count": len(investigations),
            "note": "Mock data for offline frontend development. Matches /api/investigations response shape.",
        },
        "investigations": investigations,
    }

    OUT_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written: {OUT_FILE}")
    print(f"File size: {OUT_FILE.stat().st_size:,} bytes")

    # Print summary table
    print()
    print(f"{'ID':<10} {'Title':<45} {'Fuel':<8} {'Safety':<30} {'Telemetry':<10} {'O2 min':<10} {'AF min':<10}")
    print("-" * 130)
    for inv in investigations:
        print(
            f"{inv['investigation_id']:<10} "
            f"{inv['title'][:44]:<45} "
            f"{inv['fuel_state']:<8} "
            f"{str(inv['safety_category']):<30} "
            f"{'Yes' if inv['has_telemetry'] else 'No':<10} "
            f"{str(inv.get('oxygen_percent_min', '-')):<10} "
            f"{str(inv.get('airflow_min', '-')):<10}"
        )


if __name__ == "__main__":
    main()
