"""
FlameScope – Step 2  |  src/extract/extract_investigations.py
=============================================================

Reads each data/raw/<PSI-ID>/ folder, builds structured text chunks,
calls the Gemini API to extract a validated JSON record per investigation,
and saves results to data/processed/.

Usage
-----
    # All investigations found in data/raw/
    python src/extract/extract_investigations.py

    # Specific subset
    python src/extract/extract_investigations.py --investigations PSI-69 PSI-98 PSI-25

    # Dry-run: build chunks but skip LLM calls
    python src/extract/extract_investigations.py --dry-run

Environment
-----------
    Set GEMINI_API_KEY (or GOOGLE_API_KEY) before running.
    Model defaults to gemini-2.5-flash; override with --model.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import pathlib
import re
import sys
import textwrap
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
from pydantic import ValidationError

# ── local schema (same package) ──────────────────────────────────────────────
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schema import InvestigationExtracted, FieldValue  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FAILURE_LOG = ROOT / "extraction_failures.log"

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("flamescope.extract")


# ─────────────────────────────────────────────────────────────────────────────
# LLM prompts
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""\
    You extract structured facts from NASA microgravity combustion documents.
    Use ONLY the text provided. For each field in the schema, return the value,
    the unit, an exact short quote from the text that supports it, and the
    location of the quote. If the text does not state a value, return null with
    status 'unavailable'. Do not infer numbers. If you must infer a category
    (for example safety_category), mark status 'inferred' and explain in one
    sentence. Return valid JSON that matches the schema exactly and nothing else.
""")

SCHEMA_DESCRIPTION = textwrap.dedent("""\
    Return a JSON object with exactly these top-level keys.
    Every field (except investigation_id, title, acronym, doi, source_url) is
    a FieldValue object: { "value": ..., "unit": ..., "status": "verified"|"extracted"|"inferred"|"unavailable", "evidence_quote": "...", "evidence_location": "..." }

    Top-level keys:
      investigation_id   – string (provided)
      title              – string (provided)
      acronym            – string or null
      doi                – string or null
      source_url         – string (provided)
      objective          – FieldValue  (short plain-text summary of science goal)
      hardware           – FieldValue  (experiment hardware name, e.g. CIR, MDCA)
      fuel_type          – FieldValue  (e.g. methanol, ethanol, PMMA, cotton)
      fuel_state         – FieldValue  (value MUST be one of: solid, liquid, gas)
      sample_shape       – FieldValue  (droplet, slab, cylinder, fabric, sphere …)
      sample_size        – FieldValue  (numeric; include unit mm or cm)
      oxygen_percent_min – FieldValue  (numeric 0–100; if CSV col is mole fraction, multiply × 100)
      oxygen_percent_max – FieldValue  (numeric 0–100)
      pressure_psi       – FieldValue  (numeric; convert mmHg → psi by dividing by 51.715)
      airflow_speed_min  – FieldValue  (numeric cm/s)
      airflow_speed_max  – FieldValue  (numeric cm/s)
      diluents           – FieldValue  (list of diluent names, e.g. ["He","CO2"])
      gravity_condition  – FieldValue  (value MUST be one of: microgravity, normal_gravity, partial_gravity)
      sensors_and_measurements – FieldValue  (list of sensor / measurement types)
      safety_category    – FieldValue  (value MUST be a list from: prevention, detection, suppression)

    Rules:
    • For oxygen: the CSV column "O initial ambient composition; mole fraction" must be multiplied by 100 to get percent.
    • For pressure: "Ambient pressure; mmHg" divided by 51.715 gives psi.
    • oxygen_percent_min/max: use the minimum and maximum values found across all CSV rows.
    • airflow_speed_min/max: use the minimum and maximum values found.
    • If a field has multiple possible values (e.g. several fuels), list them in value as a JSON array.
    • Never invent numbers. If unsure, set status "unavailable".
""")

USER_PROMPT_TEMPLATE = """\
=== INVESTIGATION ID: {psi_id} ===

{context}

---
{schema_desc}

Return ONLY the JSON object. No markdown fences, no explanation.
"""

RETRY_PREFIX = (
    "IMPORTANT: Your previous response failed JSON/schema validation.\n"
    "Error: {error}\n\n"
    "Fix the JSON and return ONLY the corrected JSON object.\n\n"
    "Original context follows:\n\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# Context builder
# ─────────────────────────────────────────────────────────────────────────────

MAX_CONTEXT_CHARS = 28_000   # ~7 k tokens; Gemini 2.5 Flash handles 1M but we keep costs low
CSV_SAMPLE_ROWS = 8          # header + this many data rows


def _strip_html(text: str) -> str:
    """Remove simple HTML tags from PSI narrative fields."""
    return re.sub(r"<[^>]+>", " ", text).strip()


def _safe_text(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return _strip_html(str(val))


def _read_csv_sample(path: pathlib.Path) -> str:
    """Return CSV header + first CSV_SAMPLE_ROWS rows as a text block."""
    lines: list[str] = []
    for enc in ("utf-8-sig", "latin-1", "cp1252"):
        try:
            with path.open(newline="", encoding=enc) as fh:
                reader = csv.reader(fh)
                for i, row in enumerate(reader):
                    if i > CSV_SAMPLE_ROWS:
                        break
                    lines.append(", ".join(row))
            break
        except UnicodeDecodeError:
            continue
    return "\n".join(lines)


def _read_csv_stats(path: pathlib.Path) -> Dict[str, Any]:
    """Return min/max for numeric columns that look like O2, pressure, airflow."""
    import csv as _csv

    stats: dict[str, dict] = {}
    for enc in ("utf-8-sig", "latin-1", "cp1252"):
        try:
            with path.open(newline="", encoding=enc) as fh:
                reader = _csv.DictReader(fh)
                for row in reader:
                    for col, raw in row.items():
                        try:
                            val = float(raw)
                        except (ValueError, TypeError):
                            continue
                        if col not in stats:
                            stats[col] = {"min": val, "max": val}
                        else:
                            stats[col]["min"] = min(stats[col]["min"], val)
                            stats[col]["max"] = max(stats[col]["max"], val)
            break
        except UnicodeDecodeError:
            continue
    return stats


def build_context(psi_id: str, raw_folder: pathlib.Path) -> str:
    """
    Assemble a labeled text block from all source files in a raw folder.
    Returns a string < MAX_CONTEXT_CHARS characters.
    """
    sections: list[str] = []

    # ── 1. investigation_metadata.json ──────────────────────────────────────
    meta_path = raw_folder / "investigation_metadata.json"
    if meta_path.exists():
        try:
            meta: dict = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            log.warning("%s: cannot parse metadata JSON — %s", psi_id, exc)
            meta = {}

        narrative_fields = [
            ("title", "Title"),
            ("investigationAcronym", "Acronym"),
            ("doi", "DOI"),
            ("flightProgram", "Flight Program"),
            ("missionName", "Mission"),
            ("spaceProgram", "Space Program"),
            ("managingNasaCenter", "NASA Center"),
            ("researchArea", "Research Area"),
            ("subResearchArea", "Sub-research Area"),
            ("experimentHardware", "Hardware"),
            ("objective", "Objective"),
            ("description", "Description"),
            ("approach", "Approach"),
            ("hypothesis", "Hypothesis"),
            ("researchImpacts", "Research Impacts"),
            ("factors", "Factors"),
            ("payloads", "Payloads"),
        ]
        lines = [f"=== METADATA ({psi_id}) ==="]
        for key, label in narrative_fields:
            val = _safe_text(meta.get(key))
            if val:
                # Truncate very long narrative fields to 1500 chars
                if len(val) > 1500:
                    val = val[:1500] + " … [truncated]"
                lines.append(f"[{label}] {val}")
        sections.append("\n".join(lines))

    else:
        log.warning("%s: investigation_metadata.json not found", psi_id)

    # ── 2. CSV files ─────────────────────────────────────────────────────────
    csv_files = sorted(raw_folder.glob("*.csv"))
    for csv_path in csv_files:
        sample = _read_csv_sample(csv_path)
        stats = _read_csv_stats(csv_path)
        stats_lines = [f"  {col}: min={v['min']}, max={v['max']}" for col, v in stats.items()]
        block = (
            f"=== CSV: {csv_path.name} ===\n"
            f"Sample rows (header + first {CSV_SAMPLE_ROWS}):\n{sample}\n"
            f"Numeric column ranges across all rows:\n" + "\n".join(stats_lines)
        )
        sections.append(block)

    # ── 3. PDF-extracted text files ──────────────────────────────────────────
    for txt_path in sorted(raw_folder.glob("*_extracted.txt")):
        content = txt_path.read_text(encoding="utf-8", errors="replace")
        # Keep first 3000 chars of PDF text
        if len(content) > 3000:
            content = content[:3000] + "\n… [PDF text truncated]"
        sections.append(f"=== PDF TEXT: {txt_path.name} ===\n{content}")

    # ── 4. Plain text / readme files ─────────────────────────────────────────
    for txt_path in sorted(raw_folder.glob("*.txt")):
        if "_extracted" in txt_path.name:
            continue  # already handled above
        content = txt_path.read_text(encoding="utf-8", errors="replace")
        if len(content) > 2000:
            content = content[:2000] + "\n… [truncated]"
        sections.append(f"=== TEXT: {txt_path.name} ===\n{content}")

    # ── Join and truncate to budget ──────────────────────────────────────────
    full = "\n\n".join(sections)
    if len(full) > MAX_CONTEXT_CHARS:
        full = full[:MAX_CONTEXT_CHARS] + "\n\n… [context truncated to fit token budget]"
    return full


# ─────────────────────────────────────────────────────────────────────────────
# LLM call
# ─────────────────────────────────────────────────────────────────────────────

def call_llm(model: genai.GenerativeModel, prompt: str, system: str) -> str:
    """Call Gemini and return raw text response."""
    response = model.generate_content(
        [prompt],
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            max_output_tokens=4096,
        ),
    )
    return response.text.strip()


def _clean_json_fence(text: str) -> str:
    """Strip ```json … ``` fences if the model added them despite instructions."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Extraction pipeline per investigation
# ─────────────────────────────────────────────────────────────────────────────

PSI_SOURCE_URL = "https://psi.nasa.gov/investigations/{psi_id}"


def extract_one(
    psi_id: str,
    raw_folder: pathlib.Path,
    model: Optional[genai.GenerativeModel],
    dry_run: bool = False,
) -> Tuple[Optional[InvestigationExtracted], str]:
    """
    Build context, call LLM (or skip in dry-run), validate, and return
    (InvestigationExtracted | None, status_message).
    """
    log.info("── %s: building context …", psi_id)
    context = build_context(psi_id, raw_folder)
    log.info("   context length: %d chars", len(context))

    # Read a few identity fields directly from metadata for the fixed schema keys
    source_url = PSI_SOURCE_URL.format(psi_id=psi_id)
    title = psi_id
    acronym = None
    doi = None
    meta_path = raw_folder / "investigation_metadata.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            title = meta.get("title") or psi_id
            acronym = meta.get("investigationAcronym")
            doi = meta.get("doi")
        except Exception:
            pass

    if dry_run:
        log.info("   [DRY-RUN] skipping LLM call — returning empty record")
        record = InvestigationExtracted(
            investigation_id=psi_id,
            title=title,
            acronym=acronym,
            doi=doi,
            source_url=source_url,
        )
        return record, "dry_run"

    # ── Build user prompt ────────────────────────────────────────────────────
    user_prompt = USER_PROMPT_TEMPLATE.format(
        psi_id=psi_id,
        context=context,
        schema_desc=SCHEMA_DESCRIPTION,
    )

    # ── First attempt ────────────────────────────────────────────────────────
    for attempt in range(2):
        if attempt == 0:
            prompt = user_prompt
            log.info("   attempt 1: calling LLM …")
        else:
            prompt = (
                RETRY_PREFIX.format(error=last_error)
                + user_prompt
            )
            log.warning("   attempt 2: retrying after validation error …")

        try:
            raw_text = call_llm(model, prompt, SYSTEM_PROMPT)
        except Exception as exc:
            last_error = f"LLM API error: {exc}"
            log.error("   %s", last_error)
            continue

        raw_json = _clean_json_fence(raw_text)

        # ── Parse JSON ───────────────────────────────────────────────────────
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            last_error = f"JSONDecodeError: {exc}"
            log.warning("   JSON parse failed: %s", exc)
            continue

        # Inject fixed identity fields (overwrite whatever LLM returned)
        data["investigation_id"] = psi_id
        data["title"] = title
        data["acronym"] = acronym
        data["doi"] = doi
        data["source_url"] = source_url

        # ── Pydantic validation ──────────────────────────────────────────────
        try:
            record = InvestigationExtracted.model_validate(data)
            log.info("   ✓ validated successfully (attempt %d)", attempt + 1)
            return record, "ok"
        except ValidationError as exc:
            last_error = f"Pydantic ValidationError: {exc}"
            log.warning("   validation failed: %s", exc)
            continue

    # ── Both attempts failed ─────────────────────────────────────────────────
    log.error("%s: BOTH ATTEMPTS FAILED — flagging for manual review", psi_id)
    _save_review_needed(psi_id, raw_json if "raw_json" in dir() else "", last_error)  # type: ignore[arg-type]
    return None, "failed"


# ─────────────────────────────────────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────────────────────────────────────

FIELD_NAMES = [
    "objective", "hardware", "fuel_type", "fuel_state",
    "sample_shape", "sample_size",
    "oxygen_percent_min", "oxygen_percent_max",
    "pressure_psi",
    "airflow_speed_min", "airflow_speed_max",
    "diluents",
    "gravity_condition",
    "sensors_and_measurements",
    "safety_category",
]


def save_processed(record: InvestigationExtracted) -> None:
    """Write data/processed/<PSI-ID>.json"""
    out_path = PROCESSED_DIR / f"{record.investigation_id}.json"
    out_path.write_text(
        record.model_dump_json(indent=2),
        encoding="utf-8",
    )
    log.info("   saved → %s", out_path.relative_to(ROOT))


def save_review_csv(record: InvestigationExtracted) -> None:
    """Write data/processed/<PSI-ID>_review.csv — one row per schema field."""
    csv_path = PROCESSED_DIR / f"{record.investigation_id}_review.csv"
    rows = []
    for field_name in FIELD_NAMES:
        fv: FieldValue = getattr(record, field_name, FieldValue())
        rows.append({
            "field_name": field_name,
            "value": json.dumps(fv.value) if isinstance(fv.value, list) else fv.value,
            "unit": fv.unit,
            "status": fv.status,
            "evidence_quote": fv.evidence_quote,
            "evidence_location": fv.evidence_location,
        })
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["field_name", "value", "unit", "status", "evidence_quote", "evidence_location"],
        )
        writer.writeheader()
        writer.writerows(rows)
    log.info("   review csv → %s", csv_path.relative_to(ROOT))


def _save_review_needed(psi_id: str, raw_output: str, error: str) -> None:
    """Write a .REVIEW_NEEDED.json and append to failure log."""
    out_path = PROCESSED_DIR / f"{psi_id}.REVIEW_NEEDED.json"
    out_path.write_text(
        json.dumps({"raw_llm_output": raw_output, "error": error}, indent=2),
        encoding="utf-8",
    )
    with FAILURE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            f"{datetime.now(timezone.utc).isoformat()}  {psi_id}  {error}\n"
        )
    log.error("   review-needed → %s", out_path.relative_to(ROOT))


def save_combined(records: list[InvestigationExtracted]) -> None:
    """Write data/processed/investigations.json (array of all records)."""
    out_path = PROCESSED_DIR / "investigations.json"
    payload = [json.loads(r.model_dump_json()) for r in records]
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Combined output → %s  (%d records)", out_path.relative_to(ROOT), len(records))


# ─────────────────────────────────────────────────────────────────────────────
# Discovery
# ─────────────────────────────────────────────────────────────────────────────

def discover_psi_ids() -> List[str]:
    """Return all PSI-* folder names found in data/raw/."""
    ids = sorted(
        p.name for p in RAW_DIR.iterdir()
        if p.is_dir() and p.name.startswith("PSI-")
    )
    return ids


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="FlameScope Step 2 — LLM extraction of NASA PSI combustion investigations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python src/extract/extract_investigations.py
              python src/extract/extract_investigations.py --investigations PSI-69 PSI-98
              python src/extract/extract_investigations.py --dry-run
              python src/extract/extract_investigations.py --model gemini-2.0-flash
        """),
    )
    parser.add_argument(
        "--investigations", nargs="+", metavar="PSI-ID",
        help="PSI investigation IDs to process (default: all found in data/raw/)",
    )
    parser.add_argument(
        "--model", default="gemini-2.5-flash",
        help="Gemini model name (default: gemini-2.5-flash)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Build context chunks but skip LLM calls; write empty validated records",
    )
    parser.add_argument(
        "--delay", type=float, default=2.0,
        help="Seconds to wait between LLM calls (default: 2.0)",
    )
    args = parser.parse_args()

    # ── Discover investigations ──────────────────────────────────────────────
    if args.investigations:
        psi_ids = args.investigations
    else:
        psi_ids = discover_psi_ids()

    if not psi_ids:
        log.error("No PSI investigation folders found in %s", RAW_DIR)
        sys.exit(1)

    log.info("Investigations to process (%d): %s", len(psi_ids), psi_ids)

    # ── Configure Gemini ─────────────────────────────────────────────────────
    model_instance: Optional[genai.GenerativeModel] = None
    if not args.dry_run:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            log.error(
                "No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment.\n"
                "  Windows:  $env:GEMINI_API_KEY='your_key_here'\n"
                "  Linux:    export GEMINI_API_KEY='your_key_here'"
            )
            sys.exit(1)
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(
            model_name=args.model,
            system_instruction=SYSTEM_PROMPT,
        )
        log.info("LLM: %s", args.model)

    # ── Process each investigation ───────────────────────────────────────────
    successful: list[InvestigationExtracted] = []
    failed: list[str] = []

    for idx, psi_id in enumerate(psi_ids):
        raw_folder = RAW_DIR / psi_id
        if not raw_folder.is_dir():
            log.error("Folder not found, skipping: %s", raw_folder)
            failed.append(psi_id)
            continue

        # Skip if already processed (unless --force was given)
        out_path = PROCESSED_DIR / f"{psi_id}.json"
        if out_path.exists() and not args.dry_run:
            log.info("%s: already processed, skipping (delete %s to reprocess)", psi_id, out_path.name)
            try:
                record = InvestigationExtracted.model_validate_json(out_path.read_text(encoding="utf-8"))
                successful.append(record)
            except Exception:
                pass
            continue

        record, status = extract_one(psi_id, raw_folder, model_instance, dry_run=args.dry_run)

        if record is not None:
            save_processed(record)
            save_review_csv(record)
            successful.append(record)
        else:
            failed.append(psi_id)

        # Rate-limit between calls
        if not args.dry_run and idx < len(psi_ids) - 1:
            time.sleep(args.delay)

    # ── Combined output ──────────────────────────────────────────────────────
    if successful:
        save_combined(successful)

    # ── Summary ─────────────────────────────────────────────────────────────
    log.info("")
    log.info("═══════════════════════════════════════════════════")
    log.info("DONE  |  success: %d  |  failed: %d", len(successful), len(failed))
    if failed:
        log.warning("Failed IDs: %s", failed)
        log.warning("See %s for details.", FAILURE_LOG.name)
    log.info("Output dir: %s", PROCESSED_DIR.relative_to(ROOT))


if __name__ == "__main__":
    main()

