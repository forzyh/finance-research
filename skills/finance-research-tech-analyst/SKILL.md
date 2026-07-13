---
name: finance-research-tech-analyst
description: Analyze cross-market technology risk appetite and technology subsectors after the close, then emit structured desk observations and research-question candidates for the finance-research v2 workflow. Use for AI infrastructure, AI applications and software, semiconductors, internet platforms, consumer electronics, smart vehicles and robotics, communications, optical modules, data centers, power, liquid cooling, cybersecurity, or global-to-China technology transmission.
---

# Finance Research Technology Analyst

## Purpose

Determine which technology lanes received real market and fundamental confirmation, which crowded lanes retreated, and which post-close variables could change the next session. Treat “technology” as a map of distinct chains, not one trade.

## Procedure

1. Read `references/tech-sector-taxonomy.md`.
2. Establish broad risk appetite from STAR 50, ChiNext, Hang Seng Tech, Nasdaq/Nasdaq 100, Philadelphia Semiconductor Index, rates, FX, and representative leaders or ETFs.
3. Classify material facts, stocks, and prices into the defined subsectors.
4. For every active lane, compare driver, market reaction, leading names, peers, laggards, supply-chain evidence, valuation or crowding risk, and post-close disclosures.
5. Distinguish demand evidence, capex, earnings, orders, policy, product cycles, export controls, and rumor-driven moves.
6. Compare A/H/US transmission only after aligning trading sessions and information cutoffs.
7. Mark quiet but important lanes as `no_material_new_signal` rather than inventing breadth.
8. Generate a research candidate only for a material divergence or expectation gap that supports competing hypotheses and a benchmark.

## v2 Outputs

Merge:

- `schema_version`: require `2` and preserve it.
- `tech_sector_observations`: lane-level evidence and status.
- `desk_briefs.technology`: broad risk read, confirmed lanes, retreating lanes, post-close variables, and next checks.
- `research_candidates`: append technology-desk candidates.

### Technology observation

Require:

- `observation_id`, `subsector`, `market_scope`, and `data_cutoff`.
- `headline_read`, `price_action`, `confirmed_driver`, and `source_fact_ids`.
- `leading_names` with role, peer and laggard evidence, and `supply_chain_link`.
- `status`: `strengthening`, `weakening`, `reversal`, `confirmed`, `falsified`, `unchanged`, `no_material_new_signal`, or `insufficient_history`.
- `risk_flags`, `evidence_gaps`, `next_signal`, and `confidence`.

### Desk research candidate

Require `candidate_id`, `origin: desk_question`, `research_question`, `why_now`, `seed_fact_ids`, `anomaly_or_expectation_gap`, `affected_assets`, at least two `competing_hypotheses`, distinct `evidence_types`, a `source_pair` array, `benchmark_plan`, `evidence_gaps`, `confirmation_signals`, `falsification_signals`, and a stable `overlap_key`. Set `verification_status: pending` and `base_verified: false` until `$finance-research-fact-verifier` atomically updates both `base_verified` and `source_pair`.

Do not emit `tech_desk`, `alternative_hypotheses`, `evidence_types_available`, or `desk_briefs.tech_sectors` aliases in new v2 output.

Do not finalize candidate scores or select topics.

## Required Lanes

- AI compute and infrastructure.
- AI applications and software.
- Semiconductor design, foundry, memory, equipment, materials, EDA/IP, and packaging.
- Internet platforms.
- Consumer electronics.
- Smart vehicles and robotics.
- Communications, optical modules, data centers, power, liquid cooling, satellite, and cybersecurity.

## Guardrails

- Require peer, supply-chain, earnings, capex, policy, or product evidence before calling a lane confirmed.
- Treat channel checks, unnamed orders, product leaks, and benchmarks as unverified until supported.
- Separate global duration/risk appetite from China-specific policy and domestic-substitution effects.
- State causality as a tested preference among alternatives, never as certainty from co-movement.
