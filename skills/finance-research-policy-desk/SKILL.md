---
name: finance-research-policy-desk
description: Research Chinese and global macro policy, regulation, fiscal, monetary, industrial, consumption, health, trade, and geopolitical-policy developments for finance briefings. Use when Codex must turn policy releases and market reactions into independently double-sourced research candidates, quantify policy scale and novelty, distinguish plans from funded implementation, and hand qualified questions to the finance research topic selector.
---

# Finance Research Policy Desk

## Purpose

Produce evidence packets and research questions, not finished commentary. Require two independent sources for every candidate and keep single-source items on a watchlist.

## Required References

Read [references/policy-source-and-analysis-guide.md](references/policy-source-and-analysis-guide.md) before collecting or interpreting policy evidence.

## Workflow

1. Set an explicit observation cutoff and jurisdiction.
2. Start from primary policy texts, regulator releases, budget documents, statistical releases, speeches, or legislative records.
3. Add an independent second source that confirms the material fact or supplies a separately produced implementation or market-reaction check. Do not count syndicated copies, reposts, or two pages from one source family as independent.
4. Separate each item into:
   - announced objective;
   - binding rule or funded instrument;
   - implementation parameter;
   - observed economic or market reaction;
   - unresolved assumption.
5. Quantify scale against a relevant denominator, prior policy, historical baseline, or market consensus. Label estimates and stress tests.
6. Build at least two competing hypotheses and a benchmark plan. Include explicit confirmation and falsification signals.
7. Emit a candidate only after the dual-source and base-verification gates pass. Otherwise place it in `watchlist` with the missing evidence.
8. Run `python3 scripts/validate_desk_packet.py <packet.json>` before handoff.

## Candidate Gate

Every candidate must include the workflow candidate fields plus:

- `observation_cutoff` with timezone;
- `base_verified: true`;
- `source_pair` containing at least two independent source records;
- `verified_facts`, where every material fact cites at least two independent `source_ids`;
- at least two `evidence_types` and two `competing_hypotheses`;
- a quantitative `benchmark_plan`;
- non-empty `confirmation_signals` and `falsification_signals`;
- `policy_stage`, `novelty_assessment`, `implementation_gap`, and `affected_assets`.

Use `origin: desk_question`. Do not assign the 100-point editorial score; `$finance-research-topic-selector` owns scoring and the 70-point threshold.

## Handoff

Write a compact desk packet with `desk`, `observation_cutoff`, `candidates`, and `watchlist`. Preserve source IDs and exact timestamps so later agents can audit claims without reconstructing provenance.

## Guardrails

- Treat a target, plan, consultation, quota, budget authorization, appropriation, tender, and completed spending as different facts.
- Never infer policy strength from headline wording alone.
- Never call a policy new without comparison to prior rules or programs.
- Never infer causality from a same-day market move alone.
- Keep policy facts, quantitative inference, and desk judgment visibly separate.
- Do not publish internal field names or confidence labels in reader-facing copy.

