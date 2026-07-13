# Internal paper contract

## Identity chain

Require the assignment to provide immutable `report_id`, `topic_id`, and `author_id` values. Copy all three values exactly into the structured report. Do not synthesize, rename, or replace an identifier during research; return an assignment missing any identity value before writing.

## Length

Write 3000–5000 Chinese-character equivalents in the `article` field. Count Chinese characters individually and English words or standalone numbers as one equivalent each. Exclude structured metadata and source records from the limit.

## Article structure

1. **Research question and provisional answer** — state the cutoff and avoid certainty beyond evidence.
2. **Verified chronology** — show what changed before and after the event.
3. **The anomaly** — identify what is inconsistent across price, fundamentals, policy, history, or related assets.
4. **Competing hypotheses** — use at least three, including a null or non-event explanation.
5. **Evidence that discriminates** — explain why each observation favors or weakens a hypothesis.
6. **Benchmark or base rate** — compare with history, consensus, peer assets, prior policy, or the same session.
7. **Causal map and breakpoints** — separate observed links from inferred links and identify confounders.
8. **Counterevidence and alternative explanations** — state what the preferred hypothesis does not explain.
9. **Probabilistic conclusion** — rank hypotheses without claiming hidden intent or certainty.
10. **Next checks** — list confirmation and falsification signals with time windows.

## Structured hypothesis record

Each hypothesis should contain:

- `hypothesis_id` and statement;
- mechanism;
- supporting evidence IDs;
- counterevidence IDs;
- missing evidence;
- predicted observations;
- current relative weight expressed in prose or a bounded probability range.

Probabilities are analytical estimates, not facts. If used, make ranges sum coherently and explain their sensitivity.

## Claim ledger

Each claim requires:

- `claim_id` and exact text;
- `claim_type`: `fact`, `inference`, or `judgment`;
- `material`: whether it changes the thesis;
- `source_ids` and `supporting_evidence_ids`;
- `counterevidence_ids` for causal inferences;
- `uncertainty_or_limit`;
- `summary_candidate`: true or false.

The author must leave claims as drafts. Approval belongs exclusively to the independent causal reviewer.

## Source record

Record source ID, publisher, source family, grade, title, URL, publication time, retrieval time, and supported fact IDs. Explain conflicts involving time, percentage, entity, contract, currency, revision, or source wording.

## Unacceptable shortcuts

- “Asset X rose after event Y, therefore Y caused X.”
- “Gold did not rise, therefore the market expects peace.”
- “A target names an industry, therefore orders will follow.”
- “Strong earnings and a falling stock prove positioning caused the decline.”
