#!/usr/bin/env python3
"""Atomically apply verification results to canonical v2 research candidates."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


STATUSES = {"eligible", "needs_evidence", "duplicate", "rejected"}
CANONICAL_FIELDS = {
    "candidate_id",
    "research_question",
    "origin",
    "question_type",
    "observable_trigger",
    "structural_tension",
    "required_lenses",
    "analysis_horizons",
    "impact_map",
    "evidence_types",
    "competing_hypotheses",
    "source_pair",
    "benchmark_plan",
    "confirmation_signals",
    "falsification_signals",
    "overlap_key",
}


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json_atomic(path: str, value) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, target)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def result_rows(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("candidate_verification"), list):
        return payload["candidate_verification"]
    raise SystemExit("verification results must be an array or contain candidate_verification")


def independent_source_pair(pair) -> bool:
    if not isinstance(pair, list) or len(pair) < 2:
        return False
    publishers = {row.get("publisher") for row in pair if isinstance(row, dict) and row.get("publisher")}
    families = {row.get("source_family") for row in pair if isinstance(row, dict) and row.get("source_family")}
    grades = {row.get("grade") for row in pair if isinstance(row, dict)}
    return len(publishers) >= 2 and len(families) >= 2 and bool(grades & {"A", "B"})


def validate_candidate(candidate: dict) -> list[str]:
    candidate_id = candidate.get("candidate_id", "<missing>")
    errors = [f"{candidate_id}: missing canonical field {field}" for field in sorted(CANONICAL_FIELDS) if field not in candidate]
    if candidate.get("origin") not in {"raw_anomaly", "desk_question", "frontier_question"}:
        errors.append(f"{candidate_id}: origin must be raw_anomaly, desk_question, or frontier_question")
    return errors


def apply(bundle: dict, results: list[dict]) -> dict:
    if bundle.get("schema_version") != 2:
        raise SystemExit("bundle schema_version must be 2")
    candidates = bundle.get("research_candidates")
    if not isinstance(candidates, list):
        raise SystemExit("research_candidates must be an array")

    candidate_index = {}
    errors = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("research_candidates entries must be objects")
            continue
        errors.extend(validate_candidate(candidate))
        candidate_id = candidate.get("candidate_id")
        if candidate_id in candidate_index:
            errors.append(f"duplicate candidate_id: {candidate_id}")
        candidate_index[candidate_id] = candidate

    verification_index = {}
    for row in results:
        if not isinstance(row, dict):
            errors.append("candidate_verification entries must be objects")
            continue
        candidate_id = row.get("candidate_id")
        status = row.get("status")
        if not candidate_id:
            errors.append("candidate_verification.candidate_id is required")
            continue
        if candidate_id in verification_index:
            errors.append(f"duplicate candidate verification: {candidate_id}")
        if candidate_id not in candidate_index:
            errors.append(f"verification references unknown candidate: {candidate_id}")
        if status not in STATUSES:
            errors.append(f"{candidate_id}: invalid verification status {status}")
        pair = row.get("source_pair", [])
        if not isinstance(pair, list):
            errors.append(f"{candidate_id}: source_pair must be an array")
        if status == "eligible" and not independent_source_pair(pair):
            errors.append(f"{candidate_id}: eligible requires an independent source_pair with an A/B source")
        verification_index[candidate_id] = row

    missing = sorted(set(candidate_index) - set(verification_index))
    if missing:
        errors.append(f"missing candidate verification results: {missing}")
    if errors:
        raise SystemExit("; ".join(errors))

    updated_candidates = []
    for candidate in candidates:
        row = verification_index[candidate["candidate_id"]]
        updated = dict(candidate)
        updated["base_verified"] = row["status"] == "eligible"
        updated["source_pair"] = list(row.get("source_pair", []))
        updated["verification_status"] = row["status"]
        if row.get("overlap_key"):
            updated["overlap_key"] = row["overlap_key"]
        updated_candidates.append(updated)

    output = dict(bundle)
    output["research_candidates"] = updated_candidates
    output["candidate_verification"] = results
    publication_checks = dict(output.get("publication_checks") or {})
    publication_checks["fact_gate"] = {
        "passed": all(row.get("status") in {"eligible", "duplicate", "rejected"} for row in results),
        "blocking_candidate_ids": [
            row.get("candidate_id") for row in results if row.get("status") == "needs_evidence"
        ],
    }
    output["publication_checks"] = publication_checks
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = apply(load_json(args.bundle), result_rows(load_json(args.results)))
    save_json_atomic(args.output, output)
    print(json.dumps({"updated_candidates": len(output["research_candidates"]), "output": str(Path(args.output).resolve())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
