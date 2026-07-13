#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _common import as_list, load_json, now_iso, save_json


VERDICTS = {"publish_full", "publish_note", "summary_only", "reject"}


def load_named(directory: Path, name: str) -> list[dict]:
    rows = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob(f"*/{name}")):
        value = load_json(path)
        if not isinstance(value, dict):
            raise SystemExit(f"{path} must contain an object")
        rows.append(value)
    return rows


def indexed(rows: list[dict], field: str, label: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        identifier = row.get(field)
        if not identifier:
            raise SystemExit(f"{label} is missing {field}")
        identifier = str(identifier)
        if identifier in result:
            raise SystemExit(f"duplicate {label} {field}: {identifier}")
        result[identifier] = row
    return result


def audit_report(report: dict, audit: dict) -> tuple[list[dict], list[dict]]:
    for field in ("report_id", "topic_id", "author_id"):
        if audit.get(field) != report.get(field):
            raise SystemExit(f"audit/report {field} mismatch for {report.get('report_id')}")
    if not audit.get("reviewer_id") or audit.get("reviewer_id") == report.get("author_id"):
        raise SystemExit(f"audit reviewer independence failed for {report.get('report_id')}")
    verdict = audit.get("verdict")
    if verdict not in VERDICTS:
        raise SystemExit(f"invalid audit verdict for {report.get('report_id')}: {verdict}")
    if "summary_claim_ids" not in audit:
        raise SystemExit(f"audit missing summary_claim_ids for {report.get('report_id')}")

    claims = indexed(as_list(report.get("claims")), "claim_id", "claim")
    reviews = indexed(as_list(audit.get("claim_reviews")), "claim_id", "claim review")
    unknown = set(reviews) - set(claims)
    if unknown:
        raise SystemExit(f"audit contains unknown claims for {report.get('report_id')}: {sorted(unknown)}")
    material = {claim_id for claim_id, claim in claims.items() if claim.get("material", True) is True}
    missing = material - set(reviews)
    if missing:
        raise SystemExit(f"material claims were not reviewed for {report.get('report_id')}: {sorted(missing)}")

    approved_ids = {claim_id for claim_id, review in reviews.items() if review.get("conclusion") == "approved"}
    if set(as_list(audit.get("approved_claim_ids"))) != approved_ids:
        raise SystemExit(f"approved_claim_ids mismatch for {report.get('report_id')}")
    summary_eligible = {claim_id for claim_id, review in reviews.items() if review.get("summary_eligible") is True}
    summary_ids = set(as_list(audit.get("summary_claim_ids")))
    abstract_ids = set(as_list(audit.get("abstract_claim_ids")))
    if not summary_ids.issubset(approved_ids & summary_eligible):
        raise SystemExit(f"summary_claim_ids exceed approved summary-eligible claims for {report.get('report_id')}")
    if not abstract_ids.issubset(approved_ids & summary_eligible):
        raise SystemExit(f"abstract_claim_ids exceed approved summary-eligible claims for {report.get('report_id')}")
    if verdict == "reject" and (summary_ids or abstract_ids):
        raise SystemExit(f"rejected report releases public claims: {report.get('report_id')}")

    body_claims = [{**claims[claim_id], "topic_id": report["topic_id"], "report_id": report["report_id"]} for claim_id in sorted(approved_ids)]
    summary_claims = [
        {**claims[claim_id], "topic_id": report["topic_id"], "report_id": report["report_id"], "audit_verdict": verdict}
        for claim_id in sorted(summary_ids)
    ]
    return body_claims, summary_claims


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge independently audited research into a v2 run bundle.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--reports-dir", required=True)
    parser.add_argument("--audits-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    bundle = load_json(args.bundle)
    reports = load_named(Path(args.reports_dir), "report.json")
    audits = load_named(Path(args.audits_dir), "audit.json")
    report_by_id = indexed(reports, "report_id", "report")
    audit_by_id = indexed(audits, "report_id", "audit")
    missing_audits = set(report_by_id) - set(audit_by_id)
    unknown_audits = set(audit_by_id) - set(report_by_id)
    if missing_audits:
        raise SystemExit(f"reports missing audit: {sorted(missing_audits)}")
    if unknown_audits:
        raise SystemExit(f"audits missing report: {sorted(unknown_audits)}")

    body_claims, summary_claims, eligible = [], [], []
    for report_id, report in report_by_id.items():
        audit = audit_by_id[report_id]
        approved_body, approved_summary = audit_report(report, audit)
        body_claims.extend(approved_body)
        summary_claims.extend(approved_summary)
        verdict = audit["verdict"]
        if verdict in {"publish_full", "publish_note"}:
            quality = audit.get("publication_quality_score")
            if not isinstance(quality, (int, float)) or isinstance(quality, bool) or not 0 <= quality <= 100:
                raise SystemExit(f"invalid publication_quality_score for {report_id}")
            eligible.append({
                "report_id": report_id,
                "topic_id": report["topic_id"],
                "verdict": verdict,
                "publication_quality_score": float(quality),
                "title": report.get("title") or report.get("research_question"),
                "article_path": report.get("article_path"),
                "article": report.get("article"),
                "public_abstract": audit.get("public_safe_abstract") or report.get("abstract"),
                "question_type": report.get("question_type"),
                "abstract_principle": report.get("abstract_principle"),
                "time_horizon_map": report.get("time_horizon_map"),
                "stakeholder_impact_map": report.get("stakeholder_impact_map"),
            })

    full = sorted((row for row in eligible if row["verdict"] == "publish_full"), key=lambda row: (-row["publication_quality_score"], row["report_id"]))
    notes = sorted((row for row in eligible if row["verdict"] == "publish_note"), key=lambda row: (-row["publication_quality_score"], row["report_id"]))
    flagship = full[:1]
    demoted = [{**row, "verdict": "publish_note", "demoted_from": "publish_full"} for row in full[1:]]
    public_notes = sorted(demoted + notes, key=lambda row: (-row["publication_quality_score"], row["report_id"]))[:2]

    bundle["research_reports"] = reports
    bundle["research_audits"] = audits
    bundle["approved_body_claims"] = body_claims
    bundle["approved_summary_claims"] = summary_claims
    bundle["approved_research_claims"] = summary_claims
    bundle["editorial_blueprint"] = {
        "flagship": flagship[0] if flagship else None,
        "research_notes": public_notes,
        "summary_claim_ids": [row["claim_id"] for row in summary_claims],
        "insight_thesis_claim_ids": [row["claim_id"] for row in summary_claims],
        "insight_topics": [
            {
                "report_id": row["report_id"],
                "topic_id": row["topic_id"],
                "question_type": row.get("question_type"),
                "abstract_principle": row.get("abstract_principle"),
                "time_horizon_map": row.get("time_horizon_map"),
            }
            for row in eligible
        ],
        "research_merged_at": now_iso(),
    }
    bundle.setdefault("run_metadata", {})["status"] = "research_audited"
    save_json(args.output, bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
