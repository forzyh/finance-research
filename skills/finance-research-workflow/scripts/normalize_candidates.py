#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy

from _common import as_list, load_json, now_iso, safe_id, save_json


ORIGIN_MAP = {
    "raw_anomaly": "raw_anomaly", "raw_news": "raw_anomaly", "raw_market": "raw_anomaly",
    "desk_question": "desk_question", "stock_desk": "desk_question", "tech_desk": "desk_question",
    "trend": "desk_question", "policy_desk": "desk_question", "global_commodities_desk": "desk_question",
    "frontier_question": "frontier_question", "frontier_signal": "frontier_question",
    "strategic_frontier": "frontier_question", "emerging_issue": "frontier_question",
}


def pick(item: dict, *keys, default=None):
    for key in keys:
        value = item.get(key)
        if value not in (None, "", [], {}):
            return value
    return default


def source_pair(item: dict) -> list[dict]:
    direct = as_list(item.get("source_pair"))
    if direct:
        return [row for row in direct if isinstance(row, dict)]
    values = []
    for key in ("sources", "source", "additional_sources", "source_basis"):
        value = item.get(key)
        if isinstance(value, dict):
            values.append(value)
        elif isinstance(value, list):
            values.extend(row for row in value if isinstance(row, dict))
    seen = set()
    result = []
    for row in values:
        identity = row.get("url") or (row.get("publisher"), row.get("title"))
        if identity in seen:
            continue
        seen.add(identity)
        normalized = deepcopy(row)
        normalized.setdefault("publisher", row.get("name"))
        normalized.setdefault("source_family", row.get("source_family") or row.get("grade") or row.get("layer"))
        result.append(normalized)
    return result


def normalize_one(item: dict, verification: dict | None = None, forced_origin: str | None = None) -> tuple[dict | None, list[str]]:
    verification = verification or {}
    raw_id = pick(item, "candidate_id", "id", "anomaly_id", default="")
    question = pick(item, "research_question", "candidate_question", "question", default="")
    errors = []
    if not question:
        errors.append("missing_research_question")
    candidate_id = safe_id(str(raw_id or question), "candidate")
    raw_origin = forced_origin or str(item.get("origin") or item.get("source_origin") or "desk_question")
    origin = ORIGIN_MAP.get(raw_origin)
    if not origin:
        errors.append(f"unsupported_origin:{raw_origin}")
        origin = "desk_question"

    canonical = {
        "candidate_id": candidate_id,
        "research_question": question,
        "title": pick(item, "title", "headline", default=question),
        "origin": origin,
        "source_origin": raw_origin,
        "question_type": pick(item, "question_type", default="market_anomaly" if origin == "raw_anomaly" else "strategic_shift"),
        "observable_trigger": pick(item, "observable_trigger", "observed_pattern", "why_now", default=""),
        "structural_tension": pick(item, "structural_tension", "underlying_tension", default=""),
        "required_lenses": as_list(pick(item, "required_lenses", "analytical_lenses", default=[])),
        "analysis_horizons": deepcopy(pick(item, "analysis_horizons", "time_horizons", default={})),
        "impact_map": as_list(pick(item, "impact_map", "stakeholder_map", "affected_assets", default=[])),
        "seed_fact_ids": as_list(pick(item, "seed_fact_ids", "fact_ids", "evidence_ids", default=[])),
        "source_pair": source_pair(item) or source_pair(verification),
        "evidence_types": as_list(pick(item, "evidence_types", "evidence_types_available", default=[])),
        "competing_hypotheses": as_list(pick(item, "competing_hypotheses", "alternative_hypotheses", "alternative_explanations", default=[])),
        "benchmark_plan": pick(item, "benchmark_plan", "comparison_plan", default=""),
        "confirmation_signals": as_list(pick(item, "confirmation_signals", "confirmation_plan", default=[])),
        "falsification_signals": as_list(pick(item, "falsification_signals", "falsification_plan", default=[])),
        "overlap_key": pick(item, "overlap_key", "overlap_group", default=candidate_id),
        "base_verified": verification.get("base_verified", item.get("base_verified")) is True,
        "scores": deepcopy(item.get("scores") or {}),
        "score_rationale": deepcopy(item.get("score_rationale") or {}),
        "known_conflicts": as_list(pick(verification, "conflicts", default=pick(item, "known_conflicts", "conflicts", default=[]))),
    }
    legacy_score_map = {
        "market_importance": "structural_importance",
        "anomaly": "explanatory_leverage",
        "anomaly_strength": "explanatory_leverage",
        "causal_testability": "mechanism_testability",
        "cross_asset_breadth": "cross_layer_impact",
        "novelty": "historical_comparability",
        "next_session_falsifiability": "future_falsifiability",
    }
    for old, new in legacy_score_map.items():
        if old in canonical["scores"] and new not in canonical["scores"]:
            canonical["scores"][new] = canonical["scores"].pop(old)
    return (canonical if not errors else None), errors


def normalize_bundle_candidates(bundle: dict) -> tuple[list[dict], list[dict]]:
    verification_rows = as_list(bundle.get("candidate_verification"))
    verification = {
        str(row.get("candidate_id") or row.get("id") or row.get("anomaly_id")): row
        for row in verification_rows if isinstance(row, dict)
    }
    inputs = []
    for item in as_list(bundle.get("raw_anomalies")):
        if isinstance(item, dict):
            inputs.append((item, "raw_anomaly"))
    for item in as_list(bundle.get("frontier_questions")):
        if isinstance(item, dict):
            inputs.append((item, "frontier_question"))
    for item in as_list(bundle.get("research_candidates")):
        if isinstance(item, dict):
            inputs.append((item, None))
    for brief in (bundle.get("desk_briefs") or {}).values():
        if isinstance(brief, dict):
            for item in as_list(brief.get("research_candidates")):
                if isinstance(item, dict):
                    inputs.append((item, "desk_question"))
            for item in as_list(brief.get("frontier_questions")):
                if isinstance(item, dict):
                    inputs.append((item, "frontier_question"))

    normalized, errors, seen = [], [], set()
    for item, forced_origin in inputs:
        raw_id = str(item.get("candidate_id") or item.get("id") or item.get("anomaly_id") or "")
        candidate, problems = normalize_one(item, verification.get(raw_id), forced_origin)
        if problems:
            errors.append({"candidate_id": raw_id or None, "errors": problems})
            continue
        assert candidate is not None
        if candidate["candidate_id"] in seen:
            errors.append({"candidate_id": candidate["candidate_id"], "errors": ["duplicate_candidate_id"]})
            continue
        seen.add(candidate["candidate_id"])
        normalized.append(candidate)
    return normalized, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize all candidate producers to the canonical DTO.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bundle-output")
    args = parser.parse_args()
    bundle = load_json(args.bundle)
    candidates, errors = normalize_bundle_candidates(bundle)
    result = {"research_candidates": candidates, "normalization_errors": errors, "normalized_at": now_iso()}
    save_json(args.output, result)
    if args.bundle_output:
        bundle["research_candidates"] = candidates
        bundle.setdefault("run_metadata", {})["candidate_normalization_at"] = result["normalized_at"]
        save_json(args.bundle_output, bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
