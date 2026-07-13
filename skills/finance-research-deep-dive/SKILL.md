---
name: finance-research-deep-dive
description: Produce internal Chinese finance research papers for selected causal questions. Use when Codex receives a scored assignment from the finance research topic selector and must write a 3,000–5,000-character evidence-led paper with chronology, competing hypotheses, market and fundamental evidence, counterevidence, benchmarks, causal limits, probabilistic conclusions, and an auditable claim ledger.
---

# Finance Research Deep Dive

## Purpose

Write one internal research paper per selected question. The paper is evidence for editorial review, not publishable copy and not a defense of a predetermined answer.

## Required Reference

Read [references/internal-paper-contract.md](references/internal-paper-contract.md) before research or writing.

## Inputs

Require an assignment packet containing:

- immutable `report_id`, `topic_id`, and `author_id` values plus the research question;
- observation cutoff and verified seed facts;
- independent source pair and known conflicts;
- competing hypotheses and required evidence classes;
- benchmark, confirmation, and falsification plans;
- output location and deadline.

Copy `report_id`, `topic_id`, and `author_id` unchanged into the report. Reject or return an incomplete assignment if any identity field is absent, if it leaks an expected conclusion, lacks two independent sources, or omits the cutoff.

## Research Workflow

1. Reconfirm every seed fact at the stated cutoff; refresh unstable facts before using them.
2. Build a chronology that distinguishes announcement, market session, settlement, close, and later update.
3. Expand to at least three competing explanations, including a null or non-event mechanism.
4. Gather discriminating evidence rather than more examples of the same signal.
5. Compare with a historical, cross-sectional, consensus, or same-session benchmark.
6. Map the proposed causal chain link by link. Mark observed links, inferred links, missing links, and possible confounders.
7. Seek counterevidence and state what each hypothesis cannot explain.
8. Form a probabilistic conclusion with explicit uncertainty and conditions for revision.
9. Write a 3000–5000 Chinese-character internal article. Keep the main article within the limit; structured metadata and source records are separate.
10. Build a claim ledger. Do not mark any claim `approved`; only `$finance-research-causal-reviewer` may approve claims.
11. Run `python3 scripts/validate_research_report.py <report.json>`.

## Required Output

Return a report object containing:

- `report_id`, `topic_id`, `author_id`, `research_question`, `observation_cutoff`, and `article`;
- `hypotheses`, `chronology`, `evidence`, `counterevidence`, and `benchmark`;
- `causal_map`, `limitations`, and `probabilistic_conclusion`;
- `confirmation_signals` and `falsification_signals`;
- `claims` and `sources` with stable IDs.

The article must explain the question, not merely list information. Use the structure in the reference and keep facts, inferences, and judgments distinguishable in prose.

## Claim Discipline

- Cite every material factual claim to two independent sources.
- Give every causal inference supporting evidence, counterevidence, and an identified missing link or confounder.
- Treat a price pattern as evidence about probabilities, not proof of intent or cause.
- Tag a possible summary sentence with `summary_candidate: true`; this is a nomination, not approval.
- Preserve unresolved conflicts for the reviewer instead of silently choosing a convenient version.

## Guardrails

- Do not exceed 5000 or fall below 3000 counted characters.
- Do not collapse several selected questions into one paper.
- Do not convert an official target into realized spending, orders, or earnings.
- Do not infer political intent from market prices alone.
- Do not let the author perform the final causal audit of the same paper.
