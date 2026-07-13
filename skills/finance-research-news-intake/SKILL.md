---
name: finance-research-news-intake
description: Collect and normalize the latest finance, technology, corporate-strategy, policy, scientific, geopolitical, and socioeconomic developments into source-traceable fact cards, market anomalies, and emerging structural questions for a research-grade Chinese post-close report. Use for 7x24 feeds, primary releases, filings, frontier-company announcements, cross-company strategic patterns, dual-source insight discovery, or a 30-hour evening-report window.
---

# Finance Research News Intake

## Purpose

Build the discovery layer for both the news report and the research track. Treat fast-news feeds as leads, never as final proof. Do not decide the flagship thesis at intake.

## Procedure

1. Run `scripts/fetch_7x24.py --lookback-hours 30 --limit 120 --json` when live Chinese fast news is required.
2. Read `references/sources.md` before choosing feeds, official sources, announcement systems, and search queries.
3. Cover the latest 30 hours by default. Extend to 72 hours only for unresolved events, baselines, or multi-day paths.
4. Collect each important claim from the most primary available source. Preserve the discovery source even after finding a primary source.
5. Normalize useful items as fact cards. Deduplicate only exact same-source repeats; leave event-level cross-source deduplication to `$finance-research-fact-verifier`.
6. Detect anomalies independently from the editorial desks: price/news disagreement, muted reaction to a major headline, reversal, contradictory assets, unusual timing, or a claim that conflicts with the recent baseline.
7. Detect frontier signals even without a price anomaly: several important actors making a similar strategic move; a new technical capability crossing into deployment; a bottleneck changing corporate boundaries; a business model, regulation, standard, demographic pattern, or social behavior beginning to reshape incentives.
8. Group frontier signals by structural pattern, not keyword alone. A single press release remains a fact card or watch item unless the mechanism and external relevance are independently supported.
9. Emit only evidence-backed anomaly observations and candidate questions. Do not convert co-movement, corporate intent, or an evocative future narrative into causality.
10. Record failed sources in `collection_errors`; never silently reduce coverage.

## v2 Outputs

Write or merge these fields in the current `run_bundle.json`:

- `schema_version`: `2`.
- `news_collection`: collection window, source coverage, query log, and `collection_errors`.
- `fact_cards`: normalized cards below.
- `raw_anomalies`: anomaly records below.
- `frontier_questions`: emerging structural questions below.

### Fact card

Require:

- `fact_id`, `fact`, `event_time`, `published_time`, and timezone.
- `source_name`, `source_url`, `source_layer`, and `entrypoint`.
- `data`, `entities`, `related_assets`, and optional `tech_subsector`.
- `initial_importance`: `high`, `medium`, or `low`.
- `verification_status`: `primary_confirmed`, `cross_confirmed`, or `unverified`.
- `discovered_by`: feed, query, desk, or agent identifier.

Never overwrite event time with publication time. Keep numbers and units exactly attributable to the cited source.

### Raw anomaly

Require:

- `candidate_id`, `research_question`, and `origin: raw_anomaly`.
- `question_type: market_anomaly`, `observable_trigger`, `structural_tension`, at least three `required_lenses`, `analysis_horizons`, and `impact_map`.
- `title`, `observed_pattern`, and `comparison_baseline`.
- `seed_fact_ids` and `affected_assets`.
- `why_unusual` and at least two `competing_hypotheses` when possible.
- distinct `evidence_types`, a `source_pair` array, and a concrete `benchmark_plan`.
- `evidence_gaps`, `confirmation_signals`, and `falsification_signals`.
- a stable `overlap_key` for materially equivalent causal questions.
- `verification_status`: normally `pending` until verifier review.

Use this canonical candidate DTO for both news and market anomalies. At intake, keep `source_pair` empty unless independence has already been established and set `base_verified: false`; only `$finance-research-fact-verifier` may atomically replace those fields after verification.

An anomaly is eligible for the research candidate pool only if it states an observable contrast. “Topic is important” is not an anomaly.

### Frontier question

Use the canonical candidate DTO with `origin: frontier_question`. Require:

- a concrete `observable_trigger` supported by at least two independent source families or multiple independently acting entities;
- `question_type`, `structural_tension`, at least three `required_lenses`, `analysis_horizons`, and an `impact_map`;
- a question that moves from the event to a general mechanism and back to concrete economic consequences;
- at least two competing explanations, including an implementation-gap or option-value explanation where relevant;
- evidence, benchmark, confirmation, and falsification plans appropriate to the topic's horizon.

Example pattern: Meta, OpenAI, and other model or cloud companies pursuing proprietary AI silicon may generate a question about compute vertical integration, hardware-model co-design, bargaining power, supply assurance, and value migration across accelerator vendors, foundries, packaging, memory, energy infrastructure, and AI application costs. Do not encode the answer “self-designed chips are inevitable” in the assignment.

## Handoffs

- Route company and stock-tag facts to `$finance-research-stock-analyst`.
- Route technology facts to `$finance-research-tech-analyst`.
- Route all cards and anomalies to `$finance-research-fact-verifier`.
- Allow the topic selector to consume `raw_anomalies` only after verifier reweighting.

## Guardrails

- Require an official source or two independent reliable sources for major non-official claims before publication.
- Keep rumors, broker-channel checks, and reposts explicitly unverified.
- Preserve contradictory versions as separate cards linked by the same event key.
- Do not include investment instructions or personalized recommendations.
