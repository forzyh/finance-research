---
name: finance-research-global-commodities-desk
description: Research global commodities, shipping, physical supply, macro cross-assets, and geopolitical transmission for finance briefings. Use when Codex must explain oil, gold, base metals, ferrous, agriculture, freight, FX, rates, or conflict-driven price anomalies and produce independently double-sourced research candidates with physical-market and cross-asset tests.
---

# Finance Research Global Commodities Desk

## Purpose

Turn commodity and geopolitical anomalies into testable research candidates. Do not treat a price move as proof of supply damage, political intent, or a durable trend.

## Required References

Read [references/commodities-causal-map.md](references/commodities-causal-map.md) before building candidates.

## Workflow

1. Set a timestamped observation cutoff and label every quote as close, intraday, premarket, settlement, indicative, spot, or futures.
2. Establish the event with two independent sources. Treat reposts and syndicated reports as one source family.
3. Check the physical layer: production, exports, vessel traffic, inventories, basis, spot premiums, freight, insurance, refining or processing margins, and curve structure where relevant.
4. Check the financial layer: futures price, volume, open interest, options skew, positioning, FX, rates, inflation expectations, equities, credit, and haven assets.
5. Compare the current path with a historical or same-session benchmark. Avoid cross-source pseudo-precision.
6. State at least two competing hypotheses, including a non-event explanation such as positioning, liquidity, contract mechanics, weather, inventory, or macro rates.
7. Define observable confirmation and falsification signals for the next session.
8. Promote only double-sourced, base-verified packets. Use `frontier_question` for durable changes in trade architecture, resource security, shipping routes, energy systems, or geopolitical economic order that may precede same-day price confirmation. Move unresolved single-source events to `watchlist`.
9. Run `python3 scripts/validate_desk_packet.py <packet.json>` before handoff.

## Candidate Gate

Every candidate must satisfy the shared workflow candidate contract and include:

- `observation_cutoff`, `base_verified: true`, and `origin: desk_question` or `frontier_question`;
- `question_type`, `observable_trigger`, `structural_tension`, at least three `required_lenses`, `analysis_horizons`, and `impact_map`;
- an independent `source_pair` with at least one grade A or B source;
- `verified_facts`, with two source IDs for each material event fact;
- at least two `evidence_types` and two `competing_hypotheses`;
- `market_evidence`, `physical_evidence`, and `cross_asset_checks`;
- a benchmark, confirmation signals, falsification signals, and known data gaps;
- `affected_assets` and explicit contract or instrument identifiers internally.

Do not assign the editorial score. `$finance-research-topic-selector` calculates the 100-point score and enforces the 70-point floor.

## Geopolitical Claims

Separate four layers:

1. verified event chronology;
2. observed market and physical evidence;
3. market-expectation inference;
4. attribution of government or military intent.

Prices may support layer 3 only probabilistically. Require direct official statements, documented negotiations, or independently reported decision evidence for layer 4.

## Handoff

Emit `desk: global_commodities`, `observation_cutoff`, `candidates`, and `watchlist`. Preserve source IDs, quote times, units, currencies, contract months, and comparison bases.

## Guardrails

- Do not call a cross-source snapshot a verified intraday high or low.
- Do not infer physical shortage without physical or curve evidence.
- Do not infer “the market is calm” from gold alone; test rates, dollar, volatility, credit, and other havens.
- Do not infer “talks will resume” or “conflict is limited” from oil and gold prices alone.
- Keep facts, mechanism hypotheses, alternative explanations, and judgments separate.
