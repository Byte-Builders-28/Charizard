"""
FlameScope - Step 3  |  src/api/db.py
=======================================

SQLite data access layer for the FlameScope API.

Design
------
Hybrid approach:

* Denormalized scalar filter columns (fuel_state, gravity_condition, …) for
  fast `WHERE` clauses on the list endpoint.
* `record_json` TEXT column holding the full serialized `InvestigationExtracted`
  so the detail endpoint returns every `FieldValue` (value, unit, status,
  evidence_quote, evidence_location) without a second table join.

Tables
------
investigations
  investigation_id   TEXT PRIMARY KEY
  title              TEXT NOT NULL
  acronym            TEXT
  doi                TEXT
  source_url         TEXT
  fuel_type          TEXT        (denormalized filter column)
  fuel_state         TEXT        (denormalized filter column)
  gravity_condition  TEXT        (denormalized filter column)
  oxygen_percent_min REAL
  oxygen_percent_max REAL
  pressure_psi       REAL
  airflow_speed_min  REAL
  airflow_speed_max  REAL
  safety_category    TEXT        (JSON array text, e.g. '["prevention"]')
  record_json        TEXT NOT NULL
  created_at         TEXT DEFAULT (datetime('now'))
"""

from __future__ import annotations

import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from extract.schema import InvestigationExtracted  # noqa: E402

log = logging.getLogger("flamescope.api.db")

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "flamescope.db"
PROCESSED_DIR = ROOT / "data" / "processed"
COMBINED_JSON = PROCESSED_DIR / "investigations.json"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS investigations (
                investigation_id   TEXT PRIMARY KEY,
                title              TEXT NOT NULL,
                acronym            TEXT,
                doi                TEXT,
                source_url         TEXT,
                fuel_type          TEXT,
                fuel_state         TEXT,
                gravity_condition  TEXT,
                oxygen_percent_min REAL,
                oxygen_percent_max REAL,
                pressure_psi       REAL,
                airflow_speed_min  REAL,
                airflow_speed_max  REAL,
                safety_category    TEXT,
                record_json        TEXT NOT NULL,
                created_at         TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_inv_fuel_state   ON investigations(fuel_state);
            CREATE INDEX IF NOT EXISTS idx_inv_gravity      ON investigations(gravity_condition);
            CREATE INDEX IF NOT EXISTS idx_inv_safety       ON investigations(safety_category);
            CREATE INDEX IF NOT EXISTS idx_inv_fuel_type    ON investigations(fuel_type);
            """
        )
        conn.commit()
    finally:
        conn.close()


# ── Helpers: extract scalar filter columns ──────────────────────────────────

def _fv_value(fv: Any) -> Any:
    if fv is None:
        return None
    return getattr(fv, "value", None)


def _as_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _as_scalar(val: Any) -> Any:
    """Coerce a FieldValue value to a SQLite-compatible scalar.
    Lists are JSON-serialized; everything else is passed through.
    """
    if isinstance(val, list):
        return json.dumps(val, ensure_ascii=False)
    return val


def _extract_filter_columns(record: InvestigationExtracted) -> Dict[str, Any]:
    return {
        "investigation_id": record.investigation_id,
        "title": record.title,
        "acronym": record.acronym,
        "doi": record.doi,
        "source_url": record.source_url,
        "fuel_type": _as_scalar(_fv_value(record.fuel_type)),
        "fuel_state": _as_scalar(_fv_value(record.fuel_state)),
        "gravity_condition": _as_scalar(_fv_value(record.gravity_condition)),
        "oxygen_percent_min": _as_float(_fv_value(record.oxygen_percent_min)),
        "oxygen_percent_max": _as_float(_fv_value(record.oxygen_percent_max)),
        "pressure_psi": _as_float(_fv_value(record.pressure_psi)),
        "airflow_speed_min": _as_float(_fv_value(record.airflow_speed_min)),
        "airflow_speed_max": _as_float(_fv_value(record.airflow_speed_max)),
        "safety_category": (
            json.dumps(_fv_value(record.safety_category), ensure_ascii=False)
            if isinstance(_fv_value(record.safety_category), list)
            else None
        ),
        "record_json": record.model_dump_json(),
    }


# ── Load / upsert records from the combined Step-2 JSON ─────────────────────

def load_records(db_path: Path = DB_PATH, json_path: Path = COMBINED_JSON) -> int:
    if not json_path.exists():
        log.warning("Combined JSON not found: %s — skipping DB load", json_path)
        return 0

    data: List[dict] = json.loads(json_path.read_text(encoding="utf-8"))
    log.info("Loading %d investigation records into SQLite…", len(data))

    conn = get_connection(db_path)
    try:
        count = 0
        for entry in data:
            try:
                record = InvestigationExtracted.model_validate(entry)
            except Exception as exc:
                log.warning("Skipping invalid record %s: %s", entry.get("investigation_id"), exc)
                continue

            cols = _extract_filter_columns(record)
            conn.execute(
                """
                INSERT OR REPLACE INTO investigations
                (investigation_id, title, acronym, doi, source_url,
                 fuel_type, fuel_state, gravity_condition,
                 oxygen_percent_min, oxygen_percent_max, pressure_psi,
                 airflow_speed_min, airflow_speed_max, safety_category, record_json)
                VALUES (:investigation_id, :title, :acronym, :doi, :source_url,
                        :fuel_type, :fuel_state, :gravity_condition,
                        :oxygen_percent_min, :oxygen_percent_max, :pressure_psi,
                        :airflow_speed_min, :airflow_speed_max, :safety_category,
                        :record_json)
                """,
                cols,
            )
            count += 1

        conn.commit()
        log.info("Upserted %d investigation records into %s", count, db_path)
        return count
    finally:
        conn.close()


# ── Query functions ─────────────────────────────────────────────────────────

def list_investigations(
    db_path: Path = DB_PATH,
    *,
    fuel_type: Optional[str] = None,
    fuel_state: Optional[str] = None,
    gravity_condition: Optional[str] = None,
    safety_category: Optional[str] = None,
    oxygen_min: Optional[float] = None,
    oxygen_max: Optional[float] = None,
    pressure_min: Optional[float] = None,
    pressure_max: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[dict], int]:
    conn = get_connection(db_path)
    try:
        where: List[str] = []
        params: Dict[str, Any] = {"limit": limit, "offset": offset}

        if fuel_type:
            where.append("fuel_type LIKE :fuel_type")
            params["fuel_type"] = f"%{fuel_type}%"
        if fuel_state:
            where.append("fuel_state = :fuel_state")
            params["fuel_state"] = fuel_state
        if gravity_condition:
            where.append("gravity_condition = :gravity_condition")
            params["gravity_condition"] = gravity_condition
        if safety_category:
            where.append("safety_category LIKE :safety_category")
            params["safety_category"] = f'%"{safety_category}"%'
        if oxygen_min is not None:
            where.append("oxygen_percent_max >= :oxygen_min")
            params["oxygen_min"] = oxygen_min
        if oxygen_max is not None:
            where.append("oxygen_percent_min <= :oxygen_max")
            params["oxygen_max"] = oxygen_max
        if pressure_min is not None:
            where.append("pressure_psi >= :pressure_min")
            params["pressure_min"] = pressure_min
        if pressure_max is not None:
            where.append("pressure_psi <= :pressure_max")
            params["pressure_max"] = pressure_max

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        count_row = conn.execute(
            f"SELECT COUNT(*) AS c FROM investigations {where_sql}",
            {k: v for k, v in params.items() if k not in ("limit", "offset")},
        ).fetchone()
        total = count_row["c"] if count_row else 0

        rows = conn.execute(
            f"""
            SELECT investigation_id, title, acronym, doi, source_url,
                   fuel_type, fuel_state, gravity_condition,
                   oxygen_percent_min, oxygen_percent_max, pressure_psi,
                   airflow_speed_min, airflow_speed_max, safety_category
            FROM investigations {where_sql}
            ORDER BY investigation_id
            LIMIT :limit OFFSET :offset
            """,
            params,
        ).fetchall()

        result = [dict(r) for r in rows]
        return result, total
    finally:
        conn.close()


def get_investigation(db_path: Path = DB_PATH, investigation_id: str = "") -> Optional[dict]:
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT record_json FROM investigations WHERE investigation_id = ?",
            (investigation_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["record_json"])
    finally:
        conn.close()