# Finance Fact Verification Rubric

## Source Grade

| Grade | Source type | Examples |
|---|---|---|
| A | Official or primary | Central banks, statistical agencies, exchange filings, company announcements, SEC, HKEXnews. |
| B | Wire or major mainstream finance media | Reuters, AP, CNBC, MarketWatch, major financial newspapers. |
| C | Specialist or industry media | Sector media, brokerage notes, trade associations, commodity consultancies. |
| D | Fast-news feeds and social platforms | 7x24 feeds, reposts, forums, social media. |

## News Value Score

Score each event from 1 to 10:

- Novelty: Is there new information or just repetition?
- Impact breadth: Does it affect one company, one sector, or broad risk appetite?
- Surprise: Is it meaningfully different from consensus or recent pricing?
- Market reaction: Have stocks, rates, FX, commodities, or futures moved?
- Trackability: Are there concrete follow-up signals?

## Confidence

- High: primary source confirms the fact, or multiple reliable independent sources match.
- Medium: one reliable source plus consistent market/data evidence, or two non-primary sources match.
- Low: fast-news-only, social-only, unclear source, or unresolved conflict.

## Conflict Handling

List conflicts before writing:

- Time conflict
- Amount or percentage conflict
- Policy wording conflict
- Entity/company/ticker conflict
- Price or market reaction conflict

When conflicts remain, use the most primary source for the factual claim and mark other versions as unresolved.

## Market Reaction Checks

Before claiming an event is "priced in" or "driving the market", check at least one relevant observable:

- Equity index, sector index, ETF, or representative stock.
- Bond yield or rate futures.
- FX rate or dollar index.
- Commodity or domestic futures contract.
- Volume, open interest, basis, or inventory when available.

Align the quote session and disclosure time. A later close cannot prove a reaction to information released after that close.

## Research Candidate Pre-selection Gate

The verifier may mark a candidate `eligible` only when:

- The seed facts and market timestamps survive verification.
- The claimed anomaly is observable against a named baseline.
- At least two distinct evidence types are realistically obtainable.
- At least two competing explanations are meaningfully different.
- A historical, cross-sectional, expectation, or mechanism benchmark is feasible.
- Confirmation and falsification signals are measurable.

Use `needs_evidence` when the question is promising but one requirement is missing. Use `duplicate` for substantial overlap and identify the overlap group. Use `rejected` for false premises, stale data, unresolvable conflicts, or questions that cannot be tested.

Do not assign the final 100-point topic score. Verification determines eligibility and claim scope; the topic selector ranks eligible questions.
