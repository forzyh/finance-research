#!/usr/bin/env python3
"""Validate a dual-source policy-desk candidate packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED = {
    "id", "title", "research_question", "origin", "seed_fact_ids",
    "evidence_types", "competing_hypotheses", "benchmark_plan",
    "confirmation_signals", "falsification_signals", "observation_cutoff",
    "base_verified", "source_pair", "verified_facts", "policy_stage",
    "novelty_assessment", "implementation_gap", "affected_assets",
    "question_type", "observable_trigger", "structural_tension", "required_lenses",
    "analysis_horizons", "impact_map",
}


def load_json(path: str):
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def nonempty(value) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def validate_source_pair(candidate: dict, prefix: str, errors: list[str]) -> set[str]:
    pair = candidate.get("source_pair", [])
    if not isinstance(pair, list) or len(pair) < 2:
        errors.append(f"{prefix}.source_pair must contain at least two sources")
        return set()
    source_ids, publishers, families = set(), set(), set()
    grades = set()
    for index, source in enumerate(pair):
        sp = f"{prefix}.source_pair[{index}]"
        for field in ("source_id", "publisher", "source_family", "grade", "url", "published_at"):
            if not nonempty(source.get(field)):
                errors.append(f"{sp}.{field} is required")
        source_ids.add(source.get("source_id"))
        publishers.add(source.get("publisher"))
        families.add(source.get("source_family"))
        grades.add(source.get("grade"))
    if len(publishers) < 2 or len(families) < 2:
        errors.append(f"{prefix}.source_pair is not independent")
    if not grades.intersection({"A", "B"}):
        errors.append(f"{prefix}.source_pair requires at least one grade A or B source")
    return {item for item in source_ids if item}


def validate_candidate(candidate: dict, index: int) -> list[str]:
    prefix = f"candidates[{index}]"
    errors = [f"{prefix}.{field} is required" for field in sorted(REQUIRED) if not nonempty(candidate.get(field))]
    if candidate.get("origin") not in {"desk_question", "frontier_question"}:
        errors.append(f"{prefix}.origin must be desk_question or frontier_question")
    if candidate.get("base_verified") is not True:
        errors.append(f"{prefix}.base_verified must be true")
    if len(candidate.get("evidence_types", [])) < 2:
        errors.append(f"{prefix}.evidence_types requires at least two classes")
    if len(candidate.get("competing_hypotheses", [])) < 2:
        errors.append(f"{prefix}.competing_hypotheses requires at least two hypotheses")
    if len(candidate.get("required_lenses", [])) < 3:
        errors.append(f"{prefix}.required_lenses requires at least three lenses")
    source_ids = validate_source_pair(candidate, prefix, errors)
    facts = candidate.get("verified_facts", [])
    fact_ids = set()
    for fact_index, fact in enumerate(facts if isinstance(facts, list) else []):
        fp = f"{prefix}.verified_facts[{fact_index}]"
        fact_ids.add(fact.get("fact_id"))
        cited = set(fact.get("source_ids", []))
        if not nonempty(fact.get("statement")):
            errors.append(f"{fp}.statement is required")
        if fact.get("material", True) and len(cited) < 2:
            errors.append(f"{fp} material fact requires two source_ids")
        if not cited.issubset(source_ids):
            errors.append(f"{fp}.source_ids must refer to source_pair")
    missing_seed = set(candidate.get("seed_fact_ids", [])) - fact_ids
    if missing_seed:
        errors.append(f"{prefix}.seed_fact_ids missing from verified_facts: {sorted(missing_seed)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", help="JSON file path, or - for stdin")
    args = parser.parse_args()
    packet = load_json(args.packet)
    errors = []
    if packet.get("desk") != "policy_news":
        errors.append("desk must be policy_news")
    if not nonempty(packet.get("observation_cutoff")):
        errors.append("observation_cutoff is required")
    candidates = packet.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates must be an array")
        candidates = []
    for index, candidate in enumerate(candidates):
        errors.extend(validate_candidate(candidate, index))
    if not isinstance(packet.get("watchlist", []), list):
        errors.append("watchlist must be an array")
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"valid": True, "candidate_count": len(candidates)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
