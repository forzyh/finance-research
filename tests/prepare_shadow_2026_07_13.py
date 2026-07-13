#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import importlib.util
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


TOPICS = {
    "technology-unwind": {
        "author_id": "forward-tech",
        "research_question": "2026年7月13日亚洲科技资产下跌，主要应由新地缘冲击、盈利预期恶化，还是此前高换手反弹后的风险释放解释？哪些证据能够区分这些机制？",
        "keywords": ["科创", "创业板", "半导体", "存储", "兆易", "香农", "台积电", "SOXX", "纳斯达克", "NQ", "算力", "科技"],
        "competing_hypotheses": ["新地缘与宏观冲击主导", "科技盈利预期突然恶化", "此前上涨后的估值与拥挤风险释放"],
        "benchmark_plan": "比较7月9日、7月10日与7月13日的A股科技、亚洲半导体、美国股指期货及公司基本面信息时序。",
    },
    "energy-safe-haven": {
        "author_id": "forward-energy",
        "research_question": "冲突消息出现后，原油上涨但从高点回落、黄金与美元没有同步走强，这组跨资产价格应如何解释，哪些结论仍不能由价格推出？",
        "keywords": ["原油", "WTI", "Brent", "布伦特", "黄金", "白银", "美元", "地缘", "冲突", "燃料油", "液化石油气", "LPG", "伊朗"],
        "competing_hypotheses": ["持续实物供应中断风险", "短期事件风险溢价但实物冲击未确认", "利率、汇率或仓位等非地缘因素主导贵金属表现"],
        "benchmark_plan": "比较亚洲早盘与北京时间17时的油价变化，并横向检查黄金、美元、股指期货和国内能化合约。",
    },
    "consumption-policy": {
        "author_id": "forward-policy",
        "research_question": "2030年社会消费品零售总额60万亿元目标提供了多少新增政策信息，其对近期增长和上市公司盈利的传导需要哪些执行条件？",
        "keywords": ["扩大消费", "60万亿", "零售", "消费", "居民", "财政", "人工智能+消费", "2030"],
        "competing_hypotheses": ["目标代表明显新增需求刺激", "目标主要是中期制度锚而非短期增量", "行业机会取决于预算、补贴与地方执行而非总量目标本身"],
        "benchmark_plan": "以官方历史社零基数计算隐含增速，并比较文件发布时间、既有政策表述及预算和执行机制。",
    },
}


def clean(value):
    if isinstance(value, dict):
        blocked = {"interpretation", "analysis_note", "impact_chain", "trend_status", "theme_read", "stock_read"}
        return {key: clean(item) for key, item in value.items() if key not in blocked}
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value


def source_records(row: dict) -> list[dict]:
    values = []
    for field in ("source", "additional_sources"):
        item = row.get(field)
        if isinstance(item, dict):
            values.append(item)
        elif isinstance(item, list):
            values.extend(entry for entry in item if isinstance(entry, dict))
    normalized = []
    for value in values:
        item = dict(value)
        publisher = item.get("publisher") or item.get("name")
        if not publisher:
            continue
        item["publisher"] = publisher
        item.setdefault("source_family", item.get("grade") or publisher)
        item.setdefault("grade", "B")
        normalized.append(item)
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a sanitized July 13 shadow-test fixture.")
    parser.add_argument(
        "--workspace",
        default=os.environ.get("FINANCE_RESEARCH_WORKSPACE"),
        help="Workspace containing work/finance-evening-report-runs; may also be set with FINANCE_RESEARCH_WORKSPACE.",
    )
    parser.add_argument("--output", default=str(REPO_ROOT / "tests/tmp/shadow-2026-07-13"))
    args = parser.parse_args()
    if not args.workspace:
        parser.error("--workspace or FINANCE_RESEARCH_WORKSPACE is required")
    workspace = Path(args.workspace).expanduser().resolve()
    output_root = Path(args.output).expanduser().resolve()
    source_map = {
        "2026-07-09": workspace / "work/finance-evening-report-runs/2026-07-09/170225/run_bundle.json",
        "2026-07-10": workspace / "work/finance-evening-report-runs/2026-07-10/031712/run_bundle.json",
        "2026-07-13": workspace / "work/finance-evening-report-runs/2026-07-13/run_bundle.json",
    }
    missing = [str(path) for path in source_map.values() if not path.exists()]
    if missing:
        raise SystemExit("missing source bundles:\n" + "\n".join(missing))

    all_rows = []
    for session, path in source_map.items():
        bundle = json.loads(path.read_text(encoding="utf-8"))
        for collection in ("fact_cards", "market_snapshot"):
            for index, row in enumerate(bundle.get(collection, [])):
                if not isinstance(row, dict):
                    continue
                item = clean(row)
                item["shadow_session"] = session
                item["shadow_kind"] = collection
                item.setdefault("id", f"{session}-{collection}-{index}")
                all_rows.append(item)

    output_root.mkdir(parents=True, exist_ok=True)
    canonical_candidates = []
    for topic_id, topic in TOPICS.items():
        selected = []
        for row in all_rows:
            haystack = json.dumps(row, ensure_ascii=False)
            if any(keyword.lower() in haystack.lower() for keyword in topic["keywords"]):
                selected.append(row)
        evidence_sources = []
        seen = set()
        for row in selected:
            for source in source_records(row):
                url = source.get("url")
                if url and url not in seen:
                    seen.add(url)
                    evidence_sources.append(source)
        topic_dir = output_root / topic_id
        topic_dir.mkdir(parents=True, exist_ok=True)
        evidence_path = topic_dir / "evidence.json"
        evidence_path.write_text(json.dumps({"records": selected}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        assignment = {
            "assignment_version": 1,
            "topic_id": topic_id,
            "report_id": f"report-{topic_id}",
            "author_id": topic["author_id"],
            "research_question": topic["research_question"],
            "observation_cutoff": "2026-07-13T17:30:00+08:00",
            "verified_seed_facts_path": str(evidence_path),
            "independent_source_pair": evidence_sources[:4],
            "known_conflicts": [],
            "competing_hypotheses": topic["competing_hypotheses"],
            "required_evidence_types": ["price_path", "primary_or_official_fact", "cross_asset_or_cross_section", "historical_or_base_rate"],
            "benchmark_plan": topic["benchmark_plan"],
            "confirmation_plan": ["给出下一交易日或下一官方数据节点的确认条件"],
            "falsification_plan": ["给出能推翻首选解释的可观察条件"],
            "deadline": "forward-test; no live publication",
            "output_location": str(topic_dir),
            "prohibited_context": ["旧版final_report", "旧版研究文章", "预设首选结论"],
        }
        (topic_dir / "assignment.json").write_text(json.dumps(assignment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        maxima = {
            "market_importance": 20, "anomaly": 15, "evidence_availability": 20,
            "causal_testability": 15, "cross_asset_breadth": 10, "novelty": 10,
            "next_session_falsifiability": 10,
        }
        scores = {key: round(maximum * 0.82, 2) for key, maximum in maxima.items()}
        canonical_candidates.append({
            "candidate_id": topic_id,
            "title": topic["research_question"],
            "research_question": topic["research_question"],
            "origin": "desk_question" if topic_id == "consumption-policy" else "raw_anomaly",
            "seed_fact_ids": [row.get("id") for row in selected[:12]],
            "source_pair": evidence_sources[:4],
            "evidence_types": ["price_path", "primary_or_official_fact", "cross_asset_or_cross_section", "historical_or_base_rate"],
            "competing_hypotheses": topic["competing_hypotheses"],
            "benchmark_plan": topic["benchmark_plan"],
            "confirmation_signals": ["下一验证节点出现与首选机制一致的相对价格或官方数据"],
            "falsification_signals": ["下一验证节点出现与首选机制相反的相对价格或官方数据"],
            "overlap_key": topic_id,
            "base_verified": True,
            "scores": scores,
            "score_rationale": {key: "影子测试中的可审计证据覆盖" for key in maxima},
            "score_total": round(sum(scores.values()), 2),
        })

    normalizer_path = REPO_ROOT / "skills/finance-research-workflow/scripts/normalize_bundle.py"
    common_dir = normalizer_path.parent
    import sys
    sys.path.insert(0, str(common_dir))
    spec = importlib.util.spec_from_file_location("shadow_normalize_bundle", normalizer_path)
    normalizer = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(normalizer)
    source_bundle = json.loads(source_map["2026-07-13"].read_text(encoding="utf-8"))
    shadow_bundle = normalizer.normalize(source_bundle)
    shadow_bundle["research_candidates"] = canonical_candidates
    shadow_bundle["selected_research_topics"] = canonical_candidates
    shadow_bundle["run_metadata"].update({
        "workflow": "finance-research-workflow", "status": "research_complete",
        "observation_cutoff": "2026-07-13T17:30:00+08:00",
    })
    shadow_bundle["publication_checks"] = {
        "publication_eligible": False, "market_fresh": True,
        "market_freshness_details": {"shadow_fixture": True},
    }
    (output_root / "shadow-bundle-base.json").write_text(json.dumps(shadow_bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
