#!/usr/bin/env python3
"""
FlameScope - NASA PSI & S3 Data Ingestion Engine (Step 1)
Goal: Reliable, repeatable collection of raw records with provenance.

Features:
- Given a list of PSI investigation IDs and/or S3 prefixes:
  - Downloads investigation metadata & descriptions (JSON)
  - Downloads experiment tables (CSV, XLSX)
  - Downloads documentation & reports (PDF, TXT)
  - Skips heavy videos or files larger than threshold (default 25 MB, max 50 MB)
- Preserves raw provenance in data/raw/<PSI-ID>/manifest.json with:
  - source_url or s3_key
  - retrieved_at (UTC ISO format)
  - size_bytes
  - sha256 checksum
- Idempotent: skips already downloaded files if file exists and matches size/checksum
- Retries on network errors with exponential backoff
- Logs failures to ingest_failures.log
- For PDFs: extracts plain text into a companion .txt file with page numbers preserved
  ('--- Page <N> ---') for accurate scientific citations.
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
from typing import Any, Dict, List, Optional

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError
import pypdf

# Configure logging
LOG_FAILURE_FILE = "ingest_failures.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ingest.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("ingest_psi")

S3_BUCKET_NAME = "nasa-psi"
S3_REGION = "us-west-2"
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB limit
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0


def get_s3_client():
    """Initializes and returns an unsigned boto3 S3 client."""
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        config=Config(signature_version=UNSIGNED),
    )


def log_failure(item_id: str, file_name: str, source: str, error_msg: str):
    """Appends an ingestion failure entry to ingest_failures.log."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entry = f"{timestamp} | {item_id} | {file_name} | {source} | ERROR: {error_msg}\n"
    with open(LOG_FAILURE_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    logger.error(f"Ingestion failed for {item_id}/{file_name}: {error_msg}")


def compute_sha256(filepath: str) -> str:
    """Computes SHA256 hash of a local file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_pdf_text_with_pages(pdf_path: str, txt_path: str) -> bool:
    """
    Extracts plain text from a PDF, prefixing each page with '--- Page <N> ---'
    so subsequent NLP and citation modules can reference exact page numbers.
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        extracted_pages = []
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            extracted_pages.append(f"--- Page {idx} ---\n{text.strip()}\n")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(extracted_pages))
        logger.info(f"Successfully extracted {len(reader.pages)} page(s) to {txt_path}")
        return True
    except Exception as e:
        logger.warning(f"Failed to extract PDF text from {pdf_path}: {e}")
        return False


def load_manifest(manifest_path: str) -> dict:
    """Loads existing manifest.json if present; otherwise returns empty manifest structure."""
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading manifest {manifest_path}: {e}")
    return {"files": {}}


def save_manifest(manifest_path: str, manifest: dict):
    """Atomically persists manifest.json."""
    temp_path = manifest_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    if os.path.exists(manifest_path):
        os.remove(manifest_path)
    os.rename(temp_path, manifest_path)


def download_http_with_retry(url: str, dest_path: str, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> bool:
    """Downloads a file via HTTP with exponential backoff retry and size limits."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 FlameScope-Ingest/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                content_len = resp.headers.get("Content-Length")
                if content_len and int(content_len) > max_size_bytes:
                    logger.warning(f"File size {content_len} bytes exceeds limit {max_size_bytes}. Skipping.")
                    return False

                temp_path = dest_path + ".tmp"
                downloaded = 0
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        downloaded += len(chunk)
                        if downloaded > max_size_bytes:
                            logger.warning(f"File {url} exceeded size limit during streaming. Aborting.")
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
            logger.warning(f"HTTP download attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_FACTOR ** attempt)
            else:
                return False
    return False


def download_s3_file_with_retry(s3_client, bucket: str, key: str, dest_path: str, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> bool:
    """Downloads a file from S3 bucket with size validation and retries."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            head = s3_client.head_object(Bucket=bucket, Key=key)
            size = head.get("ContentLength", 0)
            if size > max_size_bytes:
                logger.warning(f"S3 object s3://{bucket}/{key} size ({size} bytes) > limit ({max_size_bytes}). Skipping.")
                return False

            temp_path = dest_path + ".tmp"
            s3_client.download_file(bucket, key, temp_path)

            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(temp_path, dest_path)
            return True
        except Exception as e:
            logger.warning(f"S3 download attempt {attempt}/{MAX_RETRIES} failed for s3://{bucket}/{key}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_FACTOR ** attempt)
            else:
                return False
    return False


def fetch_investigation_metadata(psi_id: str) -> Optional[dict]:
    """Retrieves full investigation metadata from NASA PSI API."""
    url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 FlameScope/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Error fetching metadata for {psi_id}: {e}")
        return None


def get_psi_download_url(psi_id: str, filename: str, version: int = 1) -> Optional[str]:
    """Retrieves signed download URL from PSI studies endpoint."""
    params = {
        "file": filename,
        "version": str(version),
        "redirect": "false"
    }
    url = f"https://psi.nasa.gov/geode-py/ws/studies/{psi_id}/download?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 FlameScope/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            return res.read().decode("utf-8").strip()
    except Exception as e:
        logger.warning(f"Could not get signed URL for {psi_id}/{filename}: {e}")
        params["redirect"] = "true"
        return f"https://psi.nasa.gov/geode-py/ws/studies/{psi_id}/download?{urllib.parse.urlencode(params)}"


def ingest_investigation(psi_id: str, base_raw_dir: str = "data/raw") -> dict:
    """Ingests metadata, tables, documentation for a NASA PSI Investigation ID."""
    out_dir = os.path.join(base_raw_dir, psi_id)
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "manifest.json")
    manifest = load_manifest(manifest_path)

    logger.info(f"Ingesting investigation {psi_id} into {out_dir}...")

    # 1. Download & persist investigation description JSON
    meta = fetch_investigation_metadata(psi_id)
    if not meta:
        log_failure(psi_id, "investigation_metadata.json", f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}", "Metadata request failed")
        return manifest

    meta_file = "investigation_metadata.json"
    meta_path = os.path.join(out_dir, meta_file)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    manifest["files"][meta_file] = {
        "source_url": f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{psi_id}",
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "size_bytes": os.path.getsize(meta_path),
        "sha256": compute_sha256(meta_path),
        "type": "investigation_metadata"
    }

    # 2. Gather candidates
    candidates = []
    for item in meta.get("experimentalTable", []):
        candidates.append({"item": item, "category": "experimental_table"})
    for item in meta.get("modelingTable", []):
        candidates.append({"item": item, "category": "modeling_table"})
    for item in meta.get("readme", []):
        candidates.append({"item": item, "category": "documentation"})

    for entry in candidates:
        item = entry["item"]
        cat = entry["category"]
        fname = item.get("file_name", "")
        fsize = item.get("file_size", 0)
        version = item.get("version", 1)

        if not fname:
            continue

        ext = os.path.splitext(fname)[1].lower()
        if ext not in [".csv", ".xlsx", ".pdf", ".txt", ".json"]:
            continue

        if fsize > MAX_FILE_SIZE_BYTES:
            logger.info(f"Skipping {fname}: size {fsize} > limit {MAX_FILE_SIZE_BYTES}")
            continue

        dest_file_path = os.path.join(out_dir, fname)

        # Idempotency check: if file already exists with same size, skip
        if os.path.exists(dest_file_path) and os.path.getsize(dest_file_path) == fsize and fname in manifest["files"]:
            logger.info(f"Idempotent skip: {fname} already downloaded.")
            continue

        download_url = get_psi_download_url(psi_id, fname, version)
        if not download_url:
            log_failure(psi_id, fname, "N/A", "Failed to retrieve signed download URL")
            continue

        logger.info(f"Downloading {fname} ({fsize} bytes)...")
        success = download_http_with_retry(download_url, dest_file_path)
        if not success:
            log_failure(psi_id, fname, download_url, "Download failed after retries")
            continue

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
    return manifest


def ingest_s3_prefix(prefix: str, s3_client=None, base_raw_dir: str = "data/raw") -> dict:
    """Ingests small files under an S3 prefix in nasa-psi."""
    if not s3_client:
        s3_client = get_s3_client()

    clean_prefix = prefix.strip("/")
    folder_name = clean_prefix.split("/")[0]
    out_dir = os.path.join(base_raw_dir, folder_name)
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "manifest.json")
    manifest = load_manifest(manifest_path)

    logger.info(f"Ingesting S3 prefix s3://{S3_BUCKET_NAME}/{prefix} -> {out_dir}...")
    paginator = s3_client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj.get("Key", "")
            size = obj.get("Size", 0)
            if key.endswith("/"):
                continue

            fname = os.path.basename(key)
            ext = os.path.splitext(fname)[1].lower()

            if ext not in [".csv", ".xlsx", ".pdf", ".txt", ".json", ".docx"]:
                continue

            if size > MAX_FILE_SIZE_BYTES:
                continue

            dest_path = os.path.join(out_dir, fname)

            # Idempotent skip
            if os.path.exists(dest_path) and os.path.getsize(dest_path) == size and fname in manifest["files"]:
                logger.info(f"Idempotent skip S3: {fname}")
                continue

            logger.info(f"Downloading S3 file {key} ({size} bytes)...")
            success = download_s3_file_with_retry(s3_client, S3_BUCKET_NAME, key, dest_path)
            if not success:
                log_failure(folder_name, fname, f"s3://{S3_BUCKET_NAME}/{key}", "Failed S3 download")
                continue

            checksum = compute_sha256(dest_path)
            manifest["files"][fname] = {
                "s3_key": key,
                "s3_bucket": S3_BUCKET_NAME,
                "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "size_bytes": os.path.getsize(dest_path),
                "sha256": checksum,
                "category": "s3_archive_file"
            }

            if ext == ".pdf":
                txt_fname = os.path.splitext(fname)[0] + "_extracted.txt"
                txt_path = os.path.join(out_dir, txt_fname)
                if extract_pdf_text_with_pages(dest_path, txt_path):
                    manifest["files"][txt_fname] = {
                        "source_url": f"extracted_from:{fname}",
                        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "size_bytes": os.path.getsize(txt_path),
                        "sha256": compute_sha256(txt_path),
                        "category": "extracted_pdf_text"
                    }

    save_manifest(manifest_path, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="FlameScope Step 1 Ingestion Engine - Provenance-tracked microgravity data ingestion"
    )
    parser.add_argument(
        "--investigations",
        nargs="+",
        default=["PSI-69", "PSI-68", "PSI-98", "PSI-99", "PSI-25", "PSI-26", "PSI-107", "PSI-102", "PSI-159", "PSI-20"],
        help="List of PSI investigation IDs to ingest (e.g. PSI-69 PSI-98)",
    )
    parser.add_argument(
        "--s3-prefixes",
        nargs="+",
        default=["pk4/To_NASA_team/Campaign_Reports/"],
        help="List of S3 prefixes to ingest documentation/reports from",
    )
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        help="Base raw directory (default: data/raw)",
    )
    args = parser.parse_args()

    logger.info("=== FlameScope Step 1 Data Ingestion Pipeline ===")
    
    # 1. Ingest PSI investigations
    if args.investigations:
        logger.info(f"Ingesting {len(args.investigations)} PSI investigations...")
        for pid in args.investigations:
            ingest_investigation(pid, base_raw_dir=args.raw_dir)

    # 2. Ingest S3 prefixes
    if args.s3_prefixes:
        s3 = get_s3_client()
        logger.info(f"Ingesting {len(args.s3_prefixes)} S3 prefix(es)...")
        for pfx in args.s3_prefixes:
            ingest_s3_prefix(pfx, s3_client=s3, base_raw_dir=args.raw_dir)

    logger.info("All ingestion tasks completed.")


if __name__ == "__main__":
    main()
