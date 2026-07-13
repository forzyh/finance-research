#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/finance-research-workflow/scripts"
sys.path.insert(0, str(SCRIPTS))


def module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    value = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(value)
    return value


normalize_bundle = module("normalize_bundle")
normalize_candidates = module("normalize_candidates")
select_topics = module("select_topics")
validate_publication = module("validate_publication")
merge_research = module("merge_research")


def candidate(identifier: str, score: int = 80, **extra):
    limits = select_topics.LIMITS
    ratio = score / 100
    scores = {key: maximum * ratio for key, maximum in limits.items()}
    row = {
        "candidate_id": identifier,
        "title": identifier,
        "research_question": f"为什么{identifier}出现异常定价？",
        "origin": "raw_anomaly",
        "base_verified": True,
        "source_pair": [
            {"publisher": "官方来源", "source_family": "official", "grade": "A"},
            {"publisher": "独立媒体", "source_family": "mainstream", "grade": "B"},
        ],
        "evidence_types": ["price", "official"],
        "competing_hypotheses": ["假设一", "假设二"],
        "benchmark_plan": "比较过去三次类似时段",
        "confirmation_signals": ["次日价差扩大"],
        "falsification_signals": ["次日价差收敛"],
        "overlap_key": identifier,
        "scores": scores,
        "score_rationale": {key: "有可审计证据" for key in limits},
    }
    row.update(extra)
    return row


class WorkflowTests(unittest.TestCase):
    def test_candidate_aliases_normalize_to_canonical_dto(self):
        bundle = {
            "raw_anomalies": [{
                "anomaly_id": "a-1", "candidate_question": "油价与黄金为何背离？",
                "origin": "raw_market", "evidence_types_available": ["price", "news"],
                "alternative_explanations": ["供应风险", "仓位因素"],
                "benchmark_plan": "比较历史冲突日", "confirmation_signals": ["曲线走强"],
                "falsification_signals": ["油价回吐"], "source_pair": [
                    {"publisher": "A", "source_family": "official", "grade": "A"},
                    {"publisher": "B", "source_family": "media", "grade": "B"},
                ],
            }],
            "research_candidates": [],
            "candidate_verification": [{"candidate_id": "a-1", "base_verified": True}],
            "desk_briefs": {},
        }
        rows, errors = normalize_candidates.normalize_bundle_candidates(bundle)
        self.assertEqual(errors, [])
        self.assertEqual(rows[0]["candidate_id"], "a-1")
        self.assertEqual(rows[0]["origin"], "raw_anomaly")
        self.assertTrue(rows[0]["base_verified"])
        self.assertEqual(rows[0]["competing_hypotheses"], ["供应风险", "仓位因素"])

    def test_normalize_legacy_bundle(self):
        old = {"fact_cards": [{"id": "f1"}], "market_snapshot": [{"asset": "上证"}], "stock_observations": [{"stock": "甲"}]}
        new = normalize_bundle.normalize(old)
        self.assertEqual(new["schema_version"], 2)
        self.assertEqual(new["desk_briefs"]["stock_events"][0]["stock"], "甲")
        self.assertEqual(new["market_snapshot"]["snapshot_cards"][0]["asset"], "上证")
        self.assertEqual(new["research_reports"], [])

    def test_selection_threshold_and_overlap(self):
        rows = [
            candidate("科技回撤", 92, overlap_key="tech"),
            candidate("芯片回撤", 88, overlap_key="tech"),
            candidate("油金背离", 84),
            candidate("低质量", 60),
        ]
        result = select_topics.select(rows, 3)
        self.assertEqual([row["candidate_id"] for row in result["selected_research_topics"]], ["科技回撤", "油金背离"])
        rejected = {row["candidate_id"]: row["reasons"] for row in result["rejected_candidates"]}
        self.assertIn("overlap_with:科技回撤", rejected["芯片回撤"])
        self.assertIn("score_below_70", rejected["低质量"])

    def test_zero_topic_is_valid(self):
        result = select_topics.select([candidate("不足", 40)], 3)
        self.assertEqual(result["selected_research_topics"], [])

    def test_publication_content_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp) / "report.md"
            report.write_text(
                "# 每日财经晚报\n## 一句话总结\n" + "市场结构分化。" * 80 +
                "\n## 当天大盘行情走势\n## 为什么会这样走\n## 今天重点新闻与热点个股事件\n## 科技股与细分赛道"
                "\n## 商品与期货\n## 世界经济与地缘形势\n## 核心深挖\n## 明日验证清单与来源\n",
                encoding="utf-8",
            )
            bundle = normalize_bundle.normalize({})
            bundle["publication_checks"] = {"publication_eligible": True, "market_fresh": True, "market_freshness_details": {}}
            errors = []
            validate_publication.content_checks(bundle, report, errors)
            self.assertEqual(errors, [])

    def test_renderer_requires_v2_bundle_and_explicit_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = root / "report.md"
            bundle_path = root / "bundle.json"
            html = root / "report.html"
            report.write_text(
                "# 每日财经晚报｜测试\n\n- 日期：中国时间 2026-07-13\n- 市场状态：交易日\n- 观察窗口：收盘后\n\n"
                "## 一句话总结\n市场分化。\n## 当天大盘行情走势\nA股收盘。\n## 为什么会这样走\n"
                "### 原因一｜风险偏好\n风险偏好变化。\n## 今天重点新闻与热点个股事件\n新闻。\n"
                "## 科技股与细分赛道\n科技。\n## 商品与期货\n商品。\n## 世界经济与地缘形势\n全球。\n"
                "## 核心深挖\n当日没有达到刊发标准的独立研究。\n## 明日验证清单与来源\n### 明日验证清单\n验证。\n### 主要来源\n公开来源。\n",
                encoding="utf-8",
            )
            bundle = normalize_bundle.normalize({})
            bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
            renderer = ROOT / "skills/finance-research-publisher/scripts/render_report_html.py"
            preview = subprocess.run(
                [sys.executable, str(renderer), "--input", str(report), "--bundle", str(bundle_path), "--output", str(html), "--preview"],
                text=True, capture_output=True,
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            blocked = subprocess.run(
                [sys.executable, str(renderer), "--input", str(report), "--bundle", str(bundle_path), "--output", str(html)],
                text=True, capture_output=True,
            )
            self.assertNotEqual(blocked.returncode, 0)

    def test_delivery_gate_requires_public_single_url(self):
        with tempfile.TemporaryDirectory() as temp:
            deploy = Path(temp) / "deploy.json"
            email = Path(temp) / "email.md"
            deploy.write_text(json.dumps({
                "url": "https://example.com/report", "access_scope": "public", "require_login": False,
                "verification": {"ok": True, "status": 200}
            }), encoding="utf-8")
            email.write_text(
                "# 每日财经晚报\n\n" + "今日市场结构分化，研究部分重点解释价格与事实之间的差异，并列出下一交易日可以验证或证伪的信号。" * 3 +
                "\n\nhttps://example.com/report\n",
                encoding="utf-8",
            )
            errors = []
            validate_publication.delivery_checks(deploy, email, errors)
            self.assertEqual(errors, [])

    def test_merge_uses_summary_eligible_claims_and_one_flagship(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            bundle = normalize_bundle.normalize({})
            bundle_path = base / "bundle.json"
            bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
            reports = base / "reports"
            audits = base / "audits"
            for topic, score in (("t1", 95), ("t2", 88)):
                (reports / topic).mkdir(parents=True)
                (audits / topic).mkdir(parents=True)
                report = {
                    "report_id": topic, "topic_id": topic, "author_id": f"author-{topic}",
                    "research_question": topic, "title": topic, "article": "正文", "sources": [],
                    "claims": [
                        {"claim_id": f"{topic}-summary", "text": "摘要结论", "claim_type": "inference", "material": True},
                        {"claim_id": f"{topic}-article", "text": "仅正文结论", "claim_type": "inference", "material": True},
                    ],
                }
                audit = {
                    "report_id": topic, "topic_id": topic, "author_id": f"author-{topic}", "reviewer_id": f"reviewer-{topic}",
                    "verdict": "publish_full", "publication_quality_score": score,
                    "claim_reviews": [
                        {"claim_id": f"{topic}-summary", "conclusion": "approved", "summary_eligible": True},
                        {"claim_id": f"{topic}-article", "conclusion": "approved", "summary_eligible": False},
                    ],
                    "approved_claim_ids": [f"{topic}-summary", f"{topic}-article"],
                    "rejected_claim_ids": [],
                    "summary_claim_ids": [f"{topic}-summary"] if topic == "t1" else [],
                    "abstract_claim_ids": [f"{topic}-summary"] if topic == "t1" else [],
                    "public_safe_abstract": "摘要",
                }
                (reports / topic / "report.json").write_text(json.dumps(report), encoding="utf-8")
                (audits / topic / "audit.json").write_text(json.dumps(audit), encoding="utf-8")

            old_argv = sys.argv
            output = base / "out.json"
            try:
                sys.argv = [
                    "merge_research.py", "--bundle", str(bundle_path), "--reports-dir", str(reports),
                    "--audits-dir", str(audits), "--output", str(output),
                ]
                self.assertEqual(merge_research.main(), 0)
            finally:
                sys.argv = old_argv
            merged = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual([row["claim_id"] for row in merged["approved_research_claims"]], ["t1-summary"])
            self.assertEqual(merged["editorial_blueprint"]["flagship"]["topic_id"], "t1")
            self.assertEqual(len(merged["editorial_blueprint"]["research_notes"]), 1)


if __name__ == "__main__":
    unittest.main()
