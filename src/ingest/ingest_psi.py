#!/usr/bin/env python3
"""
FlameScope - Data Ingestion Module (Step 1)
Goal: Reliable, repeatable collection of raw records with provenance.

Features:
- Downloads experiment tables (CSV, XLSX), documentation PDFs, and JSON descriptions into data/raw/<PSI-ID>/
- Generates data/raw/<PSI-ID>/manifest.json with: source_url / s3_key, retrieved_at (UTC), size_bytes, sha256
- Idempotent: skips existing files with matching size
- Network error retry with exponential backoff
- Logs failures to ingest_failures.log
- PDF plain text extraction with page numbers preserved for citation referencing
"""

import argparse
import datetime
import hashlib
import json
import logging
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

try:
    import pypdf
except ImportError:
    pypdf = None

# Configure logging
LOG_FILE = "ingest_failures.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ingest.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("ingest_psi")

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB limit
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0


def log_failure(psi_id: str, file_name: str, url: str, error_msg: str):
    """Logs ingestion failures to a dedicated failure log file."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    failure_entry = f"{timestamp} | {psi_id} | {file_name} | {url} | ERROR: {error_msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(failure_entry)
    logger.error(f"Ingestion failed for {psi_id}/{file_name}: {error_msg}")


def compute_sha256(filepath: str) -> str:
    """Computes the SHA256 hex digest of a local file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_pdf_text_with_pages(pdf_path: str, txt_path: str) -> bool:
    """
    Extracts text from a PDF file into a companion .txt file,
    preserving page numbers: '--- Page <N> ---'
    """
    if not pypdf:
        logger.warning(f"pypdf not installed; skipping PDF text extraction for {pdf_path}")
        return False

    try:
        reader = pypdf.PdfReader(pdf_path)
        extracted_pages = []
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            extracted_pages.append(f"--- Page {idx} ---\n{text.strip()}\n")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(extracted_pages))
        logger.info(f"Extracted {len(reader.pages)} pages to text: {txt_path}")
        return True
    except Exception as e:
        logger.warning(f"Failed to extract text from {pdf_path}: {e}")
        return False


def download_with_retry(url: str, dest_path: str, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> bool:
    """
    Downloads a file from a URL with retry logic and size cap.
    Returns True if downloaded, False otherwise.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FlameScope/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > max_size_bytes:
                    logger.warning(f"Skipping {url}: Content-Length {content_length} exceeds limit {max_size_bytes}")
                    return False

                temp_path = dest_path + ".tmp"
                downloaded = 0
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        downloaded += len(chunk)
                        if downloaded > max_size_bytes:
                            logger.warning(f"File {url} exceeded max size during stream. Aborting.")
                            f.close()
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            return False
                        f.write(chunk)

                if os.path.exists(dest_path):
                    os.remove(dest_path)
                os.rename(temp_path, dest_path)
                return True
        except Exception as e:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_FACTOR ** attempt)
            else:
                return False
    return False


def fetch_investigation_json(psi_id: str) -> Optional[dict]:
    """Fetches full investigation metadata record from NASA PSI API."""
    url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Error fetching investigation record for {psi_id}: {e}")
        return None


def get_download_url(psi_id: str, filename: str, version: int = 1) -> Optional[str]:
    """
    Resolves pre-signed / direct download URL from NASA PSI studies download endpoint.
    """
    params = {
        "file": filename,
        "version": str(version),
        "redirect": "false"
    }
    url = f"https://psi.nasa.gov/geode-py/ws/studies/{psi_id}/download?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            presigned_url = res.read().decode("utf-8").strip()
            return presigned_url
    except Exception as e:
        logger.warning(f"Could not get presigned URL for {psi_id}/{filename}: {e}")
        # Fallback to direct redirect endpoint
        params["redirect"] = "true"
        return f"https://psi.nasa.gov/geode-py/ws/studies/{psi_id}/download?{urllib.parse.urlencode(params)}"


def load_manifest(manifest_path: str) -> dict:
    """Loads existing manifest.json if present."""
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading manifest {manifest_path}: {e}")
    return {"files": {}}


def save_manifest(manifest_path: str, manifest: dict):
    """Persists manifest.json."""
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def ingest_investigation(psi_id: str, base_raw_dir: str = "data/raw") -> dict:
    """
    Ingests all small raw records for an investigation:
    - metadata description json
    - experimental and modeling tables (.csv, .xlsx)
    - documentation and readme (.pdf, .txt)
    - companion .txt extracted from PDFs
    - manifest.json
    """
    out_dir = os.path.join(base_raw_dir, psi_id)
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "manifest.json")
    manifest = load_manifest(manifest_path)

    logger.info(f"Starting ingestion for investigation: {psi_id} -> {out_dir}")

    # 1. Fetch & Save Investigation Metadata Description
    meta = fetch_investigation_json(psi_id)
    if not meta:
        log_failure(psi_id, "investigation_metadata.json", f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}", "Failed to retrieve metadata")
        return manifest

    meta_file = "investigation_metadata.json"
    meta_path = os.path.join(out_dir, meta_file)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    meta_stat = os.stat(meta_path)
    manifest["files"][meta_file] = {
        "source_url": f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}",
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "size_bytes": meta_stat.st_size,
        "sha256": compute_sha256(meta_path),
        "type": "investigation_metadata"
    }

    # 2. Collect Candidate Tables & Documentation
    candidates = []
    for item in meta.get("experimentalTable", []):
        candidates.append({"item": item, "category": "experimental_table"})
    for item in meta.get("modelingTable", []):
        candidates.append({"item": item, "category": "modeling_table"})
    for item in meta.get("readme", []):
        candidates.append({"item": item, "category": "documentation"})

    logger.info(f"{psi_id}: Found {len(candidates)} file candidate(s) in repository.")

    for entry in candidates:
        item = entry["item"]
        cat = entry["category"]
        fname = item.get("file_name", "")
        fsize = item.get("file_size", 0)
        version = item.get("version", 1)

        if not fname:
            continue

        ext = os.path.splitext(fname)[1].lower()
        if ext not in [".csv", ".xlsx", ".pdf", ".txt", ".json", ".tsv"]:
            logger.info(f"Skipping non-tabular/non-doc file: {fname} ({ext})")
            continue

        if fsize > MAX_FILE_SIZE_BYTES:
            logger.info(f"Skipping {fname}: size {fsize} bytes > {MAX_FILE_SIZE_BYTES} limit")
            continue

        dest_file_path = os.path.join(out_dir, fname)

        # Idempotency check: if file already exists with same size, skip download
        if os.path.exists(dest_file_path) and os.path.getsize(dest_file_path) == fsize and fname in manifest["files"]:
            logger.info(f"Idempotent skip: {fname} already downloaded and matches recorded size.")
            continue

        # Get download link
        download_url = get_download_url(psi_id, fname, version)
        if not download_url:
            log_failure(psi_id, fname, "N/A", "Failed to obtain download URL")
            continue

        logger.info(f"Downloading {fname} ({fsize} bytes)...")
        success = download_with_retry(download_url, dest_file_path)
        if not success:
            log_failure(psi_id, fname, download_url, "Download failed after retries or size limit exceeded")
            continue

        # Record in manifest
        actual_size = os.path.getsize(dest_file_path)
        checksum = compute_sha256(dest_file_path)
        manifest["files"][fname] = {
            "source_url": download_url,
            "s3_path": item.get("s3_path", ""),
            "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "size_bytes": actual_size,
            "sha256": checksum,
            "category": cat,
            "version": version
        }

        # If PDF, extract text with page numbers
        if ext == ".pdf":
            txt_fname = os.path.splitext(fname)[0] + "_extracted.txt"
            txt_path = os.path.join(out_dir, txt_fname)
            if extract_pdf_text_with_pages(dest_file_path, txt_path):
                manifest["files"][txt_fname] = {
                    "source_url": f"extracted_from:{fname}",
                    "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "size_bytes": os.path.getsize(txt_path),
                    "sha256": compute_sha256(txt_path),
                    "category": "extracted_pdf_text"
                }

    save_manifest(manifest_path, manifest)
    logger.info(f"Finished {psi_id}. Manifest saved with {len(manifest['files'])} entries.")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="FlameScope Ingestion - Download PSI records with provenance")
    parser.add_argument(
        "--investigations",
        nargs="+",
        default=["PSI-69", "PSI-98", "PSI-25", "PSI-60", "PSI-159", "PSI-102", "PSI-68", "PSI-10"],
        help="List of PSI investigation IDs to ingest (e.g. PSI-69 PSI-98 PSI-25)",
    )
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        help="Base raw directory (default: data/raw)",
    )
    args = parser.parse_args()

    logger.info(f"Starting FlameScope Ingestion for {len(args.investigations)} investigations: {args.investigations}")
    for pid in args.investigations:
        ingest_investigation(pid, base_raw_dir=args.raw_dir)

    logger.info("Ingestion completed successfully.")


if __name__ == "__main__":
    main()
