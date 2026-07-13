---
name: finance-research-causal-reviewer
description: Independently audit internal finance research before editorial use. Use when Codex must review source independence, factual and numerical accuracy, timestamp comparability, causal sufficiency, counterevidence, uncertainty, and public wording; issue one of four publication verdicts; and enforce that summaries contain only claims explicitly marked approved.
---

# Finance Research Causal Reviewer

## Purpose

Act as an independent adversarial reviewer. Audit the report claim by claim and prevent plausible narratives from being promoted as verified causality.

## Independence Gate

Do not review a report written by the same agent or role. Require the audit's `report_id`, `topic_id`, and `author_id` to exactly match the report and require a distinct `reviewer_id`. If identity or independence cannot be established, return the report for reassignment without approving claims.

## Required Reference

Read [references/causal-review-rubric.md](references/causal-review-rubric.md) before review.

## Four Review Layers

1. **L1 fact and source:** verify wording, provenance, source independence, conflicts, and freshness.
2. **L2 number, time, and comparability:** recompute material figures; align time zones, sessions, contracts, units, currencies, and revisions.
3. **L3 causality:** test temporal order, mechanism, alternatives, confounders, counterevidence, base rates, and falsifiability.
4. **L4 publication and summary gate:** remove hidden intent, false certainty, internal jargon, and unsupported compression.

Review every material claim at all four layers. Give the claim one conclusion: `approved`, `qualified`, `revise`, or `rejected`.

## Four Audit Verdicts

Issue exactly one overall verdict:

- `publish_full`: the complete flagship deep dive is publishable after listed non-material edits;
- `publish_note`: only a shortened supporting note is publishable;
- `summary_only`: only explicitly approved claims may appear in the summary or brief reasons;
- `reject`: no part may be published from this report.

The overall verdict never automatically approves a claim.

## Summary Hard Gate

Populate both `abstract_claim_ids` and `summary_claim_ids` only from claim reviews whose conclusion is exactly `approved` and `summary_eligible` is true. Never admit `qualified`, `revise`, `rejected`, unresolved, or unreviewed claims into either public surface. The editor may shorten approved text without strengthening it; any material rewrite requires re-review.

## Workflow

1. Rebuild the source-to-claim map without relying on the author’s conclusion.
2. Recompute all thesis-relevant calculations and verify observation cutoffs.
3. Steelman at least one alternative explanation and identify the evidence that would separate it from the preferred thesis.
4. Review every material report claim exactly once through L1–L4 and assign a claim conclusion. Do not introduce unknown claim IDs.
5. Produce approved and rejected claim ID lists, conflicts, causal weaknesses, and required edits.
6. Choose the four-level overall verdict using the rubric.
7. Assign `publication_quality_score` from 0 to 100 for every non-reject verdict using the rubric; do not reuse the topic-selection score.
8. Draft a public-safe abstract using only approved and summary-eligible claim IDs.
9. Run `python3 scripts/validate_audit.py <audit.json> --report <report.json>` before handoff.

## Required Output

Return `report_id`, `topic_id`, `author_id`, `reviewer_id`, overall `verdict`, `publication_quality_score` for every non-reject verdict, `claim_reviews`, `approved_claim_ids`, `rejected_claim_ids`, `factual_conflicts`, `causal_weaknesses`, `required_edits`, `public_safe_abstract`, `abstract_claim_ids`, and `summary_claim_ids`.

Only `approved_claim_ids` may flow into `approved_research_claims`. `$finance-research-topic-selector` scores topics; do not retroactively change its 100-point score.

## Guardrails

- Price co-movement is evidence, not automatic causality.
- Lack of price reaction is not proof of benign intent or low ultimate risk.
- An official statement verifies what was said, not that its forecast or attribution is true.
- A mathematically correct calculation can still be invalid if dates, contracts, or denominators differ.
- Do not hide material conflicts behind qualified prose.
- Do not approve a summary sentence merely because the report verdict is `publish_full`.
