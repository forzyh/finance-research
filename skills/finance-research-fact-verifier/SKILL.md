---
name: finance-research-fact-verifier
description: Deduplicate, cross-verify, rank, and conflict-check finance-research v2 fact cards, market snapshots, desk observations, anomalies, trends, and research candidates before topic selection or publication. Use for source grading, freshness checks, event verification, candidate reweighting or rejection, claim-level provenance, market-reaction checks, and separating facts from causal interpretations.
---

# Finance Research Fact Verifier

## Purpose

Create the shared factual foundation for the news and research tracks. This skill performs the pre-selection gate; it does not replace the later causal review of completed research reports.

## Procedure

1. Read `references/verification-rubric.md`.
2. Group fact cards by event using entity, time, topic, and core claim while retaining all source records.
3. Prefer official, exchange, statistical, company, and primary market sources. Cross-check major non-primary facts with at least two independent reliable sources.
4. Reconcile time, amount, policy wording, entity, unit, price, session, and percentage conflicts. Never hide unresolved differences.
5. Verify snapshot freshness and session labels before using price reaction as evidence.
6. Review stock, technology, trend, policy, and commodity/global desk observations against their referenced fact IDs.
7. Review `raw_anomalies`, `frontier_questions`, and `research_candidates`. For anomalies, confirm the contrast is observable. For frontier questions, confirm the strategic pattern is real, independently sourced, and more than a single company's messaging. In both cases, require distinct alternatives, available evidence, explicit structural tension, and measurable confirmation/falsification signals.
8. Mark each candidate `eligible`, `needs_evidence`, `duplicate`, or `rejected`. Provide reasons; do not choose the final 1–3 topics or assign the 100-point score.
9. Run `python3 scripts/apply_candidate_verification.py --bundle <bundle.json> --results <verification.json> --output <verified-bundle.json>` to atomically update each canonical candidate's `base_verified`, `source_pair`, and `verification_status` together with `candidate_verification`.
10. Score verified events for editorial value and emit a small unresolved watchlist.

## v2 Outputs

Merge:

- `schema_version`: require `2` and preserve it.
- `verified_events`.
- `verified_fact_index`: claim-level provenance keyed by `fact_id` or verified claim ID.
- `candidate_verification`: one result per anomaly or candidate.
- `publication_checks.fact_gate`: pass/fail and blocking conflicts.
- `watchlist`: unresolved but potentially material items.

### Verified event

Require:

- `event_id`, `event`, `verified_fact`, and `event_time`.
- `source_basis`: source IDs, URLs, and grades.
- `conflicts`, `affected_assets`, and optional `tech_subsector`.
- `impact_chain`: clearly labeled interpretation, not fact.
- `market_reaction`: observable prices and aligned time window.
- `trend_status`, `news_value_score` from 1–10, and `confidence`.
- `confirmation_signal` and `falsification_signal`.

### Candidate verification

Require:

- `candidate_id`, `status`, and `decision_reason`.
- `source_pair`: the independently verified source records allowed downstream.
- `verified_seed_fact_ids` and `rejected_seed_fact_ids`.
- `source_grade_summary` and `market_data_freshness`.
- `observable_trigger`: true or false; an eligible frontier question need not contain a price anomaly.
- `independent_evidence_types`: list of evidence categories.
- `competing_hypotheses_valid`: true or false.
- `benchmark_feasible`, `signals_measurable`, and `overlap_group`.
- `evidence_gaps` and `allowed_claim_scope`.

Candidates cannot be `eligible` unless the core facts pass, the trigger and structural tension are well defined, two independent evidence types are plausible, two competing explanations exist, a benchmark is feasible, and confirmation plus falsification signals are concrete across an appropriate horizon.

Every input candidate must already use the canonical fields, including `origin: raw_anomaly`, `desk_question`, or `frontier_question`; `question_type`; `observable_trigger`; `structural_tension`; `required_lenses`; `analysis_horizons`; and `impact_map`. For `eligible`, atomically set `base_verified: true`, replace `source_pair` with the verified independent pair, and set `verification_status: eligible`. For every other status, atomically set `base_verified: false` and retain only source records that passed verification. Never update `base_verified` without updating `source_pair` in the same write.

## Source and Confidence Rules

- High: primary source, or multiple reliable independent sources that agree.
- Medium: one reliable source plus consistent data, or two matching non-primary sources.
- Low: fast-news-only, social-only, unclear attribution, stale price, or unresolved material conflict.

## Guardrails

- Do not upgrade a fast-news lead merely because multiple feeds copied the same origin.
- Do not use a trend observation or desk interpretation as standalone factual proof.
- Do not claim a news item drove price without aligned timing and discriminating evidence.
- Reject or narrow claims when units, baselines, restatements, or session cutoffs are ambiguous.
- Keep internal verification labels out of the public report; downstream editors translate approved facts into reader-facing language.
