"""
FlameScope - Step 3  |  src/api/main.py
=========================================

FastAPI backend serving extracted NASA PSI combustion investigation data.

Endpoints
---------
GET  /                            Health check
GET  /health                      Health check (alias)
GET  /investigations              Filterable, paginated list
GET  /investigations/{id}         Full record with all FieldValues
GET  /investigations/{id}/telemetry Raw CSV rows as JSON
POST  /reload                     Re-load records from data/processed/investigations.json
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.db import (  # noqa: E402
    COMBINED_JSON,
    DB_PATH,
    PROCESSED_DIR,
    get_connection,
    get_investigation,
    init_db,
    list_investigations,
    load_records,
)

log = logging.getLogger("flamescope.api.main")

app = FastAPI(
    title="FlameScope API",
    description="NASA PSI Microgravity Combustion & Spacecraft Fire Safety Data Connector",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db(DB_PATH)
    if COMBINED_JSON.exists():
        n = load_records(DB_PATH, COMBINED_JSON)
        log.info("Startup: loaded %d investigations into SQLite", n)
    else:
        log.warning(
            "data/processed/investigations.json not found — run Step 2 extraction first. "
            "The API will start with an empty database."
        )


@app.get("/", tags=["health"])
@app.get("/health", tags=["health"])
def health() -> Dict[str, Any]:
    conn = get_connection(DB_PATH)
    try:
        row = conn.execute("SELECT COUNT(*) AS c FROM investigations").fetchone()
        count = row["c"] if row else 0
    finally:
        conn.close()
    return {"status": "ok", "records": count}


@app.get("/investigations", tags=["investigations"])
def list_investigations_endpoint(
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type (substring match)"),
    fuel_state: Optional[str] = Query(None, description="solid | liquid | gas"),
    gravity_condition: Optional[str] = Query(
        None, description="microgravity | normal_gravity | partial_gravity"
    ),
    safety_category: Optional[str] = Query(
        None, description="prevention | detection | suppression (substring match on JSON array)"
    ),
    oxygen_min: Optional[float] = Query(None, description="Min O2 percent (inclusive)"),
    oxygen_max: Optional[float] = Query(None, description="Max O2 percent (inclusive)"),
    pressure_min: Optional[float] = Query(None, description="Min pressure psi (inclusive)"),
    pressure_max: Optional[float] = Query(None, description="Max pressure psi (inclusive)"),
    sample_shape: Optional[str] = Query(None, description="Sample shape (substring match)"),
    sample_size: Optional[str] = Query(None, description="Sample size (substring match)"),
    diluents: Optional[str] = Query(None, description="Diluents (substring match)"),
    hardware: Optional[str] = Query(None, description="Hardware (substring match)"),
    sensors_and_measurements: Optional[str] = Query(None, description="Sensors/measurements (substring match)"),
    objective: Optional[str] = Query(None, description="Objective (substring match)"),
    limit: int = Query(50, ge=1, le=500, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
) -> Dict[str, Any]:
    rows, total = list_investigations(
        DB_PATH,
        fuel_type=fuel_type,
        fuel_state=fuel_state,
        gravity_condition=gravity_condition,
        safety_category=safety_category,
        oxygen_min=oxygen_min,
        oxygen_max=oxygen_max,
        pressure_min=pressure_min,
        pressure_max=pressure_max,
        sample_shape=sample_shape,
        sample_size=sample_size,
        diluents=diluents,
        hardware=hardware,
        sensors_and_measurements=sensors_and_measurements,
        objective=objective,
        limit=limit,
        offset=offset,
    )
    return {"count": total, "offset": offset, "limit": limit, "results": rows}


@app.get("/investigations/{investigation_id}", tags=["investigations"])
def get_investigation_endpoint(investigation_id: str) -> Dict[str, Any]:
    record = get_investigation(DB_PATH, investigation_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Investigation {investigation_id} not found",
        )
    return record


@app.get("/investigations/{investigation_id}/telemetry", tags=["telemetry"])
def get_telemetry_endpoint(
    investigation_id: str,
    limit: Optional[int] = Query(None, ge=1, description="Max rows per CSV file"),
) -> Dict[str, Any]:
    summary_path = Path("data/combustion/summary_report.json")
    if not summary_path.is_absolute():
        summary_path = Path(__file__).resolve().parents[2] / summary_path

    files: List[Dict[str, Any]] = []
    matched_files: List[Path] = []

    if summary_path.exists():
        try:
            summary: List[dict] = json.loads(summary_path.read_text(encoding="utf-8"))
            for entry in summary:
                if entry.get("investigation_id") == investigation_id:
                    fname = entry.get("filename")
                    if fname:
                        csv_path = Path("data/combustion") / fname
                        if not csv_path.is_absolute():
                            csv_path = Path(__file__).resolve().parents[2] / csv_path
                        if csv_path.exists():
                            matched_files.append(csv_path)
        except Exception as exc:
            log.warning("Could not parse summary_report.json: %s", exc)

    combustion_dir = Path("data/combustion")
    if not combustion_dir.is_absolute():
        combustion_dir = Path(__file__).resolve().parents[2] / combustion_dir

    if combustion_dir.exists():
        for csv_path in sorted(combustion_dir.glob(f"*{investigation_id}*.csv")):
            if csv_path not in matched_files:
                matched_files.append(csv_path)

    for csv_path in matched_files:
        try:
            rows = _read_csv_rows(csv_path, limit=limit)
            files.append(
                {
                    "filename": csv_path.name,
                    "columns": rows["columns"],
                    "row_count": rows["row_count"],
                    "data": rows["data"],
                }
            )
        except Exception as exc:
            log.warning("Failed to read telemetry %s: %s", csv_path, exc)
            files.append({"filename": csv_path.name, "error": str(exc)})

    return {"investigation_id": investigation_id, "files": files}


@app.post("/compare", tags=["compare"])
def compare_investigations(
    investigation_ids: List[str],
) -> Dict[str, Any]:
    if len(investigation_ids) < 2 or len(investigation_ids) > 3:
        raise HTTPException(
            status_code=422,
            detail="Provide between 2 and 3 investigation IDs",
        )

    records: List[dict] = []
    missing: List[str] = []
    for inv_id in investigation_ids:
        rec = get_investigation(DB_PATH, inv_id)
        if rec is None:
            missing.append(inv_id)
        else:
            records.append(rec)

    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Investigation(s) not found: {', '.join(missing)}",
        )

    attr_keys = [
        "investigation_id", "title", "acronym", "doi",
        "fuel_type", "fuel_state", "oxygen_percent_min", "oxygen_percent_max",
        "pressure_psi", "gravity_condition", "safety_category",
        "sample_shape", "sample_size", "diluents", "hardware",
        "sensors_and_measurements", "objective",
        "airflow_speed_min", "airflow_speed_max",
    ]

    aligned_table: List[dict] = []
    for rec in records:
        row: dict = {}
        for key in attr_keys:
            fv = rec.get(key)
            if isinstance(fv, dict):
                row[key] = fv.get("value")
                row[f"{key}_unit"] = fv.get("unit")
                row[f"{key}_status"] = fv.get("status")
            else:
                row[key] = fv
        aligned_table.append(row)

    varied: List[str] = []
    same: List[str] = []
    for key in attr_keys:
        values = []
        for rec in records:
            fv = rec.get(key)
            if isinstance(fv, dict):
                values.append(json.dumps(fv.get("value"), sort_keys=True))
            else:
                values.append(json.dumps(fv, sort_keys=True))
        if all(v == values[0] for v in values):
            same.append(key)
        else:
            varied.append(key)

    telemetry_summary: List[dict] = []
    for rec in records:
        inv_id = rec["investigation_id"]
        summary_path = Path("data/combustion/summary_report.json")
        if not summary_path.is_absolute():
            summary_path = Path(__file__).resolve().parents[2] / summary_path

        col_variation: Dict[str, str] = {}
        if summary_path.exists():
            try:
                summary: List[dict] = json.loads(summary_path.read_text(encoding="utf-8"))
                for entry in summary:
                    if entry.get("investigation_id") != inv_id:
                        continue
                    for col in entry.get("columns", []):
                        clean = col.get("clean_name", "")
                        col_variation[clean] = "likely varies"
            except Exception as exc:
                log.warning("Could not parse summary_report.json for %s: %s", inv_id, exc)

        telemetry_summary.append({
            "investigation_id": inv_id,
            "columns": col_variation,
        })

    return {
        "investigations": records,
        "aligned_table": aligned_table,
        "what_varied": varied,
        "what_stayed_same": same,
        "telemetry_summary": telemetry_summary,
    }


@app.get("/search", tags=["search"])
def search_investigations(
    q: str = Query(..., description="Text search query"),
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type (substring match)"),
    fuel_state: Optional[str] = Query(None, description="solid | liquid | gas"),
    gravity_condition: Optional[str] = Query(
        None, description="microgravity | normal_gravity | partial_gravity"
    ),
    safety_category: Optional[str] = Query(
        None, description="prevention | detection | suppression"
    ),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
) -> Dict[str, Any]:
    query_terms = [t.lower() for t in q.split() if t.strip()]
    if not query_terms:
        return {"query": q, "matches": [], "count": 0}

    conn = get_connection(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT investigation_id, title, record_json FROM investigations"
        ).fetchall()
    finally:
        conn.close()

    matches: List[dict] = []
    for row in rows:
        inv_id = row["investigation_id"]
        title = row["title"] or ""
        record = json.loads(row["record_json"])

        text_blob_parts: List[str] = [title]
        for key in (
            "acronym", "doi", "source_url", "objective", "hardware",
            "fuel_type", "fuel_state", "gravity_condition", "safety_category",
            "sample_shape", "sample_size", "diluents", "pressure_psi",
            "sensors_and_measurements", "airflow_speed_min", "airflow_speed_max",
        ):
            fv = record.get(key)
            if isinstance(fv, dict):
                val = fv.get("value")
                if isinstance(val, list):
                    text_blob_parts.extend(str(v) for v in val)
                elif val is not None:
                    text_blob_parts.append(str(val))
            elif fv is not None:
                text_blob_parts.append(str(fv))

        text_blob = " ".join(text_blob_parts).lower()
        matched_terms = [t for t in query_terms if t in text_blob]
        if not matched_terms:
            continue

        relevance = len(matched_terms) / len(query_terms)

        def fv_value(key: str) -> Any:
            fv = record.get(key)
            if isinstance(fv, dict):
                return fv.get("value")
            return fv

        inv_fuel_type = fv_value("fuel_type")
        inv_fuel_state = fv_value("fuel_state")
        inv_gravity = fv_value("gravity_condition")
        inv_safety = fv_value("safety_category")

        if fuel_type and inv_fuel_type:
            ft_str = json.dumps(inv_fuel_type) if isinstance(inv_fuel_type, list) else str(inv_fuel_type)
            if fuel_type.lower() not in ft_str.lower():
                continue
        if fuel_state and inv_fuel_state and str(inv_fuel_state).lower() != fuel_state.lower():
            continue
        if gravity_condition and inv_gravity and str(inv_gravity).lower() != gravity_condition.lower():
            continue
        if safety_category and inv_safety:
            safety_items = inv_safety if isinstance(inv_safety, list) else [inv_safety]
            if not any(str(s).lower() == safety_category.lower() for s in safety_items):
                continue

        matches.append({
            "investigation_id": inv_id,
            "title": title,
            "relevance": round(relevance, 2),
            "matched_terms": matched_terms,
        })

    matches.sort(key=lambda m: m["relevance"], reverse=True)
    matches = matches[:limit]

    return {
        "query": q,
        "matches": matches,
        "count": len(matches),
    }


@app.post("/reload", tags=["admin"])
def reload_records() -> Dict[str, Any]:
    if not COMBINED_JSON.exists():
        raise HTTPException(
            status_code=404,
            detail="data/processed/investigations.json not found — run Step 2 first",
        )
    n = load_records(DB_PATH, COMBINED_JSON)
    return {"status": "reloaded", "records": n}


def _read_csv_rows(csv_path: Path, limit: Optional[int] = None) -> Dict[str, Any]:
    import csv as _csv

    with csv_path.open(newline="", encoding="utf-8-sig", errors="replace") as fh:
        reader = _csv.DictReader(fh)
        columns = reader.fieldnames or []
        data: List[dict] = []
        for i, row in enumerate(reader):
            if limit is not None and i >= limit:
                break
            cleaned = {k: (v if v != "" else None) for k, v in row.items()}
            data.append(cleaned)

    return {"columns": columns, "row_count": len(data), "data": data}