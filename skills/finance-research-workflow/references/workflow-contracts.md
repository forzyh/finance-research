# Workflow contracts

## Stage artifacts

Store the canonical `run_bundle.json` at the run root and stage evidence below it:

- `00_intake/`: raw collection, normalized fact cards, collection errors.
- `01_market/`: market snapshot and freshness checks.
- `02_desks/`: policy, stock, technology, and global/commodity briefs.
- `03_verification/`: trend comparison and verified events.
- `04_research/`: candidates, selected topics, assignment packets, reports, and audits.
- `05_editorial/`: summary packet and final Markdown report.
- `06_publish/`: HTML, deploy result, email cover, and delivery result.

## Candidate contract

Every canonical candidate must contain `candidate_id`, `title`, `research_question`, `origin`, `seed_fact_ids`, `source_pair`, `evidence_types`, `competing_hypotheses`, `benchmark_plan`, `confirmation_signals`, `falsification_signals`, `overlap_key`, `base_verified`, `scores`, and `score_rationale`. `origin` is `raw_anomaly` or `desk_question`. Run `normalize_candidates.py` before scoring; producers may not pass private aliases directly to the selector.

Score maxima are: market importance 20, anomaly 15, evidence availability 20, causal testability 15, cross-asset breadth 10, novelty 10, and next-session falsifiability 10. Eligibility requires at least 70 points, base verification, two evidence types, two competing hypotheses, a benchmark, confirmation and falsification signals, and no material overlap with a higher-scoring topic.

## Research assignment and report

An assignment contains the topic, observation cutoff, verified seed facts, known conflicts, required evidence classes, output paths, and deadline. A report contains a 3,000–5,000 Chinese-character article plus structured hypotheses, chronology, evidence, counterevidence, benchmark, limitations, probabilistic conclusion, claims, and sources.

Do not expose the expected answer to the research agent. Do not let one research agent review its own causal claims.

## Audit contract

Each audit has a verdict: `publish_full`, `publish_note`, `summary_only`, or `reject`. It lists approved claim IDs, rejected claim IDs, summary-eligible claim IDs, factual conflicts, causal weaknesses, required edits, a 0–100 `publication_quality_score`, and a public-safe abstract. Only IDs present in both the approved and summary-eligible sets may enter `approved_summary_claims` and its compatibility alias `approved_research_claims`; all approved body claims are stored separately in `approved_body_claims`.

The editor chooses the highest-quality `publish_full` report as the sole flagship. Additional `publish_full` reports are reduced to notes unless they are rejected for overlap. Publish at most two notes.

## Public report contract

The public report is ordered as: one-sentence conclusion; market path; core reasons; key news and hot stocks; technology subsectors; commodities and futures; world economy and geopolitics; flagship research and notes; next-session checks and sources.

The public page and email must not contain paths, script names, JSON fields, raw confidence/status labels, agent instructions, source-layer labels, or delivery internals. Separate facts, inference, and judgment. Do not provide personalized investment advice.

## Run eligibility

On a trading day, require current A-share, Hong Kong, and domestic-futures closes or an explicit market-closure reason. Mark US and European values as close, intraday, early-session, or premarket. Missing public/no-login Lark access is a hard delivery failure.
