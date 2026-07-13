#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _common import load_json, now_iso, save_json
from validate_publication import content_checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Atomically mark an audited, fresh, validated report eligible for rendering.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    bundle = load_json(args.bundle)
    checks = bundle.setdefault("publication_checks", {})
    if checks.get("market_fresh") is not True and not checks.get("market_closure_reason"):
        raise SystemExit("market freshness or a closure reason is required")
    if bundle.get("run_metadata", {}).get("status") != "research_audited":
        raise SystemExit("research must be audited before content finalization")
    checks.update({
        "publication_eligible": True,
        "content_review_passed": True,
        "content_checked_at": now_iso(),
        "report_path": str(Path(args.report).resolve()),
    })
    errors: list[str] = []
    content_checks(bundle, Path(args.report), errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    bundle.setdefault("run_metadata", {})["status"] = "content_validated"
    save_json(args.output, bundle)
    print("OK: content finalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
