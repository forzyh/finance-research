#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from _common import now_iso, save_json


STAGES = (
    "00_intake", "01_market", "02_desks", "03_verification",
    "04_research/assignments", "04_research/reports", "04_research/audits",
    "05_editorial", "06_publish",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Finance Research v2 run directory.")
    parser.add_argument("--runs-dir", required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--force-timestamp", action="store_true")
    args = parser.parse_args()

    base = Path(args.runs_dir).expanduser() / args.date
    if args.force_timestamp or (base.exists() and any(base.iterdir())):
        base = base / datetime.now().strftime("%H%M%S")
    for stage in STAGES:
        (base / stage).mkdir(parents=True, exist_ok=True)

    bundle = {
        "schema_version": 2,
        "run_metadata": {
            "report_date": args.date,
            "created_at": now_iso(),
            "workflow": "finance-research-workflow",
            "status": "collecting",
            "soft_deadline_minutes": 90,
            "hard_deadline_minutes": 120,
        },
        "fact_cards": [],
        "market_snapshot": {"as_of": None, "session_labels": [], "snapshot_cards": []},
        "desk_briefs": {"policy_news": {}, "stock_events": {}, "technology": {}, "global_commodities": {}},
        "raw_anomalies": [],
        "trend_observations": [],
        "verified_events": [],
        "research_candidates": [],
        "selected_research_topics": [],
        "research_reports": [],
        "research_audits": [],
        "approved_body_claims": [],
        "approved_summary_claims": [],
        "approved_research_claims": [],
        "editorial_blueprint": {},
        "publication_checks": {
            "publication_eligible": False,
            "market_fresh": False,
            "market_freshness_details": {},
        },
    }
    save_json(base / "run_bundle.json", bundle)
    print(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
