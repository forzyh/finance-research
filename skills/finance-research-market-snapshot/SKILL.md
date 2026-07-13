---
name: finance-research-market-snapshot
description: 为 finance-research v2 工作流构建盘后跨资产与期货快照，并识别可观察的市场异常信号。用于中文晚报或深度洞悉所需的 A股与港股收盘、风格与宽度、成交和资金、欧洲早盘、美股盘前或期指、利率、汇率、商品、加密资产，以及国内农产品、黑色、能源、有色和贵金属期货。
---

# 财经研究市场快照

## 目标

建立时间口径一致的收盘快照，为市场复盘提供底座，并为研究问题提供能够区分假设的证据。已观察价格与解释必须分开。

## 流程

1. 阅读 `references/instruments.md`，确认覆盖范围、符号和解释检查项。
2. 适用时运行 `scripts/fetch_sina_futures.py --watchlist core --json` 获取国内连续期货；必须标为来源快照，不得当作交易所结算价。
3. 先采集 A股和港股收盘：指数、涨跌家数、成交额、风格、行业表现和可取得的资金指标。
4. 再补充欧洲早盘、美股股指期货或盘前、利率、汇率、原油、黄金、白银、铜、铁矿、农产品期货和重要加密资产变化。
5. 每项报价都记录时间，并区分 `close`、`live`、`delayed`、`stale` 和 `missing`。
6. 只计算透明可复现的比较：相对收益、价差、距盘中极值的反转、宽度背离或跨资产确认；保留操作数与单位。
7. 识别标题与价格不一致、指数与市场宽度背离、风格错位或相关资产方向冲突等原始异常。
8. 将异常关联到相关 `fact_id`，但不得声称新闻导致了价格变化。

## v2 输出

将以下字段合并到 `run_bundle.json`：

- `schema_version`：`2`；
- `market_snapshot`：包含 `snapshot_cards`、`as_of`、`session_labels` 和覆盖元数据；
- `market_comparisons`：可复现的价差与相对变化；
- `raw_anomalies`：追加市场来源记录，不得覆盖采集阶段异常；
- `publication_checks.market_fresh`：布尔型新鲜度闸门；
- `publication_checks.market_freshness_details`：已检查时段、报价截止点和阻断原因。

### 快照卡

必须包含：

- `snapshot_id`、`asset`、`symbol`、`market` 和 `session`；
- 适用时提供 `price`、`change_absolute`、`change_percent`、`currency` 和 `unit`；
- `quote_time`、`source_name`、`source_url_or_endpoint` 和 `data_quality`；
- `observation`：只描述价格；
- `possible_context`：可选假设，必须明确标为解释。

### 市场比较

必须包含 `comparison_id`、`label`、`left_snapshot_id`、`right_snapshot_id`、公式、数值、单位、比较窗口和解释边界。

### 市场异常

使用规范候选 DTO：`candidate_id`、`research_question`、`origin: raw_anomaly`、`question_type: market_anomaly`、`observable_trigger`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons`、`impact_map`、`evidence_types`、`competing_hypotheses`、`source_pair`、`benchmark_plan`、`confirmation_signals`、`falsification_signals` 和 `overlap_key`。同时保留 `title`、`observed_pattern`、`comparison_baseline`、`seed_fact_ids`、`affected_assets`、`why_unusual` 和 `evidence_gaps`。在 `$finance-research-fact-verifier` 原子核验候选之前，设置 `verification_status: pending`、`base_verified: false`，并令 `source_pair` 为空。

## 必须覆盖

- A/H股：主要指数、科创50、创业板、恒生科技、市场宽度、成交额和重要行业/风格价差。
- 科技风险：纳斯达克/纳斯达克100、可取得时的费城半导体，以及代表性龙头或 ETF。
- 利率与汇率：相关中国国债收益率、美债2年/10年、美元兑人民币、美元兑离岸人民币，以及重要时的美元指数。
- 商品：布伦特/WTI、上海原油、黄金、白银、铜、铁矿。
- 国内期货：鸡蛋、玉米、豆粕、生猪、白糖、棉花、螺纹钢、铁矿石、铜、黄金和原油；活跃时按参考观察表扩展。

## 发布闸门

正常交易日若 A股、港股或国内期货时段标签错误、数据缺失或陈旧，必须阻止发布并记录原因，不得用前一交易日收盘替代。

## 硬性边界

- 连续合约快照不得当作官方结算价。
- 不得只凭一个资产声称“已计价”“避险”“风险厌恶”或某因素构成因果驱动。
- 提出研究问题前，至少检查一个替代资产、时间顺序和比较基准。
- 面向读者的名称必须与原始代码和内部结构分离。
