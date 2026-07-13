#!/usr/bin/env python3
"""Validate, score, de-duplicate, and select up to three research topics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MAXIMA = {
    "market_importance": 20,
    "anomaly": 15,
    "evidence_availability": 20,
    "causal_testability": 15,
    "cross_asset_breadth": 10,
    "novelty": 10,
    "next_session_falsifiability": 10,
}


def load_json(path: str):
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source_gate(candidate: dict) -> bool:
    pair = candidate.get("source_pair", [])
    if not isinstance(pair, list) or len(pair) < 2:
        return False
    publishers = {source.get("publisher") for source in pair if source.get("publisher")}
    families = {source.get("source_family") for source in pair if source.get("source_family")}
    grades = {source.get("grade") for source in pair}
    return len(publishers) >= 2 and len(families) >= 2 and bool(grades & {"A", "B"})


def gate_failures(candidate: dict) -> list[str]:
    failures = []
    if candidate.get("base_verified") is not True:
        failures.append("base_verification_failed")
    if not source_gate(candidate):
        failures.append("independent_dual_source_failed")
    if candidate.get("origin") not in {"raw_anomaly", "desk_question"}:
        failures.append("invalid_origin")
    if not candidate.get("research_question"):
        failures.append("missing_research_question")
    if len(candidate.get("evidence_types", [])) < 2:
        failures.append("fewer_than_two_evidence_types")
    if len(candidate.get("competing_hypotheses", [])) < 2:
        failures.append("fewer_than_two_competing_hypotheses")
    if not candidate.get("benchmark_plan"):
        failures.append("missing_benchmark")
    if not candidate.get("confirmation_signals"):
        failures.append("missing_confirmation_signals")
    if not candidate.get("falsification_signals"):
        failures.append("missing_falsification_signals")
    return failures


def score(candidate: dict) -> tuple[float, list[str]]:
    scores = candidate.get("scores", {})
    errors = []
    total = 0.0
    for field, maximum in MAXIMA.items():
        value = scores.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"invalid_score:{field}")
            continue
        if value < 0 or value > maximum:
            errors.append(f"out_of_range:{field}:max={maximum}")
            continue
        total += float(value)
    rationale = candidate.get("score_rationale", {})
    for field in MAXIMA:
        if not rationale.get(field):
            errors.append(f"missing_rationale:{field}")
    return total, errors


def rank_key(candidate: dict):
    scores = candidate["scores"]
    return (
        -candidate["score_total"],
        -scores["evidence_availability"],
        -scores["causal_testability"],
        -scores["market_importance"],
        str(candidate.get("candidate_id", "")),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Candidate array/object path, or - for stdin")
    parser.add_argument("--max-topics", type=int, default=3)
    parser.add_argument("--output")
    args = parser.parse_args()
    if not 1 <= args.max_topics <= 3:
        parser.error("--max-topics must be between 1 and 3")

    payload = load_json(args.input)
    candidates = payload.get("candidates", []) if isinstance(payload, dict) else payload
    if not isinstance(candidates, list):
        raise SystemExit("input must be an array or an object with candidates")

    eligible, rejected = [], []
    for candidate in candidates:
        item = dict(candidate)
        failures = gate_failures(item)
        total, score_errors = score(item)
        item["score_total"] = total
        failures.extend(score_errors)
        if total < 70:
            failures.append("score_below_70")
        if failures:
            rejected.append({"candidate_id": item.get("candidate_id"), "score_total": total, "reasons": sorted(set(failures))})
        else:
            eligible.append(item)

    eligible.sort(key=rank_key)
    deduplicated, seen_overlap = [], {}
    for item in eligible:
        overlap = item.get("overlap_key") or item.get("candidate_id")
        if overlap in seen_overlap:
            rejected.append({
                "candidate_id": item.get("candidate_id"),
                "score_total": item["score_total"],
                "reasons": [f"overlap_with:{seen_overlap[overlap]}"],
            })
        else:
            seen_overlap[overlap] = item.get("candidate_id")
            deduplicated.append(item)

    selected = deduplicated[: args.max_topics]
    for item in deduplicated[args.max_topics :]:
        rejected.append({"candidate_id": item.get("candidate_id"), "score_total": item["score_total"], "reasons": ["outside_top_3"]})

    result = {
        "threshold": 70,
        "score_maximum": 100,
        "selected_count": len(selected),
        "selected_research_topics": selected,
        "rejected_candidates": rejected,
        "no_selection_reason": "no candidate passed all gates and scored at least 70" if not selected else None,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
