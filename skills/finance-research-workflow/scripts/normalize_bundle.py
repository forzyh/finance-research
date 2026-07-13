#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy

from _common import as_list, load_json, now_iso, save_json


def normalize(source: dict) -> dict:
    if source.get("schema_version") == 2:
        result = deepcopy(source)
    else:
        result = {
            "schema_version": 2,
            "run_metadata": deepcopy(source.get("run_metadata") or {}),
            "fact_cards": as_list(source.get("fact_cards")),
            "market_snapshot": {
                "as_of": (source.get("run_metadata") or {}).get("observation_cutoff") or source.get("updated_at"),
                "session_labels": [],
                "snapshot_cards": as_list(source.get("market_snapshot")),
            },
            "desk_briefs": {
                "policy_news": deepcopy(source.get("policy_observations") or {}),
                "stock_events": deepcopy(source.get("stock_observations") or {}),
                "technology": deepcopy(source.get("tech_sector_observations") or {}),
                "global_commodities": deepcopy(source.get("global_commodities_observations") or {}),
            },
            "raw_anomalies": as_list(source.get("raw_anomalies")),
            "trend_observations": as_list(source.get("trend_observations")),
            "verified_events": as_list(source.get("verified_events")),
            "research_candidates": as_list(source.get("research_candidates")),
            "selected_research_topics": as_list(source.get("selected_research_topics")),
            "research_reports": as_list(source.get("research_reports")),
            "research_audits": as_list(source.get("research_audits")),
            "approved_body_claims": as_list(source.get("approved_body_claims")),
            "approved_summary_claims": as_list(source.get("approved_summary_claims") or source.get("approved_research_claims")),
            "approved_research_claims": as_list(source.get("approved_research_claims")),
            "editorial_blueprint": deepcopy(source.get("editorial_blueprint") or {}),
            "publication_checks": deepcopy(source.get("publication_checks") or {}),
            "legacy": {
                "final_report_summary": deepcopy(source.get("final_report_summary")),
                "watchlist": deepcopy(source.get("watchlist")),
                "sources_used": deepcopy(source.get("sources_used")),
            },
        }
        result["run_metadata"]["normalized_from_schema"] = source.get("schema_version", 1)
        result["run_metadata"]["normalized_at"] = now_iso()

    result.setdefault("desk_briefs", {})
    if not result["desk_briefs"].get("technology") and result["desk_briefs"].get("tech_sectors"):
        result["desk_briefs"]["technology"] = result["desk_briefs"].pop("tech_sectors")
    for key in ("policy_news", "stock_events", "technology", "global_commodities"):
        result["desk_briefs"].setdefault(key, {})
    if not result.get("approved_summary_claims") and result.get("approved_research_claims"):
        result["approved_summary_claims"] = deepcopy(result["approved_research_claims"])
    for key in (
        "fact_cards", "raw_anomalies", "trend_observations", "verified_events",
        "research_candidates", "selected_research_topics", "research_reports", "research_audits",
        "approved_body_claims", "approved_summary_claims", "approved_research_claims",
    ):
        result[key] = as_list(result.get(key))
    market = result.get("market_snapshot")
    if isinstance(market, list):
        result["market_snapshot"] = {"as_of": None, "session_labels": [], "snapshot_cards": market}
    elif not isinstance(market, dict):
        result["market_snapshot"] = {"as_of": None, "session_labels": [], "snapshot_cards": []}
    else:
        market.setdefault("as_of", None)
        market.setdefault("session_labels", [])
        if "snapshot_cards" not in market:
            market["snapshot_cards"] = as_list(market.get("cards") or market.get("items"))
    result.setdefault("run_metadata", {})
    result.setdefault("editorial_blueprint", {})
    result.setdefault("publication_checks", {})
    checks = result["publication_checks"]
    if "market_fresh" not in checks and "market_freshness" in checks:
        freshness = checks.pop("market_freshness")
        checks["market_fresh"] = freshness if isinstance(freshness, bool) else bool(freshness and freshness.get("ok"))
        checks["market_freshness_details"] = freshness if isinstance(freshness, dict) else {}
    checks.setdefault("market_freshness_details", {})
    checks.setdefault("market_fresh", False)
    checks.setdefault("publication_eligible", False)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize legacy finance bundles to schema v2.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    save_json(args.output, normalize(load_json(args.input)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
