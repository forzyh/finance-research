#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or remove finance-research skill symlinks.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--install", action="store_true")
    action.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    destination = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills"
    destination.mkdir(parents=True, exist_ok=True)

    if args.install:
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_pack.py")])
        if result.returncode:
            return result.returncode
        for name in manifest["skills"]:
            source = ROOT / "skills" / name
            target = destination / name
            if target.is_symlink() and target.resolve() == source.resolve():
                print(f"already installed: {name}")
                continue
            if target.exists() or target.is_symlink():
                raise SystemExit(f"refusing to replace existing path: {target}")
            target.symlink_to(source, target_is_directory=True)
            print(f"installed: {target} -> {source}")
    else:
        for name in manifest["skills"]:
            target = destination / name
            source = ROOT / "skills" / name
            if target.is_symlink() and target.resolve() == source.resolve():
                target.unlink()
                print(f"removed: {target}")
            elif target.exists() or target.is_symlink():
                print(f"kept unrelated path: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

