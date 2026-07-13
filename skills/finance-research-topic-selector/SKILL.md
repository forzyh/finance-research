---
name: finance-research-topic-selector
description: Score and select finance research questions from verified anomalies and desk candidates. Use when Codex must enforce independent dual-source eligibility, apply a fixed 100-point rubric and 70-point floor, remove overlapping topics, and choose one to three causal questions for internal deep-dive research without leaking an expected answer.
---

# Finance Research Topic Selector

## Purpose

Choose the smallest set of questions that can materially improve the report. Score evidence and researchability, not headline drama.

## Required Reference

Read [references/topic-scoring-rubric.md](references/topic-scoring-rubric.md) before scoring.

## Eligibility Before Scoring

Reject a candidate from the scored pool unless all conditions hold:

- `base_verified` is true;
- `source_pair` contains at least two independent source families, with at least one grade A or B source;
- `origin` is `raw_anomaly` or `desk_question`;
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
5. Rank remaining candidates by total, evidence availability, causal testability, market importance, then stable `candidate_id`.
6. Select between one and three questions. If none reaches 70, select none and report the evidence gaps; never lower the threshold to force a topic.
7. Run `python3 scripts/score_topics.py <candidates.json> --max-topics 3 --output <selection.json>`.

## Assignment Packet

For each selected question, pass:

- topic ID, question, score and rationale;
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
- Prefer anomalies with discriminating evidence over already-explained headlines.
- Penalize weak source independence inside the evidence-availability score, but still apply the hard dual-source gate first.
- Do not select several phrasings of the same causal issue.
- Do not exceed three selected questions.
