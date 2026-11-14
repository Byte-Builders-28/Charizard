#!/usr/bin/env python3
"""
FlameScope - NASA PSI S3 Inventory Generator
Step 0: S3 Exploration & Inventory

Lists files from the public NASA PSI S3 bucket (nasa-psi, us-west-2)
using anonymous / unsigned requests and outputs an inventory.csv.
"""

import argparse
import csv
import logging
import os
import sys
from typing import List, Optional

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("s3_inventory")

BUCKET_NAME = "nasa-psi"
REGION_NAME = "us-west-2"
MAX_DOWNLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit


def get_s3_client():
    """Initializes and returns an unsigned S3 client for public bucket access."""
    return boto3.client(
        "s3",
        region_name=REGION_NAME,
        config=Config(signature_version=UNSIGNED),
    )


def list_top_level_prefixes(s3_client, bucket: str = BUCKET_NAME) -> List[str]:
    """Retrieves all top-level common prefixes from the S3 bucket."""
    logger.info(f"Scanning top-level prefixes in s3://{bucket}/ (region: {REGION_NAME})...")
    paginator = s3_client.get_paginator("list_objects_v2")
    top_prefixes = []
    try:
        pages = paginator.paginate(Bucket=bucket, Delimiter="/")
        for page in pages:
            for p in page.get("CommonPrefixes", []):
                prefix = p.get("Prefix")
                if prefix:
                    top_prefixes.append(prefix)
    except ClientError as e:
        logger.error(f"Failed to list top-level prefixes: {e}")
        raise

    logger.info(f"Discovered {len(top_prefixes)} top-level prefixes: {top_prefixes}")
    return top_prefixes


def scan_prefix_inventory(
    s3_client,
    prefix: str,
    bucket: str = BUCKET_NAME,
    max_keys: Optional[int] = None,
) -> List[dict]:
    """
    Scans an S3 prefix and returns a list of file metadata records:
    [prefix, key, size_bytes, extension]
    """
    logger.info(f"Scanning files under prefix: '{prefix}' (max_keys: {max_keys or 'all'})...")
    paginator = s3_client.get_paginator("list_objects_v2")
    records = []
    count = 0

    pagination_args = {"Bucket": bucket, "Prefix": prefix}
    if max_keys and max_keys > 0:
        pagination_args["PaginationConfig"] = {"MaxItems": max_keys}

    try:
        for page in paginator.paginate(**pagination_args):
            contents = page.get("Contents", [])
            for obj in contents:
                key = obj.get("Key", "")
                size = obj.get("Size", 0)

                # Skip directory placeholder objects ending in '/'
                if key.endswith("/"):
                    continue

                _, ext = os.path.splitext(key)
                ext = ext.lstrip(".").lower() if ext else "none"

                records.append({
                    "prefix": prefix,
                    "key": key,
                    "size_bytes": size,
                    "extension": ext,
                })
                count += 1
                if max_keys and count >= max_keys:
                    break
            if max_keys and count >= max_keys:
                break
    except ClientError as e:
        logger.error(f"Error scanning prefix '{prefix}': {e}")
        raise

    logger.info(f"Prefix '{prefix}' completed: found {len(records)} files.")
    return records


def write_inventory_csv(records: List[dict], output_path: str = "inventory.csv"):
    """Writes list of records to CSV with required columns."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fieldnames = ["prefix", "key", "size_bytes", "extension"]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    logger.info(f"Successfully wrote {len(records)} records to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="List files and sizes from public NASA PSI S3 bucket (nasa-psi) and export inventory.csv"
    )
    parser.add_argument(
        "--prefix",
        action="append",
        help="S3 prefix to scan (e.g. DSI/ or OASIS/). Can be passed multiple times. If omitted, all top-level prefixes are scanned.",
    )
    parser.add_argument(
        "--max-keys",
        type=int,
        default=None,
        help="Maximum number of keys to list per prefix (useful for exploration/rate-limiting).",
    )
    parser.add_argument(
        "--output",
        default="inventory.csv",
        help="Path to output CSV file (default: inventory.csv).",
    )
    args = parser.parse_args()

    s3 = get_s3_client()

    prefixes_to_scan = args.prefix
    if not prefixes_to_scan:
        prefixes_to_scan = list_top_level_prefixes(s3)

    all_records = []
    for prefix in prefixes_to_scan:
        # Ensure trailing slash if user omitted it for directory prefixes
        clean_prefix = prefix if prefix.endswith("/") or "." in prefix else f"{prefix}/"
        prefix_records = scan_prefix_inventory(s3, clean_prefix, max_keys=args.max_keys)
        all_records.extend(prefix_records)

    write_inventory_csv(all_records, args.output)

    # Print summary statistics
    extensions = {}
    total_bytes = 0
    over_50mb_count = 0
    for r in all_records:
        ext = r["extension"]
        extensions[ext] = extensions.get(ext, 0) + 1
        total_bytes += r["size_bytes"]
        if r["size_bytes"] > MAX_DOWNLOAD_SIZE_BYTES:
            over_50mb_count += 1

    logger.info("=== Inventory Summary ===")
    logger.info(f"Total files listed: {len(all_records)}")
    logger.info(f"Total size: {total_bytes / (1024 * 1024):.2f} MB")
    logger.info(f"Files > 50 MB (flagged to prevent download): {over_50mb_count}")
    logger.info(f"Extensions breakdown: {extensions}")


if __name__ == "__main__":
    main()
