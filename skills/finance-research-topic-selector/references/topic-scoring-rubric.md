# Topic scoring rubric

## Fixed 100-point scale

| Criterion | Maximum | High-score test |
|---|---:|---|
| `market_importance` | 20 | Affects broad assets, major sectors, policy transmission, earnings, inflation, or risk budgets |
| `anomaly` | 15 | Price or fact pattern materially differs from consensus, history, related assets, or the morning thesis |
| `evidence_availability` | 20 | Independent dual-source base plus timely physical, market, corporate, policy, or historical evidence is obtainable |
| `causal_testability` | 15 | Competing mechanisms make different observable predictions |
| `cross_asset_breadth` | 10 | Two or more relevant asset classes, regions, or value-chain links help discriminate explanations |
| `novelty` | 10 | Adds non-obvious information rather than repeating the news headline |
| `next_session_falsifiability` | 10 | Concrete next-session evidence can confirm or weaken the thesis |
| **Total** | **100** | |

Scores may be integers or half points, but each must remain between zero and its fixed maximum. Include a criterion-specific rationale; do not award points for prose quality.

## Hard threshold

- `score_total >= 70`: eligible for ranking if all gates pass.
- `score_total < 70`: reject from deep-dive selection.
- Never round 69.5 to 70 and never lower the threshold because the news day is quiet.

## Evidence gate

A dual-source candidate requires two independently produced sources, not two URLs. Common ownership, syndication, circular citation, or a reposted press release counts as one family. At least one source must be grade A or B.

## Overlap rule

Use the same `overlap_key` for candidates that ask substantially the same causal question. Retain the highest total. On ties, prefer evidence availability, then causal testability, then market importance, then stable ID.

## Selection output

Select one to three questions. Zero is allowed only when no candidate clears both the hard gates and 70 points. Record rejected candidates and reasons so the workflow can improve collection rather than silently lowering standards.

