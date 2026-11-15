"""
FlameScope FastAPI Backend
NASA Microgravity Combustion Science Data Platform
"""

from __future__ import annotations

import glob
import io
import json
import pathlib
import re
from typing import Any, Dict, List, Optional

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent  # Charizard/
RAW_DIR = BASE_DIR / "data" / "raw"
COMBUSTION_DIR = BASE_DIR / "data" / "combustion"

# ---------------------------------------------------------------------------
# Data-loading helpers
# ---------------------------------------------------------------------------

def _derive_fuel_state(sub_research_area: str, title: str = "", acronym: str = "", hardware: str = "") -> str:
    s = (sub_research_area + " " + title + " " + acronym + " " + hardware).lower()
    if "droplet" in s or "flex" in s or "liquid" in s:
        return "liquid"
    if "solid" in s or "surface combustion" in s or "bass" in s or "saffire" in s:
        return "solid"
    return "gas"


def _derive_safety_category(sub_research_area: str) -> List[str]:
    s = sub_research_area.lower()
    if "fire" in s:
        return ["detection", "suppression"]
    if "safety" in s:
        return ["prevention", "detection"]
    return ["prevention"]


def _safe_numeric(series: pd.Series) -> Optional[tuple]:
    """Return (min, max) of a column after coercing to numeric; None if no data."""
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        return None
    return float(cleaned.min()), float(cleaned.max())


def _extract_first_number(val: Any) -> Optional[float]:
    """Extract the first floating-point number from a cell that may be a range string."""
    if val is None:
        return None
    text = str(val)
    match = re.search(r"[-+]?\d*\.?\d+", text)
    if match:
        return float(match.group())
    return None


def _parse_csv_telemetry(csv_path: pathlib.Path) -> Dict[str, Any]:
    """Parse a combustion CSV and extract telemetry stats."""
    try:
        df = pd.read_csv(csv_path, encoding="latin-1")
    except Exception:
        return {"row_count": 0, "columns": []}

    result: Dict[str, Any] = {
        "row_count": len(df),
        "columns": list(df.columns),
        "file": csv_path.name,
    }
    cols = {c.strip().lower(): c for c in df.columns}

    # --- Oxygen ---
    ox_col = None
    ox_multiplier = 1.0
    # Priority order
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
            # mole fraction columns → multiply by 100
            if "mole fraction" in candidate or candidate.startswith("xo2") or candidate.strip().startswith("xo2"):
                ox_multiplier = 100.0
            break

    if ox_col:
        series = df[ox_col].apply(lambda v: _extract_first_number(v))
        series = pd.to_numeric(series, errors="coerce").dropna() * ox_multiplier
        series = series[(series >= 0) & (series <= 100)]
        if not series.empty:
            result["oxygen_percent_min"] = round(float(series.min()), 3)
            result["oxygen_percent_max"] = round(float(series.max()), 3)

    # --- Pressure mmHg ---
    for candidate in ["ambient pressure; mmhg"]:
        if candidate in cols:
            pr = _safe_numeric(df[cols[candidate]])
            if pr:
                result["pressure_mmhg_min"] = round(pr[0], 3)
                result["pressure_mmhg_max"] = round(pr[1], 3)
            break

    # --- Airflow ---
    for candidate in ["air flow (cm/s)", "airflow (cm/s)", "flow velocity (cm/s)"]:
        if candidate in cols:
            af = _safe_numeric(df[cols[candidate]])
            if af:
                result["airflow_min"] = round(af[0], 3)
                result["airflow_max"] = round(af[1], 3)
            break

    return result


def _load_investigation(psi_dir: pathlib.Path) -> Optional[Dict[str, Any]]:
    psi_id = psi_dir.name
    meta_file = psi_dir / "investigation_metadata.json"
    if not meta_file.exists():
        return None

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception:
        try:
            meta = json.loads(meta_file.read_text(encoding="latin-1"))
        except Exception:
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
        "fuel_state": _derive_fuel_state(
            sub_ra,
            meta.get("title", ""),
            meta.get("investigationAcronym", ""),
            str(meta.get("experimentHardware", "")),
        ),
        "gravity_condition": "microgravity",
        "safety_category": _derive_safety_category(sub_ra),
        # telemetry fields populated later
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

    # --- Match CSV files ---
    csv_pattern = str(COMBUSTION_DIR / f"{psi_id}_*.csv")
    csv_files = glob.glob(csv_pattern)
    if csv_files:
        inv["has_telemetry"] = True
        inv["telemetry_files"] = [pathlib.Path(f).name for f in csv_files]
        # Merge stats across all CSV files for this investigation
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

    return inv


# ---------------------------------------------------------------------------
# Startup: load all investigations into memory
# ---------------------------------------------------------------------------

_investigations: List[Dict[str, Any]] = []
_investigations_index: Dict[str, Dict[str, Any]] = {}  # keyed by investigation_id


def _load_all_data() -> None:
    global _investigations, _investigations_index
    _investigations = []
    _investigations_index = {}

    psi_dirs = sorted(RAW_DIR.glob("PSI-*"))
    for psi_dir in psi_dirs:
        inv = _load_investigation(psi_dir)
        if inv:
            _investigations.append(inv)
            _investigations_index[inv["investigation_id"]] = inv

    print(f"[FlameScope] Loaded {len(_investigations)} investigations")
    for inv in _investigations:
        print(
            f"  {inv['investigation_id']}: telemetry={inv['has_telemetry']}"
            f" O2=[{inv['oxygen_percent_min']},{inv['oxygen_percent_max']}]"
            f" AF=[{inv['airflow_min']},{inv['airflow_max']}]"
        )


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FlameScope API",
    description="NASA Microgravity Combustion Science Data Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load data immediately at module load time so it is ready for tests & requests
_load_all_data()

@app.on_event("startup")
def startup_event():
    if not _investigations:
        _load_all_data()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str
    investigation_ids: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "investigation_count": len(_investigations)}


@app.get("/api/investigations")
def list_investigations(
    q: Optional[str] = None,
    safety_category: Optional[str] = None,
    fuel_state: Optional[str] = None,
    gravity_condition: Optional[str] = None,
):
    results = list(_investigations)

    if q:
        q_lower = q.lower()
        results = [
            inv for inv in results
            if q_lower in (inv.get("title", "") or "").lower()
            or q_lower in (inv.get("objective", "") or "").lower()
            or q_lower in (inv.get("description", "") or "").lower()
            or q_lower in (inv.get("acronym", "") or "").lower()
            or q_lower in (inv.get("sub_research_area", "") or "").lower()
        ]

    if safety_category:
        sc = safety_category.lower()
        results = [inv for inv in results if sc in inv.get("safety_category", [])]

    if fuel_state:
        fs = fuel_state.lower()
        results = [inv for inv in results if inv.get("fuel_state") == fs]

    if gravity_condition:
        gc = gravity_condition.lower()
        results = [inv for inv in results if inv.get("gravity_condition") == gc]

    return {"count": len(results), "investigations": results}


@app.get("/api/investigations/{investigation_id}")
def get_investigation(investigation_id: str):
    inv = _investigations_index.get(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail=f"Investigation {investigation_id!r} not found")
    return inv


@app.get("/api/compare")
def compare_investigations(
    ids: str = Query(..., description="Comma-separated list of 2-3 PSI IDs, e.g. PSI-69,PSI-98,PSI-25"),
):
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    if len(id_list) < 2 or len(id_list) > 3:
        raise HTTPException(status_code=400, detail="Provide 2-3 investigation IDs to compare")

    found = []
    missing = []
    for pid in id_list:
        inv = _investigations_index.get(pid)
        if inv:
            found.append(inv)
        else:
            missing.append(pid)

    if missing:
        raise HTTPException(status_code=404, detail=f"Not found: {', '.join(missing)}")

    # Build comparison matrix
    fields = [
        "investigation_id", "title", "acronym", "doi", "research_area",
        "sub_research_area", "hardware", "flight_program", "fuel_state",
        "gravity_condition", "safety_category", "has_telemetry",
        "telemetry_row_count", "oxygen_percent_min", "oxygen_percent_max",
        "pressure_mmhg_min", "pressure_mmhg_max", "airflow_min", "airflow_max",
        "objective",
    ]

    comparison = {
        "investigations": found,
        "matrix": {
            field: {inv["investigation_id"]: inv.get(field) for inv in found}
            for field in fields
        },
        "summary": {
            "all_microgravity": all(inv["gravity_condition"] == "microgravity" for inv in found),
            "shared_safety_categories": list(
                set.intersection(*[set(inv["safety_category"]) for inv in found])
            ),
            "telemetry_overlap": all(inv["has_telemetry"] for inv in found),
        },
    }
    return comparison


def _score_investigation(inv: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    score = 0
    reasons = []

    sc = set(inv.get("safety_category", []))
    has_telem = inv.get("has_telemetry", False)
    has_doi = bool(inv.get("doi", ""))
    ox_min = inv.get("oxygen_percent_min")
    pres_min = inv.get("pressure_mmhg_min")
    airflow = inv.get("airflow_min") is not None

    if scenario == "iss":
        if inv.get("gravity_condition") == "microgravity":
            score += 40; reasons.append("microgravity platform (ISS)")
        if "detection" in sc:
            score += 20; reasons.append("fire detection capability")
        if "suppression" in sc:
            score += 20; reasons.append("suppression research")
        if has_telem:
            score += 10; reasons.append("experimental telemetry available")
        if has_doi:
            score += 10; reasons.append("peer-reviewed publication (DOI)")

    elif scenario == "moon_base":
        desc_obj = (inv.get("objective", "") + " " + inv.get("description", "")).lower()
        if "partial" in desc_obj or "lunar" in desc_obj or "moon" in desc_obj or "low gravity" in desc_obj:
            score += 30; reasons.append("partial/low gravity referenced")
        if "prevention" in sc:
            score += 20; reasons.append("fire prevention research")
        if "detection" in sc:
            score += 15; reasons.append("fire detection research")
        if airflow:
            score += 15; reasons.append("airflow data available (ventilation modeling)")
        if has_telem:
            score += 10; reasons.append("experimental telemetry available")
        if has_doi:
            score += 10; reasons.append("peer-reviewed publication (DOI)")

    elif scenario == "mars":
        # Mars: ~0.095% O2, ~0.6 kPa (~4.5 mmHg)
        if ox_min is not None and ox_min < 15:
            score += 30; reasons.append(f"low-O2 experiments (min {ox_min:.1f}% ≈ Mars-like)")
        if pres_min is not None and pres_min < 100:
            score += 20; reasons.append(f"low-pressure experiments (min {pres_min:.0f} mmHg)")
        if "prevention" in sc:
            score += 20; reasons.append("fire prevention (critical for Mars habitats)")
        if has_telem:
            score += 10; reasons.append("experimental telemetry available")
        if has_doi:
            score += 10; reasons.append("peer-reviewed publication (DOI)")

    elif scenario == "rover":
        if "suppression" in sc:
            score += 30; reasons.append("fire suppression research (rover safety)")
        if inv.get("fuel_state") == "solid":
            score += 20; reasons.append("solid fuel combustion (rover materials)")
        if "detection" in sc:
            score += 20; reasons.append("fire detection research")
        # "small sample" heuristic: solid-fuel investigations with limited test rows
        if inv.get("telemetry_row_count", 0) < 20 and has_telem:
            score += 15; reasons.append("small-sample test regime")
        if has_telem:
            score += 10; reasons.append("experimental telemetry available")
        if has_doi:
            score += 5; reasons.append("peer-reviewed publication (DOI)")

    return {
        "investigation_id": inv["investigation_id"],
        "title": inv.get("title", ""),
        "score": min(score, 100),
        "reasons": reasons,
    }


@app.get("/api/rank")
def rank_investigations(
    scenario: str = Query(..., description="One of: iss, moon_base, mars, rover"),
):
    valid = {"iss", "moon_base", "mars", "rover"}
    if scenario not in valid:
        raise HTTPException(status_code=400, detail=f"scenario must be one of {valid}")

    ranked = [_score_investigation(inv, scenario) for inv in _investigations]
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {"scenario": scenario, "rankings": ranked}


@app.get("/api/gaps")
def research_gaps():
    # Oxygen-airflow heatmap data
    heatmap = []
    for inv in _investigations:
        if inv.get("oxygen_percent_min") is not None and inv.get("airflow_min") is not None:
            heatmap.append({
                "investigation_id": inv["investigation_id"],
                "title": inv.get("title", ""),
                "oxygen_min": inv["oxygen_percent_min"],
                "oxygen_max": inv["oxygen_percent_max"],
                "airflow_min": inv["airflow_min"],
                "airflow_max": inv["airflow_max"],
            })

    # Partial gravity gap — count non-microgravity
    partial_gravity_gap = sum(
        1 for inv in _investigations if inv.get("gravity_condition") != "microgravity"
    )

    # Field coverage
    schema_fields = [
        "investigation_id", "title", "acronym", "doi", "source_url",
        "research_area", "sub_research_area", "hardware", "flight_program",
        "objective", "description", "fuel_state", "gravity_condition",
        "safety_category", "has_telemetry", "oxygen_percent_min",
        "pressure_mmhg_min", "airflow_min",
    ]
    field_coverage = {}
    for field in schema_fields:
        count = sum(
            1 for inv in _investigations
            if inv.get(field) is not None and inv.get(field) != "" and inv.get(field) != []
        )
        field_coverage[field] = {"filled": count, "total": len(_investigations)}

    # Scenario coverage (score > 0)
    scenario_coverage = {}
    for scenario in ("iss", "moon_base", "mars", "rover"):
        relevant = [
            inv for inv in _investigations
            if _score_investigation(inv, scenario)["score"] > 0
        ]
        scenario_coverage[scenario] = len(relevant)

    return {
        "oxygen_airflow_heatmap": heatmap,
        "partial_gravity_gap": {
            "count": partial_gravity_gap,
            "note": "0 non-microgravity investigations — this IS the gap. No partial-gravity combustion data exists.",
        },
        "field_coverage": field_coverage,
        "scenario_coverage": scenario_coverage,
        "summary": {
            "total_investigations": len(_investigations),
            "with_telemetry": sum(1 for inv in _investigations if inv["has_telemetry"]),
            "with_oxygen_data": sum(1 for inv in _investigations if inv.get("oxygen_percent_min") is not None),
            "with_airflow_data": sum(1 for inv in _investigations if inv.get("airflow_min") is not None),
            "with_pressure_data": sum(1 for inv in _investigations if inv.get("pressure_mmhg_min") is not None),
        },
    }


@app.post("/api/ask")
def ask(request: AskRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Determine which investigations to search
    if request.investigation_ids:
        pool = [
            _investigations_index[pid]
            for pid in request.investigation_ids
            if pid in _investigations_index
        ]
    else:
        pool = _investigations

    # Tokenize question
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "do", "does", "did",
                  "in", "of", "on", "at", "to", "for", "and", "or", "not", "what",
                  "how", "why", "when", "which", "who", "can", "has", "have", "been",
                  "be", "by", "with", "that", "this", "it", "about"}
    keywords = [w.lower() for w in re.findall(r"\w+", question) if w.lower() not in stop_words]

    # Score investigations
    scored = []
    for inv in pool:
        search_text = " ".join([
            inv.get("title", ""),
            inv.get("objective", ""),
            inv.get("description", ""),
            inv.get("sub_research_area", ""),
            inv.get("acronym", ""),
        ]).lower()
        hits = sum(1 for kw in keywords if kw in search_text)
        if hits > 0:
            # Find a relevant quote
            quote_source = ""
            quote_text = ""
            for field_name, field_key in [("objective field", "objective"), ("description field", "description"), ("title", "title")]:
                field_val = inv.get(field_key, "") or ""
                matching_kw = [kw for kw in keywords if kw in field_val.lower()]
                if matching_kw and field_val:
                    # Extract a ~120-char snippet around first keyword hit
                    idx = field_val.lower().find(matching_kw[0])
                    start = max(0, idx - 40)
                    end = min(len(field_val), idx + 80)
                    quote_text = ("..." if start > 0 else "") + field_val[start:end].strip() + ("..." if end < len(field_val) else "")
                    quote_source = field_name
                    break
            scored.append((hits, inv, quote_text, quote_source))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:5]

    if not top:
        return {
            "answer": f"No investigations found matching your query: '{question}'. Try searching for topics like 'droplet combustion', 'fire suppression', 'oxygen limits', or 'solid fuel'.",
            "citations": [],
            "matched_count": 0,
        }

    # Build a synthesized answer
    top_invs = [t[1] for t in top]
    names = [f"{inv.get('acronym') or inv['investigation_id']} ({inv['investigation_id']})" for inv in top_invs[:3]]
    names_str = ", ".join(names[:-1]) + (" and " + names[-1] if len(names) > 1 else names[0])

    # Build contextual answer paragraph
    kw_str = ", ".join(keywords[:5])
    answer_parts = [
        f"Based on {names_str}, here is what the FlameScope dataset reveals about '{question}':",
    ]
    for _, inv, quote, _ in top[:3]:
        snippet = inv.get("objective", inv.get("description", ""))[:200]
        if snippet:
            answer_parts.append(
                f"\n• **{inv.get('title', inv['investigation_id'])}** ({inv['investigation_id']}): {snippet.strip()}{'...' if len(snippet) >= 200 else ''}"
            )

    answer_parts.append(
        f"\n\nKeywords matched: {kw_str}. "
        f"{'Note: No LLM key configured — this is a keyword-based mock response. Connect a Gemini/OpenAI key for deeper synthesis.' if len(top) > 0 else ''}"
    )

    citations = [
        {
            "investigation_id": inv["investigation_id"],
            "title": inv.get("title", ""),
            "acronym": inv.get("acronym", ""),
            "quote": quote,
            "source": source,
            "url": inv.get("source_url", ""),
            "relevance_score": hits,
        }
        for hits, inv, quote, source in top
    ]

    return {
        "answer": "".join(answer_parts),
        "citations": citations,
        "matched_count": len(top),
        "keywords_used": keywords,
    }


@app.get("/api/export")
def export_investigations(
    format: str = "csv",
):
    if format not in ("csv", "json"):
        raise HTTPException(status_code=400, detail="format must be 'csv' or 'json'")

    if format == "json":
        content = json.dumps(_investigations, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=flamescope_investigations.json"},
        )

    # CSV export
    rows = []
    for inv in _investigations:
        row = dict(inv)
        row["safety_category"] = "|".join(row.get("safety_category", []))
        row["telemetry_files"] = "|".join(row.get("telemetry_files", []))
        rows.append(row)

    df = pd.DataFrame(rows)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flamescope_investigations.csv"},
    )


@app.get("/api/telemetry/{investigation_id}")
def get_telemetry(investigation_id: str):
    inv = _investigations_index.get(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail=f"Investigation {investigation_id!r} not found")

    if not inv.get("has_telemetry"):
        return {
            "investigation_id": investigation_id,
            "has_telemetry": False,
            "message": "No CSV telemetry available for this investigation",
            "rows": [],
            "files": [],
        }

    csv_pattern = str(COMBUSTION_DIR / f"{investigation_id}_*.csv")
    csv_files = sorted(glob.glob(csv_pattern))

    all_rows = []
    files_info = []
    for csv_path in csv_files:
        try:
            df = pd.read_csv(csv_path, encoding="latin-1")
            # Convert to records, filling NaN with None
            records = df.where(pd.notnull(df), None).to_dict(orient="records")
            fname = pathlib.Path(csv_path).name
            files_info.append({"file": fname, "rows": len(records)})
            # Tag each row with its source file
            for rec in records:
                rec["_source_file"] = fname
            all_rows.extend(records)
        except Exception as e:
            files_info.append({"file": pathlib.Path(csv_path).name, "error": str(e)})

    return {
        "investigation_id": investigation_id,
        "has_telemetry": True,
        "files": files_info,
        "total_rows": len(all_rows),
        "rows": all_rows,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
