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
        "question_type": "market_anomaly",
        "observable_trigger": f"{identifier}出现可观察变化",
        "structural_tension": "效率与韧性之间的权衡",
        "required_lenses": ["产业结构", "公司战略", "资本市场"],
        "analysis_horizons": {"near": "一个季度", "medium": "一至三年", "long": "三年以上"},
        "impact_map": ["上游供应商", "平台企业", "终端用户"],
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

    def test_frontier_source_normalizes_as_frontier_question(self):
        bundle = {
            "raw_anomalies": [],
            "frontier_questions": [{
                "candidate_id": "chip-vertical-integration",
                "research_question": "模型企业为何持续进入AI芯片设计？",
                "question_type": "technology_trajectory",
                "observable_trigger": "多家公司公布自研芯片计划",
                "structural_tension": "通用生态效率与垂直控制之间的权衡",
                "required_lenses": ["技术架构", "产业经济", "公司战略"],
                "analysis_horizons": {"near": "一年", "medium": "三年", "long": "五年以上"},
                "impact_map": ["芯片设计", "晶圆代工", "模型企业"],
            }],
            "research_candidates": [],
            "candidate_verification": [],
            "desk_briefs": {},
        }
        rows, errors = normalize_candidates.normalize_bundle_candidates(bundle)
        self.assertEqual(errors, [])
        self.assertEqual(rows[0]["origin"], "frontier_question")

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

    def test_frontier_question_can_pass_without_price_anomaly(self):
        row = candidate(
            "模型企业自研芯片",
            88,
            origin="frontier_question",
            question_type="technology_trajectory",
            research_question="前沿模型企业自研芯片是否反映算力正在成为必须内化的战略控制点？",
            observable_trigger="多家模型与云企业持续公布自研AI芯片、编译器和部署计划",
            structural_tension="通用生态的规模效率与垂直整合的控制力之间的权衡",
            required_lenses=["技术架构", "产业经济", "公司战略", "资本市场"],
            impact_map=["加速器厂商", "晶圆代工", "先进封装", "云平台", "模型开发者"],
        )
        result = select_topics.select([row], 3)
        self.assertEqual(result["selected_research_topics"][0]["candidate_id"], "模型企业自研芯片")

    def test_publication_content_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp) / "report.md"
            report.write_text(
                "# 每日财经晚报\n## 一句话总结\n" + "市场结构分化。" * 80 +
                "\n## 当天大盘行情走势\n## 为什么会这样走\n## 今天重点新闻与热点个股事件\n## 科技股与细分赛道"
                "\n## 商品与期货\n## 世界经济与地缘形势\n## 深度洞悉\n## 明日验证清单与来源\n",
                encoding="utf-8",
            )
            bundle = normalize_bundle.normalize({})
            bundle["publication_checks"] = {"publication_eligible": True, "market_fresh": True, "market_freshness_details": {}}
            errors = []
            validate_publication.content_checks(bundle, report, errors)
            self.assertEqual(errors, [])

    def test_publication_style_gate_rejects_formulaic_ai_prose(self):
        errors = []
        validate_publication.style_checks(
            "在当今瞬息万变的时代，本文将深入探讨人工智能产业。"
            "值得注意的是，行业既有机遇，也有挑战。值得注意的是，未来可期。",
            errors,
        )
        self.assertTrue(any("本文将" in error for error in errors))
        self.assertTrue(any("值得注意的是" in error for error in errors))
        self.assertTrue(any("未来可期" in error for error in errors))

    def test_publication_style_gate_accepts_natural_financial_prose(self):
        errors = []
        validate_publication.style_checks(
            "科技股的卖压在周末冲突前已经出现。地缘风险放大了跌势，却不是起点："
            "科创50在前一个交易日已经反转。眼下缺的是ETF申赎和融资数据，"
            "这些数据将决定仓位解释能否继续成立。",
            errors,
        )
        self.assertEqual(errors, [])
        validate_publication.style_checks("英伟达作为AI芯片供应商，仍控制着通用训练市场的大部分生态。", errors)
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
                "## 深度洞悉\n当日没有达到刊发标准的独立洞悉。\n## 明日验证清单与来源\n### 明日验证清单\n验证。\n### 主要来源\n公开来源。\n",
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

    def test_insight_report_validator_enforces_multi_horizon_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            report_path = Path(temp) / "report.json"
            report = {
                "report_id": "r1", "topic_id": "t1", "author_id": "a1",
                "research_question": "模型企业为何进入AI芯片设计？",
                "question_type": "technology_trajectory",
                "observation_cutoff": "2026-07-14T00:00:00+08:00",
                "article": "洞" * 3000,
                "hypotheses": ["成本与协同", "供应与议价", "战略期权而非替代"],
                "chronology": ["公告", "开发", "部署"],
                "evidence": ["公司披露"], "counterevidence": ["生态与良率约束"],
                "benchmark": "云厂商历史垂直整合",
                "causal_map": ["工作负载→设计→部署→成本"],
                "limitations": ["缺少规模部署数据"],
                "probabilistic_conclusion": "垂直整合更可能先形成议价与补充能力，而非立即全面替代。",
                "abstract_principle": "当通用投入成为核心瓶颈，领先企业会尝试内化关键控制点。",
                "time_horizon_map": {"near": "研发与资本开支", "medium": "部署与单位经济", "long": "行业边界与价值分配"},
                "stakeholder_impact_map": ["加速器厂商", "晶圆代工", "模型企业"],
                "second_order_effects": ["竞争者调整产品与定价"],
                "philosophical_lens": {"principle": "控制与专业化的张力", "empirical_anchor": "自研芯片投入与部署", "limits": "不能由意图推断成功"},
                "confirmation_signals": ["规模部署与单位成本披露"],
                "falsification_signals": ["项目停滞或经济性持续不达标"],
                "claims": [{
                    "claim_id": "c1", "text": "多家公司正在投入自研AI芯片。", "claim_type": "fact", "material": True,
                    "source_ids": ["s1", "s2"], "supporting_evidence_ids": ["e1"], "counterevidence_ids": [],
                    "uncertainty_or_limit": "投入不等于规模成功", "summary_candidate": True,
                }],
                "sources": [{"source_id": "s1"}, {"source_id": "s2"}],
            }
            report_path.write_text(json.dumps(report), encoding="utf-8")
            validator = ROOT / "skills/finance-research-deep-dive/scripts/validate_research_report.py"
            passed = subprocess.run([sys.executable, str(validator), str(report_path)], text=True, capture_output=True)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            del report["philosophical_lens"]
            report_path.write_text(json.dumps(report), encoding="utf-8")
            blocked = subprocess.run([sys.executable, str(validator), str(report_path)], text=True, capture_output=True)
            self.assertNotEqual(blocked.returncode, 0)

    def test_causal_audit_validator_requires_style_pass_for_public_article(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report_path = root / "report.json"
            audit_path = root / "audit.json"
            report_path.write_text(json.dumps({
                "report_id": "r1", "topic_id": "t1", "author_id": "author-1",
                "claims": [{"claim_id": "c1", "material": True}],
            }), encoding="utf-8")
            audit = {
                "report_id": "r1", "topic_id": "t1", "author_id": "author-1", "reviewer_id": "reviewer-1",
                "verdict": "publish_note", "publication_quality_score": 82,
                "claim_reviews": [{
                    "claim_id": "c1", "conclusion": "approved", "summary_eligible": False,
                    "layers": {layer: {"result": "pass", "notes": "已核验"} for layer in ("L1", "L2", "L3", "L4")},
                }],
                "approved_claim_ids": ["c1"], "rejected_claim_ids": [],
                "factual_conflicts": [], "causal_weaknesses": [], "required_edits": [],
                "public_safe_abstract": "已核验摘要。", "abstract_claim_ids": [], "summary_claim_ids": [],
                "style_review": {
                    "verdict": "pass", "formulaic_phrases": [], "voice_issues": [],
                    "required_rewrites": [], "preserves_claim_scope": True,
                },
            }
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            validator = ROOT / "skills/finance-research-causal-reviewer/scripts/validate_audit.py"
            passed = subprocess.run(
                [sys.executable, str(validator), str(audit_path), "--report", str(report_path)],
                text=True, capture_output=True,
            )
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            audit["style_review"]["verdict"] = "revise"
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            blocked = subprocess.run(
                [sys.executable, str(validator), str(audit_path), "--report", str(report_path)],
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
                    "style_review": {
                        "verdict": "pass", "formulaic_phrases": [], "voice_issues": [],
                        "required_rewrites": [], "preserves_claim_scope": True,
                    },
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

    def test_public_research_requires_passed_style_review(self):
        report = {
            "report_id": "r1", "topic_id": "t1", "author_id": "author-1",
            "claims": [{"claim_id": "c1", "text": "结论", "material": True}],
        }
        audit = {
            "report_id": "r1", "topic_id": "t1", "author_id": "author-1", "reviewer_id": "reviewer-1",
            "verdict": "publish_note",
            "claim_reviews": [{"claim_id": "c1", "conclusion": "approved", "summary_eligible": False}],
            "approved_claim_ids": ["c1"], "summary_claim_ids": [], "abstract_claim_ids": [],
        }
        with self.assertRaises(SystemExit):
            merge_research.audit_report(report, audit)
        audit["style_review"] = {
            "verdict": "pass", "formulaic_phrases": [], "voice_issues": [],
            "required_rewrites": [], "preserves_claim_scope": True,
        }
        body, summary = merge_research.audit_report(report, audit)
        self.assertEqual([row["claim_id"] for row in body], ["c1"])
        self.assertEqual(summary, [])


if __name__ == "__main__":
    unittest.main()
