# 深度洞悉 internal paper contract

## Identity chain

Require the assignment to provide immutable `report_id`, `topic_id`, and `author_id` values. Copy all three values exactly into the structured report. Do not synthesize, rename, or replace an identifier during research; return an assignment missing any identity value before writing.

## Length

Write 3000–5000 Chinese-character equivalents in the `article` field. Count Chinese characters individually and English words or standalone numbers as one equivalent each. Exclude structured metadata and source records from the limit.

## Analytical coverage

The following items must be covered, but they are not a mandatory heading list. Combine them into four to seven natural sections when that reads better. Do not make the public article look like a completed questionnaire.

1. **Question, trigger, and provisional answer** — state the cutoff, question type, and what newly became observable.
2. **Verified chronology** — distinguish ideas, announcements, investment, technical milestones, adoption, earnings effects, and price response.
3. **From phenomenon to principle** — identify the underlying constraint or strategic tension and state an abstract principle that can travel beyond the case.
4. **Competing hypotheses** — use at least three, including a null, bargaining-option, or implementation-gap explanation.
5. **Mechanism across lenses** — connect the relevant technical architecture, unit economics, firm incentives, industry structure, institutions, and capital markets.
6. **Value migration and stakeholder map** — explain which capabilities become scarce, who captures value, who loses bargaining power, and which complements benefit.
7. **Time-horizon map** — separate near-term announcements/capex, medium-term adoption/economics, and long-term equilibrium or social effects.
8. **Second-order effects and feedback loops** — include competitor responses, supply-chain adaptation, standards, regulation, labor, consumers, and capital allocation where relevant.
9. **Benchmark or base rate** — compare with history, peers, prior integration cycles, technology transitions, consensus, or same-session evidence.
10. **Counterevidence, breakpoints, and alternatives** — state what the preferred thesis cannot explain and where the chain may fail.
11. **Philosophical interpretation** — discuss scarcity, autonomy, specialization, coordination, dependence, or power as an interpretation grounded in the mechanism; distinguish empirical, normative, and metaphorical claims.
12. **Probabilistic conclusion and future checks** — rank hypotheses and give confirmation/falsification windows suitable to the topic, not only the next trading day.

## Authored voice

Write like a knowledgeable person making a case to another knowledgeable person. Begin with the fact or tension that made the question worth asking. Let one strong example carry more weight than a list of five weak examples. Use concrete subjects and verbs. Vary sentence and paragraph length. A short sentence may carry the conclusion.

Avoid announcing the essay, summarizing every section twice, or manufacturing balance with “一方面、另一方面”. Do not repeat “值得注意的是、这意味着、本质上、总体而言” as connective tissue. Avoid serial “不是A而是B” formulations. Put uncertainty next to the claim it limits, then move on.

The philosophy section should feel earned by the preceding evidence. Do not change tone into a grand speech. End with a concrete breakpoint, stakeholder consequence, or unresolved choice.

## Abstraction discipline

Use the ladder `trigger → constraint/incentive → mechanism → value migration → economic/social consequence`. Every move upward must preserve the observable facts below it; every move downward must name concrete actors and measurable effects.

For example, several frontier-model companies developing proprietary accelerators can motivate a broader thesis about compute becoming a strategic control point. The paper must still test whether the motivation is cost, hardware-model co-design, supply assurance, bargaining leverage, data-center power, or geopolitics; distinguish design intent from viable volume deployment; and trace conditional effects on accelerator vendors, foundries, advanced packaging, memory, cloud capex, model costs, and entry barriers.

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
- “Several firms announced chips, therefore every model company must vertically integrate.”
- “Custom silicon hurts the incumbent, therefore its valuation must fall.”
- “The historical analogy feels similar, therefore the same equilibrium will follow.”
