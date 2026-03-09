#!/usr/bin/env python3
"""Backfill prediction_log table from existing seeded/demo tables.

Place this file in the repository and run it to populate the `prediction_log`
table so the model monitoring utilities have data to compute metrics and drift.

Usage:
    python scripts/backfill_prediction_log.py
"""
import sqlite3
import json
import argparse
from datetime import datetime
from pathlib import Path


def find_db_path() -> str:
    # Prefer backend/smartshield.db relative to repo root
    repo_root = Path(__file__).resolve().parents[1]
    candidate = repo_root / "backend" / "smartshield.db"
    if candidate.exists():
        return str(candidate)
    # Fallbacks
    alt = Path("backend") / "smartshield.db"
    return str(alt)


def ensure_prediction_table(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT,
            timestamp DATETIME,
            prediction REAL,
            actual REAL,
            features TEXT,
            metadata TEXT
        )
        """
    )


def backfill_from_delivery_outcomes(cur):
    cur.execute(
        "SELECT delivery_id, estimated_time, actual_time, traffic_level, weather FROM delivery_outcomes"
    )
    rows = cur.fetchall()
    count = 0
    for delivery_id, est, act, traffic, weather in rows:
        try:
            features = {"delivery_id": delivery_id, "traffic_level": traffic, "weather": weather}
            cur.execute(
                """
                INSERT INTO prediction_log (model_name, timestamp, prediction, actual, features, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "time_predictor",
                    datetime.now().isoformat(),
                    float(est) if est is not None else None,
                    float(act) if act is not None else None,
                    json.dumps(features),
                    "{}",
                ),
            )
            count += 1
        except Exception as e:
            print("Skipping delivery", delivery_id, "error:", e)
    return count


def backfill_from_route_segments(cur, fill_missing_actuals: bool = False):
    # Try to include route_id so we can map to delivery_routes or delivery_outcomes
    cur.execute(
        "SELECT id, route_id, safety_score, timestamp, crime_rate, lighting, patrol_frequency, traffic_density FROM route_segments"
    )
    rows = cur.fetchall()
    count = 0
    for rid, route_id, score, ts, crime, lighting, patrol, traffic in rows:
        try:
            # Attempt mapping: delivery_routes.route_id -> use its safety_score as actual
            actual_val = None
            if route_id:
                try:
                    cur.execute("SELECT safety_score FROM delivery_routes WHERE route_id = ? LIMIT 1", (route_id,))
                    row = cur.fetchone()
                    if row and row[0] is not None:
                        actual_val = float(row[0])
                except Exception:
                    actual_val = None

            # If not found, try delivery_outcomes where delivery_id contains route_id
            if actual_val is None and route_id:
                try:
                    cur.execute("SELECT safety_score FROM delivery_outcomes WHERE delivery_id LIKE ? LIMIT 1", (f"%{route_id}%",))
                    row = cur.fetchone()
                    if row and row[0] is not None:
                        actual_val = float(row[0])
                except Exception:
                    actual_val = None

            # If mapping didn't provide actual and user asked to fill missing, use prediction as proxy
            if actual_val is None and fill_missing_actuals and score is not None:
                actual_val = float(score)

            features = {"crime_rate": crime, "lighting": lighting, "patrol_frequency": patrol, "traffic_density": traffic}
            cur.execute(
                """
                INSERT INTO prediction_log (model_name, timestamp, prediction, actual, features, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "safety_model",
                    ts if ts is not None else datetime.now().isoformat(),
                    float(score) if score is not None else None,
                    actual_val,
                    json.dumps(features),
                    "{}",
                ),
            )
            count += 1
        except Exception as e:
            print("Skipping segment", rid, "error:", e)
    return count


def main():
    parser = argparse.ArgumentParser(description='Backfill prediction_log from demo tables')
    parser.add_argument('--fill-missing-actuals', action='store_true', help='If set, use prediction as actual for route_segments when mapping not found')
    args = parser.parse_args()

    db = find_db_path()
    print("Using DB:", db)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    ensure_prediction_table(cur)
    conn.commit()

    print("Backfilling from `delivery_outcomes` -> model: time_predictor")
    c1 = backfill_from_delivery_outcomes(cur)
    conn.commit()
    print(f"Inserted {c1} rows into prediction_log from delivery_outcomes")

    print("Backfilling from `route_segments` -> model: safety_model")
    # Pass flag to allow filling missing actuals when user requests
    c2 = backfill_from_route_segments(cur, fill_missing_actuals=args.fill_missing_actuals)
    conn.commit()
    print(f"Inserted {c2} rows into prediction_log from route_segments")

    conn.close()
    print("Done.")


if __name__ == '__main__':
    main()
