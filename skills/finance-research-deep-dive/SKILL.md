---
name: finance-research-deep-dive
description: Produce internal Chinese “深度洞悉” papers for selected market, strategic, technological, institutional, business-model, or societal questions. Use when Codex receives a scored assignment and must move from an observed trigger to an abstract principle, test competing mechanisms, trace value migration and second-order economic effects across near/medium/long horizons, apply a disciplined philosophical lens, and deliver a 3,000–5,000-character evidence-led paper with an auditable claim ledger.
---

# Finance Research 深度洞悉

## Purpose

Write one internal insight paper per selected question. The paper is evidence for editorial review, not publishable copy and not a defense of a predetermined answer. It may begin with today's market, but it must not be confined to today's market.

## Required Reference

Read [references/internal-paper-contract.md](references/internal-paper-contract.md) before research or writing.

## Inputs

Require an assignment packet containing:

- immutable `report_id`, `topic_id`, and `author_id` values plus the research question;
- observation cutoff and verified seed facts;
- independent source pair and known conflicts;
- competing hypotheses and required evidence classes;
- question type, observable trigger, structural tension, required analytical lenses, time horizons, and stakeholder impact map;
- benchmark, confirmation, and falsification plans;
- output location and deadline.

Copy `report_id`, `topic_id`, and `author_id` unchanged into the report. Reject or return an incomplete assignment if any identity field is absent, if it leaks an expected conclusion, lacks two independent sources, or omits the cutoff.

## Research Workflow

1. Reconfirm every seed fact at the stated cutoff; refresh unstable facts before using them.
2. Build a chronology that distinguishes announcement, market session, settlement, close, and later update.
3. Abstract the event into a general tension or constraint. State the smallest reusable principle that could explain more than this one case.
4. Expand to at least three competing explanations, including a null, bargaining-option, implementation, or non-event mechanism where appropriate.
5. Analyze at least three relevant lenses: technology architecture, unit economics, industrial organization, corporate strategy, capital markets, policy/geopolitics, labor/consumers, history, or philosophy.
6. Gather discriminating evidence rather than more examples of the same signal. Separate company statements, actual investment, technical feasibility, adoption, economics, and market pricing.
7. Compare with a historical, cross-sectional, consensus, technology-transition, or business-model benchmark.
8. Map the causal chain and value migration link by link. Mark observed, inferred, missing, lagged, and confounded links.
9. Build near-, medium-, and long-horizon consequences. Identify first-order effects, second-order responses, feedback loops, beneficiaries, losers, bottlenecks, and possible equilibrium changes.
10. Apply a philosophical lens to scarcity, control, dependence, specialization, coordination, standardization, or power only after the empirical mechanism is established. Label normative claims and metaphors.
11. Seek counterevidence and state what each hypothesis cannot explain. Treat “inevitable” as a thesis requiring unusually strong evidence.
12. Form a probabilistic conclusion with explicit uncertainty and conditions for revision.
13. Write a 3000–5000 Chinese-character internal article. Keep the main article within the limit; structured metadata and source records are separate.
14. Build a claim ledger. Do not mark any claim `approved`; only `$finance-research-causal-reviewer` may approve claims.
15. Run `python3 scripts/validate_research_report.py <report.json>`.

## Required Output

Return a report object containing:

- `report_id`, `topic_id`, `author_id`, `research_question`, `observation_cutoff`, and `article`;
- `hypotheses`, `chronology`, `evidence`, `counterevidence`, and `benchmark`;
- `causal_map`, `limitations`, and `probabilistic_conclusion`;
- `question_type`, `abstract_principle`, `time_horizon_map`, `stakeholder_impact_map`, `second_order_effects`, and `philosophical_lens`;
- `confirmation_signals` and `falsification_signals`;
- `claims` and `sources` with stable IDs.

The article must explain the question, not merely list information. Use the structure in the reference and keep facts, inferences, and judgments distinguishable in prose.

## Claim Discipline

- Cite every material factual claim to two independent sources.
- Give every causal inference supporting evidence, counterevidence, and an identified missing link or confounder.
- Treat a price pattern as evidence about probabilities, not proof of intent or cause.
- Treat company announcements as evidence of strategy, not proof of technical success, cost advantage, volume adoption, or incumbent displacement.
- For valuation implications, expose the bridge from industry structure to revenue, margins, duration, capital intensity, and multiple; do not jump from “competition increases” to a target valuation.
- Tag a possible summary sentence with `summary_candidate: true`; this is a nomination, not approval.
- Preserve unresolved conflicts for the reviewer instead of silently choosing a convenient version.

## Guardrails

- Do not exceed 5000 or fall below 3000 counted characters.
- Do not collapse several selected questions into one paper.
- Do not convert an official target into realized spending, orders, or earnings.
- Do not infer political intent from market prices alone.
- Do not use “必经之路”, “终局”, or “必然” without defining the domain, time horizon, necessary conditions, and plausible exceptions.
- Do not mistake an evocative analogy for a historical base rate.
- Do not let the author perform the final causal audit of the same paper.
