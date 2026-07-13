#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path

from _common import as_list, load_json


REQUIRED_FIELDS = (
    "schema_version", "run_metadata", "fact_cards", "market_snapshot", "desk_briefs", "raw_anomalies", "frontier_questions",
    "trend_observations", "verified_events", "research_candidates", "selected_research_topics",
    "research_reports", "research_audits", "approved_body_claims", "approved_summary_claims",
    "approved_research_claims", "editorial_blueprint", "publication_checks",
)
RENDERER = Path(__file__).resolve().parents[2] / "finance-research-publisher/scripts/render_report_html.py"
_spec = importlib.util.spec_from_file_location("finance_research_renderer_contract", RENDERER)
_renderer = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_renderer)
PUBLIC_SECTIONS = tuple(title for title, _, _ in _renderer.SECTIONS)
FORBIDDEN = (
    "run_bundle", "run bundle", "delivery_status", "sender_body", "final_report", "source_basis",
    "research_candidates", "approved_research_claims", "publication_checks", "unverified", "follow_up",
    "medium/high/low", "warming/cooling/reversal", "脚本名", "命令行参数", "JSON字段",
)
URL_RE = re.compile(r"https?://[^\s)>]+")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def content_checks(bundle: dict, report_path: Path, errors: list[str]) -> None:
    for key in REQUIRED_FIELDS:
        if key not in bundle:
            fail(errors, f"missing bundle field: {key}")
    if bundle.get("schema_version") != 2:
        fail(errors, "schema_version must be 2")
    if len(as_list(bundle.get("selected_research_topics"))) > 3:
        fail(errors, "more than three selected research topics")
    blueprint = bundle.get("editorial_blueprint") or {}
    if len(as_list(blueprint.get("research_notes"))) > 2:
        fail(errors, "more than two public research notes")
    reports = {str(row.get("report_id")): row for row in as_list(bundle.get("research_reports")) if isinstance(row, dict) and row.get("report_id")}
    audits = {str(row.get("report_id")): row for row in as_list(bundle.get("research_audits")) if isinstance(row, dict) and row.get("report_id")}
    if set(reports) != set(audits):
        fail(errors, "every research report must have exactly one matching audit")
    flagship = blueprint.get("flagship")
    if flagship:
        report_id = str(flagship.get("report_id"))
        if report_id not in reports or audits.get(report_id, {}).get("verdict") != "publish_full":
            fail(errors, "flagship is not backed by a publish_full audit")
    for note in as_list(blueprint.get("research_notes")):
        report_id = str(note.get("report_id"))
        if report_id not in reports or audits.get(report_id, {}).get("verdict") not in {"publish_full", "publish_note"}:
            fail(errors, "research note is not backed by an eligible audit")
    summary_ids = [row.get("claim_id") for row in as_list(bundle.get("approved_summary_claims"))]
    compatibility_ids = [row.get("claim_id") for row in as_list(bundle.get("approved_research_claims"))]
    if summary_ids != compatibility_ids:
        fail(errors, "approved_research_claims must exactly alias approved_summary_claims")
    checks = bundle.get("publication_checks") or {}
    if checks.get("market_fresh") is not True and not checks.get("market_closure_reason"):
        fail(errors, "market freshness or closure reason is required")
    if checks.get("publication_eligible") is not True:
        fail(errors, "publication_eligible is not true")

    if not report_path.exists() or report_path.stat().st_size < 500:
        fail(errors, "public report is missing or too short")
        return
    text = report_path.read_text(encoding="utf-8")
    flagship_count = len(re.findall(r"^###\s+旗舰洞悉(?:｜|—|\s|$)", text, flags=re.MULTILINE))
    note_count = len(re.findall(r"^###\s+洞悉短评(?:｜|—|\s|$)", text, flags=re.MULTILINE))
    if flagship_count != (1 if flagship else 0):
        fail(errors, "public flagship count does not match editorial blueprint")
    if note_count != len(as_list(blueprint.get("research_notes"))):
        fail(errors, "public research-note count does not match editorial blueprint")
    headings = re.findall(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)
    positions = []
    for section in PUBLIC_SECTIONS:
        matched = [index for index, heading in enumerate(headings) if heading == section or heading.startswith(section + "｜") or heading.startswith(section + "—")]
        if len(matched) != 1:
            fail(errors, f"public section must appear exactly once: {section}")
        else:
            positions.append(matched[0])
    if len(positions) == len(PUBLIC_SECTIONS) and positions != sorted(positions):
        fail(errors, "public sections are out of canonical order")
    lowered = text.lower()
    for token in FORBIDDEN:
        if token.lower() in lowered:
            fail(errors, f"forbidden implementation label in report: {token}")


def delivery_checks(deploy_path: Path, email_path: Path, errors: list[str]) -> None:
    if not deploy_path.exists():
        fail(errors, "deploy result is missing")
        return
    deploy = load_json(deploy_path)
    url = deploy.get("url")
    if not isinstance(url, str) or not url.startswith("http"):
        fail(errors, "public URL is missing")
    scope = str(deploy.get("access_scope", deploy.get("scope", ""))).lower()
    if scope not in {"all", "public", "internet_public"}:
        fail(errors, "deploy scope is not public")
    if deploy.get("require_login") is not False:
        fail(errors, "public page still requires login")
    verification = deploy.get("verification")
    if not isinstance(verification, dict) or verification.get("ok") is not True:
        fail(errors, "anonymous public URL verification failed")
    if not email_path.exists():
        fail(errors, "email cover is missing")
        return
    email = email_path.read_text(encoding="utf-8")
    urls = URL_RE.findall(email)
    if len(urls) != 1:
        fail(errors, "email must contain exactly one URL")
    elif url and urls[0].rstrip(".,，。") != url.rstrip("/") and urls[0].rstrip(".,，。/") != url.rstrip("/"):
        fail(errors, "email URL does not match deployed URL")
    if ".html" in email.lower() or "attachment" in email.lower() or "附件" in email:
        fail(errors, "email must not mention or attach HTML")
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", email))
    if chinese_chars < 100 or chinese_chars > 380:
        fail(errors, "email cover must stay concise with a 100-300 character lead")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate content or delivery publication gates.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--phase", choices=("content", "delivery", "all"), default="content")
    parser.add_argument("--deploy-json")
    parser.add_argument("--email-md")
    args = parser.parse_args()
    bundle = load_json(args.bundle)
    errors: list[str] = []
    if args.phase in {"content", "all"}:
        content_checks(bundle, Path(args.report), errors)
    if args.phase in {"delivery", "all"}:
        if not args.deploy_json or not args.email_md:
            fail(errors, "delivery phase requires --deploy-json and --email-md")
        else:
            delivery_checks(Path(args.deploy_json), Path(args.email_md), errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: publication gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
