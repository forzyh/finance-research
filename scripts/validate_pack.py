#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"
CHINESE_RE = re.compile(r"[\u3400-\u9fff]")
ENGLISH_HEADINGS = re.compile(
    r"^#{1,6}\s+(?:Purpose|Procedure|Workflow|Inputs?|Outputs?|Required|Guardrails|"
    r"Handoff|Publication|Candidate|Source|Scoring|Pipeline|Timing|Deterministic)",
    re.MULTILINE | re.IGNORECASE,
)


def check_chinese_document(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if not CHINESE_RE.search(text):
        errors.append(f"中文文档缺少中文内容: {path.relative_to(ROOT)}")
    match = ENGLISH_HEADINGS.search(text)
    if match:
        errors.append(
            f"中文文档仍含英文说明标题: {path.relative_to(ROOT)}: {match.group(0)}"
        )


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
        check_chinese_document(skill / "SKILL.md", errors)
        for reference in sorted((skill / "references").glob("*.md")):
            check_chinese_document(reference, errors)
        yaml = skill / "agents/openai.yaml"
        yaml_text = yaml.read_text(encoding="utf-8") if yaml.exists() else ""
        if f"${name}" not in yaml_text:
            errors.append(f"default_prompt does not mention ${name}")
        if not CHINESE_RE.search(yaml_text):
            errors.append(f"Agent 界面提示不是中文: {name}")
        if any(skill.rglob("__pycache__")):
            errors.append(f"generated cache found: {name}")
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors))
        return 1
    print(f"OK: validated {len(manifest['skills'])} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
