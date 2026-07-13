---
name: finance-research-stock-analyst
description: Analyze information-rich A-share, Hong Kong, US, and global stocks after the close, then convert stock events into verified desk observations and research-question candidates for the finance-research v2 workflow. Use for unusual moves, high turnover, announcements, exchange inquiries, earnings, buybacks, block trades, insider or shareholder changes, leader confirmation, theme diffusion, risk repricing, or speculation retreat.
---

# Finance Research Stock Analyst

## Purpose

Explain what selected stocks reveal about company fundamentals, sector structure, and market expectations. Produce both a concise stock desk and question candidates for deeper research.

## Procedure

1. Read `references/stock-hotspot-rubric.md`.
2. Build candidates from fact cards, top gainers and losers, turnover, announcements, inquiries,龙虎榜, block trades, buybacks, holdings changes, repeated history, and relevant overseas moves.
3. Select 3–8 names or coherent clusters with the highest information value. Do not rank solely by percentage move.
4. Establish the event chronology: when price moved, when information became public, and whether expectations were already visible.
5. Verify the company-level driver with filings, exchange material, company IR, or reliable independent evidence. Keep rumors separate.
6. Compare leaders, peers, laggards, and supply-chain names before classifying sector diffusion.
7. Classify the read as `leader_confirmation`, `theme_diffusion`, `risk_repricing`, `speculation_retreat`, `macro_sensitive`, or `idiosyncratic`.
8. Extract a research question only when the stock evidence exposes a material expectation gap or contradiction that needs hypothesis testing.

## v2 Outputs

Merge:

- `schema_version`: require `2` and preserve it.
- `stock_observations`: 3–8 high-signal observations.
- `desk_briefs.stock_events`: desk-level summary, evidence gaps, and next-session checks.
- `research_candidates`: append stock-desk question candidates.

### Stock observation

Require:

- `observation_id`, `stock`, `ticker`, `market`, and `event_time`.
- `move_or_attention`, `turnover_or_volume`, and timing relative to disclosure.
- `verified_driver`, `source_fact_ids`, and `source_urls`.
- `theme`, optional `tech_subsector`, peer evidence, and supply-chain position.
- `classification`, `stock_read`, `theme_read`, `risk_flags`, and `confidence`.
- `confirmation_signals` and `falsification_signals`.

### Desk research candidate

Require:

- `candidate_id`, `origin: desk_question`, `research_question`, and `why_now`.
- `seed_fact_ids`, `anomaly_or_expectation_gap`, and `affected_assets`.
- `competing_hypotheses`: at least two.
- `evidence_types`: identify distinct types, not just source count.
- `source_pair`, initially empty unless source independence is already established.
- `benchmark_plan`, `evidence_gaps`, `confirmation_signals`, and `falsification_signals`.
- a stable `overlap_key`, `verification_status: pending`, and `base_verified: false`.

Do not emit `stock_desk`, `alternative_hypotheses`, or `evidence_types_available` aliases in new v2 candidates. `$finance-research-fact-verifier` owns the atomic update of `base_verified` and `source_pair`.

Do not assign the final 100-point selection score; `$finance-research-topic-selector` owns scoring after verifier review.

## Handoffs

- Route technology clusters to `$finance-research-tech-analyst`.
- Route observations and candidates to `$finance-research-fact-verifier`.
- Preserve rejected or unresolved names as watch items, not report filler.

## Guardrails

- Do not infer a sector trend from one large move.
- Treat clarification notices, inquiries, abnormal-volatility notices, and selling plans as material counterevidence.
- Separate headline profit growth from recurring profit, cash flow, base effects, and market expectations.
- Avoid buy/sell wording and personalized investment advice.
