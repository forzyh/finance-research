---
name: finance-research-topic-selector
description: Score and select one to three evidence-backed finance insight questions from market anomalies, desk questions, and emerging structural developments. Use when Codex must identify researchable shifts in technology, corporate strategy, industrial organization, policy, capital allocation, geopolitics, or society; apply a fixed 100-point rubric and 70-point floor; and choose questions with explanatory leverage and multi-horizon economic consequences without leaking an expected answer.
---

# Finance Research Topic Selector

## Purpose

Choose the smallest set of questions that can materially improve how readers understand the present and the future. Score evidence, explanatory leverage, and researchability—not headline drama or whether the topic already moved today's market.

## Required Reference

Read [references/topic-scoring-rubric.md](references/topic-scoring-rubric.md) before scoring.

## Eligibility Before Scoring

Reject a candidate from the scored pool unless all conditions hold:

- `base_verified` is true;
- `source_pair` contains at least two independent source families, with at least one grade A or B source;
- `origin` is `raw_anomaly`, `desk_question`, or `frontier_question`;
- `question_type` identifies a market anomaly, strategic shift, technology trajectory, institutional change, business-model transition, or societal transition;
- an observable trigger exists even when there is no price anomaly;
- the candidate states a structural tension, such as efficiency versus control, generality versus specialization, openness versus value capture, or scale versus resilience;
- at least three analytical lenses, explicit near/medium/long horizons, and a stakeholder impact map are present;
- at least two evidence types and two competing hypotheses exist;
- a benchmark plan exists;
- confirmation and falsification signals are non-empty;
- the research question is causal, comparative, or mechanism-seeking rather than a broad topic label.

Do not rescue a failed gate with a high subjective score.

## Scoring and Selection

1. Assign each eligible candidate all seven scores and a short rationale per criterion.
2. Calculate the total out of 100; never normalize or add discretionary points.
3. Reject every candidate below 70. The 70-point threshold is absolute.
4. Group material overlaps by `overlap_key`; retain only the highest-scoring question in each group.
5. Rank remaining candidates by total, evidence availability, mechanism testability, structural importance, then stable `candidate_id`.
6. Select between one and three questions. If none reaches 70, select none and report the evidence gaps; never lower the threshold to force a topic.
7. Run `python3 scripts/score_topics.py <candidates.json> --max-topics 3 --output <selection.json>`.

## Assignment Packet

For each selected question, pass:

- topic ID, question, score and rationale;
- question type, observable trigger, structural tension, required lenses, time horizons, and impact map;
- observation cutoff and verified seed facts;
- source pair and known conflicts;
- competing hypotheses without marking an expected winner;
- required evidence classes and benchmark plan;
- confirmation and falsification signals;
- output contract: one 3000–5000 Chinese-character internal paper;
- deadline and output path supplied by the caller.

Do not reveal a preferred conclusion to `$finance-research-deep-dive`.

## Guardrails

- Select questions, not conclusions.
- Do not require a same-day price anomaly. A frontier question can qualify when several credible actors reveal the same strategic shift and the economic mechanism is researchable.
- Prefer questions that reveal a general principle and then return to concrete distributional effects. For example, several frontier-model companies designing chips can motivate a question about whether compute vertical integration is a durable stage of model economics, then test implications for accelerators, foundries, packaging, memory, cloud capex, entry barriers, and AI costs.
- Reject “philosophical” themes that cannot be tied to observed facts, mechanisms, affected actors, time horizons, and falsifiers.
- Penalize weak source independence inside the evidence-availability score, but still apply the hard dual-source gate first.
- Do not select several phrasings of the same causal issue.
- Do not exceed three selected questions.
