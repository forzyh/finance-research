#!/usr/bin/env python3
"""Send a short finance-report cover only after public deployment is verified."""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from urllib.parse import urlparse


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            value = json.load(handle)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError) as error:
        raise SystemExit(f"invalid deployment record: {error}") from error


def valid_url(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def validate_delivery_gate(email_path, deploy_path):
    deploy = read_json(deploy_path)
    url = deploy.get("url", "")
    if not valid_url(url):
        raise SystemExit("deployment record has no valid public URL")
    if deploy.get("access_scope") != "public" or deploy.get("require_login") is not False:
        raise SystemExit("deployment is not internet-public with login disabled")
    verification = deploy.get("verification")
    if not isinstance(verification, dict) or verification.get("ok") is not True:
        raise SystemExit("public no-login URL was not successfully verified")

    try:
        with open(email_path, "r", encoding="utf-8") as handle:
            body = handle.read()
    except OSError as error:
        raise SystemExit(f"could not read email cover: {error}") from error
    urls = re.findall(r"https?://[^\s)>\]]+", body)
    if urls != [url]:
        raise SystemExit("email cover must contain exactly the verified public URL")
    if body.count("## ") > 0 or len(body) > 1800:
        raise SystemExit("email cover is too long; do not send full report sections")
    if re.search(r"(?:\.html\b|/Users/|run[_ ]bundle|final_report|sender_body|delivery_status)", body, flags=re.I):
        raise SystemExit("email cover contains an attachment/path/internal implementation reference")
    return url


def main():
    parser = argparse.ArgumentParser(description="Send a verified short-link finance report cover with sender CLI.")
    parser.add_argument("--email-md", required=True)
    parser.add_argument("--deploy-json", required=True, help="Verified Lark deployment record.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--to")
    parser.add_argument("--from-name", default="每日财经晚报")
    parser.add_argument("--delivery-json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for path in (args.email_md, args.deploy_json):
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise SystemExit(f"missing or empty file: {path}")
    public_url = validate_delivery_gate(args.email_md, args.deploy_json)

    sender = shutil.which("sender")
    if not sender:
        raise SystemExit("sender CLI not found on PATH")
    command = [sender, args.email_md, "-s", args.subject, "--from-name", args.from_name]
    if args.to:
        command.extend(["--to", args.to])

    status = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "public_url": public_url,
        "sent": False,
        "returncode": None,
    }
    if args.dry_run:
        status["dry_run"] = True
        print("delivery gate passed; sender command prepared")
    else:
        process = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status.update({"sent": process.returncode == 0, "returncode": process.returncode})
        if process.stdout:
            print(process.stdout, end="")
        if process.stderr:
            print(process.stderr, end="", file=__import__("sys").stderr)
        if process.returncode != 0:
            raise SystemExit(process.returncode)

    if args.delivery_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.delivery_json)) or ".", exist_ok=True)
        with open(args.delivery_json, "w", encoding="utf-8") as handle:
            json.dump(status, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
