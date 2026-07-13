#!/usr/bin/env python3
"""Validate the structure and 3,000-5,000 character length of a research report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED = {
    "report_id", "topic_id", "author_id", "research_question", "observation_cutoff", "article",
    "hypotheses", "chronology", "evidence", "counterevidence", "benchmark",
    "causal_map", "limitations", "probabilistic_conclusion",
    "question_type", "abstract_principle", "time_horizon_map", "stakeholder_impact_map",
    "second_order_effects", "philosophical_lens",
    "confirmation_signals", "falsification_signals", "claims", "sources",
}


def load_json(path: str):
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def character_equivalents(text: str) -> int:
    cjk = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
    stripped = re.sub(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", " ", text)
    words_and_numbers = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:[.,]\d+)*", stripped))
    return cjk + words_and_numbers


def nonempty(value) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", help="Report JSON path, or - for stdin")
    args = parser.parse_args()
    report = load_json(args.report)
    errors = [f"{field} is required" for field in sorted(REQUIRED) if not nonempty(report.get(field))]
    for field in ("report_id", "topic_id", "author_id"):
        if not isinstance(report.get(field), str) or not report.get(field, "").strip():
            errors.append(f"{field} must be a non-empty string")

    count = character_equivalents(report.get("article", ""))
    if count < 3000 or count > 5000:
        errors.append(f"article length is {count}; required range is 3000-5000")
    if len(report.get("hypotheses", [])) < 3:
        errors.append("hypotheses must contain at least three competing explanations")
    horizons = report.get("time_horizon_map", {})
    if not isinstance(horizons, dict) or not {"near", "medium", "long"}.issubset(horizons):
        errors.append("time_horizon_map must contain near, medium, and long")
    if len(report.get("stakeholder_impact_map", [])) < 2:
        errors.append("stakeholder_impact_map must contain at least two affected actors")
    if len(report.get("second_order_effects", [])) < 1:
        errors.append("second_order_effects cannot be empty")
    lens = report.get("philosophical_lens", {})
    if not isinstance(lens, dict) or not lens.get("principle") or not lens.get("empirical_anchor") or not lens.get("limits"):
        errors.append("philosophical_lens requires principle, empirical_anchor, and limits")
    if len(report.get("confirmation_signals", [])) < 1:
        errors.append("confirmation_signals cannot be empty")
    if len(report.get("falsification_signals", [])) < 1:
        errors.append("falsification_signals cannot be empty")

    source_ids = {source.get("source_id") for source in report.get("sources", []) if source.get("source_id")}
    claim_ids = set()
    for index, claim in enumerate(report.get("claims", [])):
        prefix = f"claims[{index}]"
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"{prefix}.claim_id must be a non-empty string")
        elif claim_id in claim_ids:
            errors.append(f"duplicate claim_id: {claim_id}")
        else:
            claim_ids.add(claim_id)
        if claim.get("claim_type") not in {"fact", "inference", "judgment"}:
            errors.append(f"{prefix}.claim_type must be fact, inference, or judgment")
        if not isinstance(claim.get("material"), bool):
            errors.append(f"{prefix}.material must be true or false")
        if not claim.get("text"):
            errors.append(f"{prefix}.text is required")
        cited = set(claim.get("source_ids", []))
        if not cited.issubset(source_ids):
            errors.append(f"{prefix}.source_ids contain unknown source IDs")
        if claim.get("claim_type") == "fact" and claim.get("material", True) and len(cited) < 2:
            errors.append(f"{prefix} material fact requires two independent source IDs")
        if claim.get("claim_type") == "inference":
            if not claim.get("supporting_evidence_ids"):
                errors.append(f"{prefix} inference requires supporting_evidence_ids")
            if not claim.get("counterevidence_ids"):
                errors.append(f"{prefix} inference requires counterevidence_ids")
        if claim.get("status") == "approved":
            errors.append(f"{prefix} cannot self-approve; causal reviewer owns approval")
        if not claim.get("uncertainty_or_limit"):
            errors.append(f"{prefix}.uncertainty_or_limit is required")

    result = {"valid": not errors, "article_character_equivalents": count, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
