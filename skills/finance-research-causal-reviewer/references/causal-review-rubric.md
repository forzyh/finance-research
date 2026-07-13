# Causal review rubric

## Identity and coverage gate

Match the audit's `report_id`, `topic_id`, and `author_id` exactly to the report and require a distinct `reviewer_id`. Review every report claim with `material: true` exactly once. Reject audits that omit a material claim, review it more than once, or reference a claim ID absent from the report.

## L1 — Fact and source

Check:

- exact claim wording against sources;
- two independent sources for material non-trivial facts;
- primary-source status and source-family independence;
- observation cutoff and post-cutoff contamination;
- unresolved time, amount, entity, wording, percentage, or attribution conflicts.

Fail when a material fact is unsupported, stale, circularly sourced, or contradicted without disclosure.

## L2 — Number, time, and comparability

Recompute totals, percentages, growth rates, spreads, cumulative returns, and implied rates. Check calendar versus trading day, local versus UTC time, intraday versus close, futures month and roll, spot versus settlement, nominal versus real, annual versus cumulative, and restated versus original bases.

Fail when the correction changes the thesis or when incomparable snapshots create pseudo-precision.

## L3 — Causality

Require:

- cause preceding effect;
- a plausible mechanism with observed intermediate links;
- at least one serious alternative explanation;
- counterevidence and confounders;
- a benchmark or base rate;
- confirmation and falsification signals.

Downgrade intent claims, “priced in” claims, and single-day causal claims unless direct evidence exists. If prices merely fit a hypothesis, use “consistent with” rather than “proves.”

## L4 — Publication and summary

Ensure public wording distinguishes fact, inference, and judgment; preserves uncertainty; avoids internal fields and workflow jargon; and gives no personalized trading instruction.

Only an `approved` claim with `summary_eligible: true` can enter the abstract or summary. A `qualified` claim may enter a note only with its exact required qualification and after any material change is re-reviewed.

## Claim conclusions

| Conclusion | Meaning | Summary eligible |
|---|---|---|
| `approved` | Supported, correctly scoped, and public-safe | Yes, only if separately marked eligible |
| `qualified` | Usable only with an explicit limitation in body or note | No |
| `revise` | Potentially usable after evidence or wording changes and re-review | No |
| `rejected` | False, unsupported, misleading, or irreparably confounded | No |

## Overall four-level verdict

| Verdict | Use |
|---|---|
| `publish_full` | One flagship article; all thesis-critical claims approved and no blocking conflict |
| `publish_note` | A shorter note built from approved claims; depth or causal closure is insufficient for flagship use |
| `summary_only` | Only approved claim IDs may be used in the summary; no deep-dive article |
| `reject` | No publication from this report |

For `publish_full`, thesis-critical calculations and causal links must pass L1–L3. For any verdict, summary admission remains claim-specific.

## Publication quality score

For every non-`reject` verdict, assign `publication_quality_score` from 0 to 100 after claim review. Score source integrity, numerical and timestamp comparability, causal closure, counterevidence handling, uncertainty discipline, and public usability. This is a publication-ranking score, not the topic selector's 100-point research-priority score. A `reject` audit may omit it.
