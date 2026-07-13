---
name: finance-research-market-snapshot
description: Build a post-close cross-asset and futures snapshot plus observable market-anomaly signals for the finance-research v2 workflow. Use when a Chinese evening report or 深度洞悉 run needs A-share and Hong Kong closes, style and breadth, turnover and flows, Europe early trade, US premarket or futures, rates, FX, commodities, crypto, or Chinese agricultural, black, energy, metals, and precious futures.
---

# Finance Research Market Snapshot

## Purpose

Create a time-consistent closing snapshot that supports the market recap and supplies discriminating evidence for research questions. Separate observed prices from explanations.

## Procedure

1. Read `references/instruments.md` for coverage, symbols, and interpretation checks.
2. Run `scripts/fetch_sina_futures.py --watchlist core --json` for Chinese continuous futures when appropriate; label them as source snapshots, not exchange settlement prices.
3. Capture A-share and Hong Kong closes first: indices, breadth, turnover, style, sector performance, and available flow indicators.
4. Add Europe early trade, US index futures or premarket, rates, FX, oil, gold, silver, copper, iron ore, agricultural futures, and material crypto moves.
5. Timestamp every quote and distinguish `close`, `live`, `delayed`, `stale`, and `missing`.
6. Calculate only transparent comparisons: relative return, spread, reversal from an intraday extreme, breadth divergence, or cross-asset confirmation. Record operands and units.
7. Detect raw market anomalies such as headline-price disagreement, index-versus-breadth divergence, style dislocation, or related assets moving in conflicting directions.
8. Join anomalies to relevant `fact_id` values without asserting that the news caused the move.

## v2 Outputs

Merge these fields into `run_bundle.json`:

- `schema_version`: `2`.
- `market_snapshot`: an object containing `snapshot_cards`, `as_of`, `session_labels`, and coverage metadata.
- `market_comparisons`: reproducible spreads and relative moves.
- `raw_anomalies`: append market-origin records without replacing intake anomalies.
- `publication_checks.market_fresh`: boolean freshness gate.
- `publication_checks.market_freshness_details`: checked sessions, quote cutoffs, and blocking reasons.

### Snapshot card

Require:

- `snapshot_id`, `asset`, `symbol`, `market`, and `session`.
- `price`, `change_absolute`, `change_percent`, `currency`, and `unit` where applicable.
- `quote_time`, `source_name`, `source_url_or_endpoint`, and `data_quality`.
- `observation`: price-only description.
- `possible_context`: optional hypotheses, clearly marked as interpretation.

### Market comparison

Require `comparison_id`, `label`, `left_snapshot_id`, `right_snapshot_id`, formula, value, unit, comparison window, and interpretation limits.

### Market anomaly

Use the canonical candidate DTO: `candidate_id`, `research_question`, `origin: raw_anomaly`, `question_type: market_anomaly`, `observable_trigger`, `structural_tension`, at least three `required_lenses`, `analysis_horizons`, `impact_map`, `evidence_types`, `competing_hypotheses`, `source_pair`, `benchmark_plan`, `confirmation_signals`, `falsification_signals`, and `overlap_key`. Also preserve `title`, `observed_pattern`, `comparison_baseline`, `seed_fact_ids`, `affected_assets`, `why_unusual`, and `evidence_gaps`. Set `verification_status: pending`, `base_verified: false`, and an empty `source_pair` until `$finance-research-fact-verifier` atomically verifies the candidate.

## Required Coverage

- A/H equities: major indices, STAR 50, ChiNext, Hang Seng Tech, breadth, turnover, and material sector/style spreads.
- Technology risk: Nasdaq/Nasdaq 100, Philadelphia Semiconductor Index when available, and representative leaders or ETFs.
- Rates and FX: relevant Chinese yields, US 2Y/10Y, USD/CNY, USD/CNH, and DXY when material.
- Commodities: Brent/WTI, Shanghai crude, gold, silver, copper, iron ore.
- Chinese futures: egg, corn, soymeal, hog, sugar, cotton, rebar, iron ore, copper, gold, and crude; expand to the reference watchlist when active.

## Publication Gate

Block a normal trading-day report when the A-share, Hong Kong, or domestic-futures session is mislabeled, missing, or stale. Record the reason rather than substituting the prior close.

## Guardrails

- Never treat continuous-contract snapshots as official settlement.
- Never claim “priced in,” “safe haven,” “risk-off,” or a causal driver from one asset alone.
- Check at least one alternative asset, timing sequence, and baseline before proposing a research question.
- Keep reader-facing names separate from raw symbols and internal structures.
