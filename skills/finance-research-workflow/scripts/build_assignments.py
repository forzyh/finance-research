#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _common import as_list, load_json, now_iso, safe_id, save_json


def card_id(card: dict) -> str:
    return str(card.get("id") or card.get("fact_id") or card.get("event_id") or "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build isolated deep-research assignment packets.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--minutes", type=int, default=45)
    args = parser.parse_args()

    bundle = load_json(args.bundle)
    selected = as_list(bundle.get("selected_research_topics"))
    if len(selected) > 3:
        raise SystemExit("selected_research_topics exceeds three")
    facts = {card_id(card): card for card in as_list(bundle.get("fact_cards")) if isinstance(card, dict)}
    events = {card_id(card): card for card in as_list(bundle.get("verified_events")) if isinstance(card, dict)}
    deadline = (datetime.now(timezone.utc).astimezone() + timedelta(minutes=args.minutes)).isoformat(timespec="seconds")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    index = []

    for rank, topic in enumerate(selected, start=1):
        topic_id = safe_id(str(topic.get("candidate_id") or topic.get("id") or topic.get("title") or f"topic-{rank}"), f"topic-{rank}")
        report_id = f"report-{topic_id}"
        author_id = f"research-agent-{rank}"
        seed_ids = [str(item) for item in as_list(topic.get("seed_fact_ids"))]
        seed_facts = [facts[item] if item in facts else events[item] for item in seed_ids if item in facts or item in events]
        packet = {
            "assignment_version": 1,
            "topic_id": topic_id,
            "report_id": report_id,
            "author_id": author_id,
            "research_question": topic.get("research_question") or topic.get("title"),
            "topic": topic,
            "observation_cutoff": bundle.get("run_metadata", {}).get("observation_cutoff"),
            "verified_seed_facts": seed_facts,
            "known_conflicts": as_list(topic.get("known_conflicts")),
            "independent_source_pair": as_list(topic.get("source_pair")),
            "required_evidence_types": as_list(topic.get("evidence_types")),
            "required_sections": [
                "研究问题与结论摘要", "数据范围与时间线", "竞争假设", "机制检验",
                "跨资产或产业证据", "历史或横向比较", "反证与局限", "概率性结论", "确认与证伪信号", "来源"
            ],
            "article_length_chinese_chars": {"minimum": 3000, "maximum": 5000},
            "deadline": deadline,
            "created_at": now_iso(),
            "output_contract": {
                "article_markdown": "report.md",
                "structured_report": "report.json",
                "claims": "claims.json",
            },
        }
        topic_dir = out / topic_id
        save_json(topic_dir / "assignment.json", packet)
        index.append({
            "topic_id": topic_id, "report_id": report_id, "author_id": author_id,
            "assignment": str(topic_dir / "assignment.json"), "deadline": deadline,
        })
    save_json(out / "assignments.json", index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
