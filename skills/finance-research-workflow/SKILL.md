---
name: finance-research-workflow
description: Orchestrate a post-close Chinese finance report with a “深度洞悉” track, from broad finance/frontier intake through four analysis desks, three-origin insight selection, one-to-three isolated insight agents, causal and abstraction review, summary backflow, editorial assembly, HTML QA, public Lark publication, and URL-only email delivery. Use for the complete Daily Finance Evening Report workflow, frontier-issue analysis, shadow runs, historical replays, or stage recovery under a 120-minute deadline.
---

# Finance Research Workflow

## Operating contract

Read `references/workflow-contracts.md` before running the pipeline. Use `references/run-bundle-v2.schema.json` when creating or validating a bundle. Keep implementation labels and internal status fields out of public copy.

The workflow owns orchestration and gates. Domain skills own analysis. The publisher owns rendering and delivery. Never let drafting replace a missing research or verification stage.

## Pipeline

1. Create the run directory with `scripts/init_run.py --runs-dir <runs-dir> --date YYYY-MM-DD`.
2. Load one to seven prior bundles. Normalize legacy bundles with `scripts/normalize_bundle.py` before trend comparison.
3. Run `$finance-research-news-intake` and `$finance-research-market-snapshot`. Generate `fact_cards`, `market_snapshot`, `raw_anomalies`, and `frontier_questions`. Frontier discovery includes technology, corporate strategy, institutions, business models, demographics, science, and socioeconomic change, not only priced financial anomalies.
4. Run the four desks in parallel when slots allow: `$finance-research-policy-desk`, `$finance-research-stock-analyst`, `$finance-research-tech-analyst`, and `$finance-research-global-commodities-desk`.
5. Run `$finance-research-trend-analyst` and `$finance-research-fact-verifier`. Base verification may reject or reduce the weight of research candidates.
6. Merge raw anomalies, desk questions, and frontier questions. Run `scripts/normalize_candidates.py`, let `$finance-research-topic-selector` fill the canonical scores and rationales, then run `scripts/select_topics.py`; select zero to three eligible, non-overlapping topics. Never force a topic below the gate or require a same-day price move.
7. Run `scripts/build_assignments.py`. Spawn one isolated insight agent per selected topic. Give each agent only its assignment packet, verified seed facts, observation cutoff, and `$finance-research-deep-dive` (the internal skill ID for 深度洞悉). Do not provide an expected conclusion.
8. Require every insight agent to return a complete internal report and machine-readable claims, including the abstract principle, multi-horizon impact map, value migration, second-order effects, and philosophical limits. Late or incomplete reports cannot become the flagship article.
9. Give each report and its sources to a separate causal-review pass using `$finance-research-causal-reviewer`. New facts, causal claims, abstraction steps, winner/loser implications, and valuation bridges must be approved before entering either the summary or public article.
10. Run `scripts/merge_research.py` to collect audit verdicts and approved claims. Use only `approved_summary_claims` when generating the summary; `approved_research_claims` is a compatibility alias and must be identical.
11. Run `$finance-research-evening-editor`. Publish at most one full “旗舰洞悉” article and two “洞悉短评”; retain the required “深度洞悉” section with a restrained empty state when no report qualifies.
12. Run `scripts/finalize_content.py`, then `scripts/validate_publication.py`. Only then invoke `$finance-research-publisher`. Require an anonymous, no-login public URL before sending the URL-only cover email.

## Timing and degradation

- T+0–15: history, intake, and market snapshot.
- T+15–30: four desks, trend comparison, base verification, and candidate generation.
- T+30–75: one to three research agents.
- T+75–95: causal review, approved-claim backflow, and editing.
- T+95–105: rendering, visual QA, public-access check, and delivery.
- T+120: hard stop. Exclude late reports from publication.

If no topic passes, publish the verified market and news report without a forced flagship. A high-quality frontier topic may remain open across multiple runs; its confirmation window need not be the next session. If critical trading-day closes are stale, mark the run ineligible and do not publish. If public access fails, do not send email.

## Deterministic scripts

- `init_run.py`: create a v2 run and stage directories.
- `normalize_bundle.py`: convert legacy bundles to the v2 envelope without inventing research outputs.
- `normalize_candidates.py`: map every anomaly and desk producer to the single canonical candidate DTO.
- `select_topics.py`: delegate eligibility and scoring rules to the topic-selector module, deduplicate, and select candidates.
- `build_assignments.py`: create isolated research-agent packets.
- `merge_research.py`: apply audit verdicts and build the approved-claim feed.
- `finalize_content.py`: atomically mark only a fresh, audited, public-safe report eligible for rendering.
- `validate_publication.py`: enforce freshness, research provenance, public-copy, and email gates.
