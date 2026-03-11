"""
load_responses.py — Bulk load 108 HR responses into Janina database
===================================================================
Run this once during initialization to populate janina_responses table.

Usage:
    python load_responses.py --file responses.json
    python load_responses.py --file responses.csv

Expects input format (JSON or CSV):
    [
      {
        "category": "benefits",
        "query_type": "faq",
        "keywords": ["vacation", "pto", "time-off"],
        "response_text": "Our vacation policy allows...",
        "quality_score": 0.95
      },
      ...
    ]
"""

import os
import sys
import json
import csv
import logging
import argparse
from typing import List, Dict

import psycopg2

logger = logging.getLogger("load_responses")
logging.basicConfig(level=logging.INFO)


def get_db_conn():
    """Get Postgres connection from environment."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set in environment")
    return psycopg2.connect(db_url)


def load_from_json(filepath: str) -> List[Dict]:
    """Load responses from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = [data]
        logger.info(f"Loaded {len(data)} responses from JSON")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        return []


def load_from_csv(filepath: str) -> List[Dict]:
    """Load responses from CSV file."""
    try:
        responses = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse keywords from comma-separated string
                keywords = [k.strip() for k in row.get('keywords', '').split(',')]
                quality = float(row.get('quality_score', 0.0))
                
                responses.append({
                    'category': row['category'],
                    'query_type': row.get('query_type', 'general'),
                    'keywords': keywords,
                    'response_text': row['response_text'],
                    'quality_score': quality,
                })
        logger.info(f"Loaded {len(responses)} responses from CSV")
        return responses
    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        return []


def bulk_insert_responses(responses: List[Dict]) -> int:
    """
    Bulk insert responses into janina_responses table.
    Returns number of rows inserted.
    """
    if not responses:
        logger.warning("No responses to insert")
        return 0
    
    sql = """
        INSERT INTO janina_responses
            (category, query_type, keywords, response_text, quality_score, active)
        VALUES
            (%s, %s, %s, %s, %s, TRUE)
    """
    
    inserted = 0
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                for resp in responses:
                    try:
                        cur.execute(
                            sql,
                            (
                                resp['category'],
                                resp.get('query_type', 'general'),
                                resp.get('keywords', []),
                                resp['response_text'],
                                resp.get('quality_score', 0.0),
                            )
                        )
                        inserted += 1
                    except Exception as e:
                        logger.error(f"Failed to insert response: {e}")
                        continue
            conn.commit()
        
        logger.info(f"✓ Successfully inserted {inserted}/{len(responses)} responses")
        return inserted
    
    except Exception as e:
        logger.error(f"Bulk insert failed: {e}")
        return inserted


def validate_responses(responses: List[Dict]) -> bool:
    """Validate response structure before insert."""
    required = ['category', 'response_text']
    
    for i, resp in enumerate(responses):
        missing = [k for k in required if k not in resp or not resp[k]]
        if missing:
            logger.error(f"Response {i} missing fields: {missing}")
            return False
    
    logger.info(f"✓ Validation passed for {len(responses)} responses")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bulk load HR responses into Janina database"
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to responses file (JSON or CSV)'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        help='Force file format (auto-detected from extension if not specified)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate without inserting'
    )
    
    args = parser.parse_args()
    
    # Determine format
    if args.format:
        fmt = args.format
    else:
        ext = os.path.splitext(args.file)[1].lower()
        fmt = 'json' if ext == '.json' else 'csv'
    
    logger.info(f"Loading from {args.file} ({fmt} format)")
    
    # Load responses
    if fmt == 'json':
        responses = load_from_json(args.file)
    else:
        responses = load_from_csv(args.file)
    
    if not responses:
        logger.error("No responses loaded. Exiting.")
        sys.exit(1)
    
    # Validate
    if not validate_responses(responses):
        logger.error("Validation failed. Exiting.")
        sys.exit(1)
    
    if args.dry_run:
        logger.info("DRY RUN: Would insert {len(responses)} responses")
        sys.exit(0)
    
    # Insert
    inserted = bulk_insert_responses(responses)
    
    if inserted == len(responses):
        logger.info("✓ All responses loaded successfully")
        sys.exit(0)
    else:
        logger.warning(f"⚠ Only {inserted}/{len(responses)} responses inserted")
        sys.exit(1)


if __name__ == '__main__':
    main()
