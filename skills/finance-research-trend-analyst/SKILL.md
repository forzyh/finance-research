---
name: finance-research-trend-analyst
description: Compare a finance-research v2 run with the latest 1–7 historical runs, while reading legacy v1 bundles, to identify path dependence, confirmation, falsification, reversal, price-fact divergence, and research-worthy expectation gaps. Use when a post-close report must answer which prior tracking items were confirmed or disproved and which questions should carry into tomorrow.
---

# Finance Research Trend Analyst

## Purpose

Explain how today's close changes the prior narrative. Supply historical evidence to the news desk and research candidate pool without turning repeated mentions into truth.

## Procedure

1. Read `references/trend-rubric.md`.
2. Accept v2 bundles and legacy bundles. For legacy input, read `fact_cards` or `news_collection.items`, existing snapshot fields, stock/technology observations, trends, verified events, and watchlists when present.
3. Store new bundles under `work/finance-research-runs/YYYY-MM-DD/`; use timestamped subdirectories for same-day reruns.
4. Run `scripts/compare_runs.py --current <bundle> --runs-dir work/finance-research-runs --history 7 --json --bundle-output <updated-bundle>`. Point `--runs-dir` to a legacy run root when importing old history. The script atomically writes `run_comparison` and `desk_briefs.trend.machine_comparison` while preserving existing analyst-authored observations and candidates.
5. Compare the latest 1–3 runs for immediate path and up to 7 runs for weekly context.
6. Test every carried item against current facts and prices. Label confirmed, weakened, reversed, falsified, unchanged, or pending.
7. Detect path dependence: whether today's move began before the newest headline, whether a rebound failed, or whether reaction broadened or narrowed.
8. Generate a candidate question only when history reveals a material contradiction or unresolved mechanism.

## v2 Outputs

Merge:

- `schema_version`: write `2` for normalized output.
- `trend_observations`.
- `run_comparison`: history files, windows, cold-start status, and machine comparisons.
- `desk_briefs.trend`: confirmed, falsified, and carry-forward lists.
- `research_candidates`: append trend-origin candidates when warranted.

### Trend observation

Require:

- `observation_id`, `trend`, and `status`: `strengthening`, `weakening`, `reversal`, `confirmed`, `falsified`, `unchanged`, or `pending`.
- `current_evidence_ids`, `historical_evidence`, and exact comparison window.
- `affected_assets`, `price_or_sentiment_change`, and `path_read`.
- `alternative_explanations`, `confidence`, `confirmation_signal`, and `falsification_signal`.

### Trend research candidate

Use the canonical DTO: `candidate_id`, `origin: desk_question`, `research_question`, `evidence_types`, `competing_hypotheses`, `source_pair`, `benchmark_plan`, `confirmation_signals`, `falsification_signals`, and `overlap_key`. Also preserve `why_now`, `seed_fact_ids`, the historical anomaly or expectation gap, affected assets, and evidence gaps. Set `verification_status: pending`, `base_verified: false`, and an empty `source_pair` until `$finance-research-fact-verifier` performs the atomic verification update.

## Guardrails

- Treat missing history as a cold start.
- Never promote an old unverified claim because it recurs.
- Separate observable sequence from inferred mechanism.
- Do not use mention counts alone as evidence of market importance.
- Make tomorrow's follow-up measurable wherever possible.
