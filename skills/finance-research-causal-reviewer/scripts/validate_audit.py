#!/usr/bin/env python3
"""Jointly validate a causal audit against its source research report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VERDICTS = {"publish_full", "publish_note", "summary_only", "reject"}
CONCLUSIONS = {"approved", "qualified", "revise", "rejected"}
LAYER_RESULTS = {"pass", "warn", "fail"}
REQUIRED = {
    "report_id", "topic_id", "author_id", "reviewer_id", "verdict", "claim_reviews",
    "approved_claim_ids", "rejected_claim_ids", "factual_conflicts",
    "causal_weaknesses", "required_edits", "public_safe_abstract",
    "abstract_claim_ids", "summary_claim_ids", "style_review",
}


def load_json(path: str):
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def nonempty(value) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def id_set(value, field: str, errors: list[str]) -> set[str]:
    if not isinstance(value, list):
        errors.append(f"{field} must be an array")
        return set()
    result = set()
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            errors.append(f"{field}[{index}] must be a non-empty string")
            continue
        if item in result:
            errors.append(f"duplicate ID in {field}: {item}")
        result.add(item)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit", help="Audit JSON path, or - for stdin")
    parser.add_argument("--report", required=True, help="Source research report JSON path")
    args = parser.parse_args()
    audit = load_json(args.audit)
    report = load_json(args.report)
    errors = [f"{field} is required" for field in sorted(REQUIRED) if field not in audit]

    for field in ("report_id", "topic_id", "author_id", "reviewer_id"):
        if not isinstance(audit.get(field), str) or not audit.get(field, "").strip():
            errors.append(f"{field} must be a non-empty string")
    for field in ("report_id", "topic_id", "author_id"):
        if not isinstance(report.get(field), str) or not report.get(field, "").strip():
            errors.append(f"report.{field} must be a non-empty string")
        elif audit.get(field) != report.get(field):
            errors.append(f"audit.{field} must exactly match report.{field}")

    if audit.get("author_id") == audit.get("reviewer_id"):
        errors.append("reviewer_id must differ from author_id")
    verdict = audit.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"verdict must be one of {sorted(VERDICTS)}")

    quality_score = audit.get("publication_quality_score")
    valid_quality_score = (
        isinstance(quality_score, (int, float))
        and not isinstance(quality_score, bool)
        and 0 <= quality_score <= 100
    )
    if verdict != "reject" and not valid_quality_score:
        errors.append("non-reject verdict requires publication_quality_score from 0 to 100")
    if verdict == "reject" and quality_score is not None and not valid_quality_score:
        errors.append("publication_quality_score must be from 0 to 100 when present")

    style_review = audit.get("style_review")
    if not isinstance(style_review, dict):
        errors.append("style_review must be an object")
        style_review = {}
    style_verdict = style_review.get("verdict")
    if style_verdict not in {"pass", "revise"}:
        errors.append("style_review.verdict must be pass or revise")
    for field in ("formulaic_phrases", "voice_issues", "required_rewrites"):
        if not isinstance(style_review.get(field), list):
            errors.append(f"style_review.{field} must be an array")
    if style_review.get("preserves_claim_scope") is not True:
        errors.append("style_review.preserves_claim_scope must be true")
    if verdict in {"publish_full", "publish_note"} and style_verdict != "pass":
        errors.append("publish_full and publish_note require style_review.verdict pass")

    report_claim_ids = set()
    material_claim_ids = set()
    report_claims = report.get("claims", [])
    if not isinstance(report_claims, list):
        errors.append("report.claims must be an array")
        report_claims = []
    for index, claim in enumerate(report_claims):
        prefix = f"report.claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{prefix} must be an object")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"{prefix}.claim_id must be a non-empty string")
            continue
        if claim_id in report_claim_ids:
            errors.append(f"duplicate report claim_id: {claim_id}")
        report_claim_ids.add(claim_id)
        if claim.get("material") is True:
            material_claim_ids.add(claim_id)

    conclusions = {}
    summary_eligible = set()
    review_counts = {}
    claim_reviews = audit.get("claim_reviews", [])
    if not isinstance(claim_reviews, list):
        errors.append("claim_reviews must be an array")
        claim_reviews = []
    for index, review in enumerate(claim_reviews):
        prefix = f"claim_reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{prefix} must be an object")
            continue
        claim_id = review.get("claim_id")
        conclusion = review.get("conclusion")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"{prefix}.claim_id must be a non-empty string")
            continue
        review_counts[claim_id] = review_counts.get(claim_id, 0) + 1
        if claim_id in conclusions:
            errors.append(f"duplicate claim review: {claim_id}")
        conclusions[claim_id] = conclusion
        if claim_id not in report_claim_ids:
            errors.append(f"unknown claim review ID: {claim_id}")
        if conclusion not in CONCLUSIONS:
            errors.append(f"{prefix}.conclusion must be one of {sorted(CONCLUSIONS)}")
        layers = review.get("layers", {})
        if not isinstance(layers, dict):
            errors.append(f"{prefix}.layers must be an object")
            layers = {}
        for layer in ("L1", "L2", "L3", "L4"):
            entry = layers.get(layer, {})
            if not isinstance(entry, dict):
                errors.append(f"{prefix}.layers.{layer} must be an object")
                entry = {}
            if entry.get("result") not in LAYER_RESULTS:
                errors.append(f"{prefix}.layers.{layer}.result must be pass, warn, or fail")
            if not entry.get("notes"):
                errors.append(f"{prefix}.layers.{layer}.notes is required")
        if conclusion == "approved" and review.get("summary_eligible") is True:
            summary_eligible.add(claim_id)

    for claim_id in sorted(material_claim_ids):
        count = review_counts.get(claim_id, 0)
        if count != 1:
            errors.append(f"material claim {claim_id} must be reviewed exactly once; found {count}")

    approved = id_set(audit.get("approved_claim_ids"), "approved_claim_ids", errors)
    rejected = id_set(audit.get("rejected_claim_ids"), "rejected_claim_ids", errors)
    summary = id_set(audit.get("summary_claim_ids"), "summary_claim_ids", errors)
    abstract = id_set(audit.get("abstract_claim_ids"), "abstract_claim_ids", errors)

    expected_approved = {claim_id for claim_id, conclusion in conclusions.items() if conclusion == "approved"}
    expected_rejected = {claim_id for claim_id, conclusion in conclusions.items() if conclusion == "rejected"}
    if approved != expected_approved:
        errors.append("approved_claim_ids must exactly match claim reviews concluded approved")
    if rejected != expected_rejected:
        errors.append("rejected_claim_ids must exactly match claim reviews concluded rejected")
    for field, values in (
        ("approved_claim_ids", approved),
        ("rejected_claim_ids", rejected),
        ("summary_claim_ids", summary),
        ("abstract_claim_ids", abstract),
    ):
        unknown = values - report_claim_ids
        if unknown:
            errors.append(f"{field} contains unknown report claim IDs: {sorted(unknown)}")
    releaseable = approved & summary_eligible
    if not summary.issubset(releaseable):
        errors.append("summary_claim_ids may contain only approved and summary-eligible claims")
    if not abstract.issubset(releaseable):
        errors.append("abstract_claim_ids may contain only approved and summary-eligible claims")
    if verdict == "reject" and (summary or abstract):
        errors.append("reject verdict cannot release abstract or summary claims")
    if verdict in {"publish_full", "publish_note", "summary_only"} and not approved:
        errors.append("non-reject verdict requires at least one approved claim")
    if verdict != "reject" and not audit.get("public_safe_abstract"):
        errors.append("non-reject verdict requires public_safe_abstract")

    result = {
        "valid": not errors,
        "verdict": audit.get("verdict"),
        "report_id": audit.get("report_id"),
        "topic_id": audit.get("topic_id"),
        "publication_quality_score": quality_score,
        "material_claim_count": len(material_claim_ids),
        "approved_claim_count": len(approved),
        "summary_claim_count": len(summary),
        "style_verdict": style_verdict,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
