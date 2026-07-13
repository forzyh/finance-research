#!/usr/bin/env python3
"""Delegate eligibility and scoring to the topic-selector skill's canonical module."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from _common import as_list, load_json, now_iso, save_json


SELECTOR = Path(__file__).resolve().parents[2] / "finance-research-topic-selector/scripts/score_topics.py"
spec = importlib.util.spec_from_file_location("finance_research_score_topics", SELECTOR)
score_topics = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(score_topics)
LIMITS = score_topics.MAXIMA


def select(candidates: list[dict], maximum: int) -> dict:
    eligible, rejected = [], []
    for candidate in candidates:
        item = dict(candidate)
        failures = score_topics.gate_failures(item)
        total, score_errors = score_topics.score(item)
        item["score_total"] = total
        failures.extend(score_errors)
        if total < 70:
            failures.append("score_below_70")
        if failures:
            rejected.append({"candidate_id": item.get("candidate_id"), "score_total": total, "reasons": sorted(set(failures))})
        else:
            eligible.append(item)
    eligible.sort(key=score_topics.rank_key)

    selected, seen_overlap = [], {}
    for item in eligible:
        overlap_key = item.get("overlap_key") or item.get("candidate_id")
        if overlap_key in seen_overlap:
            rejected.append({
                "candidate_id": item.get("candidate_id"), "score_total": item["score_total"],
                "reasons": [f"overlap_with:{seen_overlap[overlap_key]}"],
            })
        elif len(selected) < maximum:
            seen_overlap[overlap_key] = item.get("candidate_id")
            item["selection_rank"] = len(selected) + 1
            selected.append(item)
        else:
            rejected.append({"candidate_id": item.get("candidate_id"), "score_total": item["score_total"], "reasons": ["outside_top_3"]})
    return {
        "selected_research_topics": selected,
        "rejected_candidates": rejected,
        "selected_at": now_iso(),
        "no_selection_reason": "no candidate passed all gates and scored at least 70" if not selected else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select zero to three normalized research topics.")
    parser.add_argument("--input", required=True, help="Canonical candidate list or v2 bundle JSON")
    parser.add_argument("--output", required=True)
    parser.add_argument("--bundle-output")
    parser.add_argument("--max-topics", type=int, default=3, choices=(1, 2, 3))
    args = parser.parse_args()
    source = load_json(args.input)
    candidates = source.get("research_candidates", []) if isinstance(source, dict) else source
    result = select(as_list(candidates), args.max_topics)
    save_json(args.output, result)
    if args.bundle_output:
        if not isinstance(source, dict):
            raise SystemExit("--bundle-output requires bundle input")
        source["selected_research_topics"] = result["selected_research_topics"]
        source.setdefault("run_metadata", {})["topic_selection_at"] = result["selected_at"]
        save_json(args.bundle_output, source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
