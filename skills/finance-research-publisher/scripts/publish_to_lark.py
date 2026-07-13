#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
from urllib.parse import urlparse


HTML_LIMIT = 10 * 1024 * 1024
TOTAL_LIMIT = 200 * 1024 * 1024


def validate_html_before_publish(html_path):
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    required_markers = ["<!doctype html>", 'id="summary"', 'id="market"', 'id="drivers"',
                        'id="news"', 'id="tech"', 'id="commodities"', 'id="global"',
                        'id="deep"', 'id="tomorrow"', 'class="mobile-nav"']
    missing = [marker for marker in required_markers if marker not in text]
    forbidden = ["run_bundle", "delivery_status", "approved_research_claims", "research_audits", "/Users/"]
    leaked = [marker for marker in forbidden if marker.lower() in text.lower()]
    if missing or leaked:
        details = []
        if missing:
            details.append("missing required report markers: " + ", ".join(missing))
        if leaked:
            details.append("contains internal markers: " + ", ".join(leaked))
        raise SystemExit("refusing to publish invalid finance research HTML (" + "; ".join(details) + ")")


def run_json(cmd, cwd):
    env = os.environ.copy()
    env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"] = "1"
    env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"] = "1"
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}\n{proc.stderr or proc.stdout}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"lark-cli returned non-JSON output: {exc}\n{proc.stdout}\n{proc.stderr}") from exc


def ensure_ok(payload, action):
    if payload.get("ok") is True:
        return payload.get("data") or {}
    error = payload.get("error") or {}
    hint = error.get("hint") or error.get("message") or f"{action} failed"
    raise SystemExit(hint)


def verify_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Codex finance report publisher"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read(2048).decode("utf-8", errors="ignore")
            return {"ok": 200 <= resp.status < 400, "status": resp.status, "sample": body[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Publish a finance report HTML to Lark Miaoda and make it publicly accessible.")
    parser.add_argument("--html", required=True, help="Rendered report.html path.")
    parser.add_argument("--bundle", required=True, help="Finance Research v2 run bundle.")
    parser.add_argument("--report", required=True, help="Publication-ready final report Markdown.")
    parser.add_argument("--app-name", help="Miaoda app name. If omitted, a timestamped name is used.")
    parser.add_argument("--app-id", help="Existing Miaoda app_id to reuse. If omitted, a new HTML app is created.")
    parser.add_argument("--deploy-json", help="Optional JSON output path for deployment status.")
    args = parser.parse_args()

    bundle_path = Path(args.bundle).expanduser().resolve()
    report_path = Path(args.report).expanduser().resolve()
    validator = Path(__file__).resolve().parents[2] / "finance-research-workflow/scripts/validate_publication.py"
    if not validator.exists():
        raise SystemExit("finance-research publication validator not found")
    gate = subprocess.run(
        [sys.executable, str(validator), "--bundle", str(bundle_path), "--report", str(report_path), "--phase", "content"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if gate.returncode != 0:
        raise SystemExit(f"publication content gate failed:\n{gate.stdout}{gate.stderr}")

    html = Path(args.html).expanduser().resolve()
    if not html.exists():
        raise SystemExit(f"missing file: {html}")
    if html.stat().st_size == 0:
        raise SystemExit(f"empty file: {html}")
    if html.suffix.lower() != ".html":
        raise SystemExit(f"--html must point to an .html file: {html}")
    if html.stat().st_size > HTML_LIMIT:
        raise SystemExit(f"HTML file is larger than 10MB: {html.stat().st_size} bytes")
    validate_html_before_publish(html)

    run_dir = html.parent
    publish_dir = run_dir / "lark_publish"
    if publish_dir.exists():
        shutil.rmtree(publish_dir)
    publish_dir.mkdir(parents=True)
    index = publish_dir / "index.html"
    shutil.copy2(html, index)

    total_size = sum(p.stat().st_size for p in publish_dir.rglob("*") if p.is_file())
    if total_size > TOTAL_LIMIT:
        raise SystemExit(f"publish payload is larger than 200MB: {total_size} bytes")

    lark_cli = shutil.which("lark-cli")
    if not lark_cli:
        raise SystemExit("lark-cli not found on PATH")

    app_id = args.app_id
    created_app = False
    if not app_id:
        app_name = args.app_name or f"财经报告 {dt.datetime.now().strftime('%Y-%m-%d %H%M')}"
        created = run_json([lark_cli, "apps", "+create", "--as", "user", "--name", app_name, "--app-type", "html"], cwd=run_dir)
        data = ensure_ok(created, "create app")
        app = data.get("app") or {}
        app_id = app.get("app_id")
        if not app_id:
            raise SystemExit(f"could not find app_id in create response: {created}")
        created_app = True

    rel_index = str(index.relative_to(run_dir))
    published = run_json([lark_cli, "apps", "+html-publish", "--as", "user", "--app-id", app_id, "--path", rel_index], cwd=run_dir)
    data = ensure_ok(published, "publish html")
    url = data.get("url")
    parsed_url = urlparse(url or "")
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise SystemExit(f"could not find url in publish response: {published}")

    scoped = run_json(
        [
            lark_cli,
            "apps",
            "+access-scope-set",
            "--as",
            "user",
            "--app-id",
            app_id,
            "--scope",
            "public",
            "--require-login=false",
        ],
        cwd=run_dir,
    )
    ensure_ok(scoped, "set public access")

    verification = verify_url(url)
    if not verification.get("ok"):
        raise SystemExit(f"public no-login URL verification failed: {verification}")
    result = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "app_id": app_id,
        "created_app": created_app,
        "url": url,
        "access_scope": "public",
        "require_login": False,
        "html": str(html),
        "bundle": str(bundle_path),
        "report": str(report_path),
        "published_entry": str(index),
        "verification": verification,
    }

    if args.deploy_json:
        out = Path(args.deploy_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
