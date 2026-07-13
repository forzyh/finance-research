# Stock Hotspot Rubric

## Candidate Sources

- 7x24 feeds with stock tags: 财联社, 东方财富, 新浪财经, 同花顺.
- Company announcements: 上交所, 深交所, 北交所, 港交所, SEC, company IR.
- Post-close editorial sources: exchange close summaries, 财联社/证券时报/e公司复盘, company filings, and reliable global market coverage.
- Market data: top gainers/losers, turnover leaders, sector leaders, unusual volume, repeated limit-up/limit-down names.
- Prior run bundles: names repeatedly appearing across recent runs.

## Stock-Level Questions

For each hot stock, answer:

1. What exactly happened?
2. Is the driver confirmed by company/official/exchange source, or only by fast-news/rumor?
3. Did price move before or after the information?
4. Is this stock leading a theme, confirming an existing theme, or warning of speculation/risk?
5. Are peers moving too?
6. Is there a related futures/commodity, rate, FX, or policy driver?

## Theme Extraction

Classify stock clusters:

- `leader_confirmation`: leading stocks and peers move with confirmed driver.
- `theme_diffusion`: news starts from one name and spreads across sector/chain.
- `rumor_heat`: price moves before confirmation or relies on social/fast-news only.
- `risk_repricing`: inquiry letters, failed deals, earnings miss, regulatory risk.
- `macro_sensitive`: stock moves mainly reflect rates, FX, commodities, or global risk appetite.
- `idiosyncratic`: company-specific, not enough evidence for sector trend.

## Technology Stock Routing

When a hot stock belongs to technology, do not stop at a generic `科技股` theme. Assign a likely lane and hand it to `$finance-research-tech-analyst`:

- AI infrastructure: GPU/ASIC, AI servers, optical modules, switches, data-center power/cooling.
- AI applications/software: SaaS, enterprise AI, model platforms, vertical AI tools.
- Semiconductors: design, foundry, memory, equipment, materials, EDA/IP, advanced packaging.
- Internet platforms: e-commerce, local services, games, ads, cloud, buybacks, regulation.
- Consumer electronics: phone/PC/wearables/MR supply chain.
- Smart vehicles/robotics: autonomous driving, auto chips, sensors, humanoid robots, industrial automation.
- Digital infrastructure/cybersecurity: telecom equipment, satellite internet, cybersecurity, cloud infra.

## Evening Research Output

Stock analysis should support two paths:

- A concise public "重点新闻与热点个股" section with 3-8 developed names or clusters.
- Research candidates when chronology, peer evidence, fundamentals and price expose a testable expectation gap.

## Research Candidate Gate

Ask before emitting a candidate:

1. Is the gap observable rather than rhetorical?
2. Can at least two competing explanations survive initial review?
3. Are there two independent evidence types, such as filings plus price/flow data?
4. Is a historical, peer, supply-chain or expectation benchmark feasible?
5. Can tomorrow or a named future event confirm or falsify the preferred explanation?
