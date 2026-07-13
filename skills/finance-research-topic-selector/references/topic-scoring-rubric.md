# Topic scoring rubric

## Fixed 100-point scale

| Criterion | Maximum | High-score test |
|---|---:|---|
| `structural_importance` | 20 | Changes an important constraint, capability, institution, value chain, profit pool, or allocation of power—not merely a daily price |
| `explanatory_leverage` | 15 | One well-framed question can explain several observations and yield a reusable principle rather than restating headlines |
| `evidence_availability` | 15 | Independent dual-source facts plus technical, corporate, policy, market, historical, or scientific evidence are obtainable |
| `mechanism_testability` | 15 | Competing mechanisms imply distinct observable outcomes and expose intermediate links |
| `cross_layer_impact` | 15 | Connects at least three layers such as technology architecture, firm strategy, industry structure, capital markets, policy, labor, consumers, or geopolitics |
| `historical_comparability` | 10 | Has a relevant historical, cross-sectional, business-model, or technology-transition comparison without forcing analogy |
| `future_falsifiability` | 10 | Specifies observable checks across suitable near-, medium-, or long-term horizons; it need not resolve next session |
| **Total** | **100** | |

Scores may be integers or half points, but each must remain between zero and its fixed maximum. Include a criterion-specific rationale; do not award points for prose quality.

## Hard threshold

- `score_total >= 70`: eligible for ranking if all gates pass.
- `score_total < 70`: reject from 深度洞悉 selection.
- Never round 69.5 to 70 and never lower the threshold because the news day is quiet.

## Three origins

- `raw_anomaly`: an observable mismatch in price, facts, timing, policy, or related assets.
- `desk_question`: a mechanism question extracted by a policy, company, technology, commodity, or global desk.
- `frontier_question`: an emerging pattern whose structural importance can precede clear market pricing, such as frontier-model companies moving into proprietary silicon.

All three origins face the same evidence and falsifiability gates. “Interesting future topic” is not sufficient.

## Evidence gate

A dual-source candidate requires two independently produced sources, not two URLs. Common ownership, syndication, circular citation, or a reposted press release counts as one family. At least one source must be grade A or B.

## Abstraction test

A high-quality candidate moves through four levels without skipping one:

1. observed trigger;
2. underlying constraint or incentive;
3. mechanism and value migration;
4. economic and social consequences across time.

Reward philosophical leverage only when the abstract principle returns to concrete actors, quantities, decisions, and falsifiers. Do not reward grand language, inevitability claims, or unsupported forecasts.

## Overlap rule

Use the same `overlap_key` for candidates that ask substantially the same causal question. Retain the highest total. On ties, prefer evidence availability, then mechanism testability, then structural importance, then stable ID.

## Selection output

Select one to three questions. Zero is allowed only when no candidate clears both the hard gates and 70 points. Record rejected candidates and reasons so the workflow can improve collection rather than silently lowering standards.
