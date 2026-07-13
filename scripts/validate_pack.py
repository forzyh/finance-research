#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    uv = shutil.which("uv")
    if not uv:
        print("ERROR: uv is required to provide the PyYAML validation dependency")
        return 1
    errors = []
    for name in manifest["skills"]:
        skill = ROOT / "skills" / name
        if not skill.exists():
            errors.append(f"missing skill: {name}")
            continue
        result = subprocess.run(
            [uv, "run", "--with", "pyyaml", "python", str(VALIDATOR), str(skill)],
            text=True,
            capture_output=True,
        )
        print(f"[{name}] {result.stdout.strip() or result.stderr.strip()}")
        if result.returncode:
            errors.append(f"validation failed: {name}")
        yaml = skill / "agents/openai.yaml"
        if not yaml.exists() or f"${name}" not in yaml.read_text(encoding="utf-8"):
            errors.append(f"default_prompt does not mention ${name}")
        if any(skill.rglob("__pycache__")):
            errors.append(f"generated cache found: {name}")
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors))
        return 1
    print(f"OK: validated {len(manifest['skills'])} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
