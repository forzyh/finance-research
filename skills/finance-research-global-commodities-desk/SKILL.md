---
name: finance-research-global-commodities-desk
description: 为财经简报研究全球商品、航运、实物供给、宏观跨资产和地缘传导。用于解释原油、黄金、有色、黑色、农产品、运费、汇率、利率或冲突驱动的价格异常，并生成经过两个独立来源支持、包含实物市场和跨资产检验的研究候选。
---

# 财经研究全球与商品分析台

## 目标

把商品和地缘异常转化为可检验的研究候选。价格变化不能直接证明供给受损、政治意图或长期趋势。

## 必读参考

构建候选前完整阅读 [references/commodities-causal-map.md](references/commodities-causal-map.md)。

## 工作流程

1. 设置带时间戳的观察截止点，将每项报价标为收盘、盘中、盘前、结算、指示价、现货或期货。
2. 用两个独立来源确认事件；转载和同源稿件按一个来源家族处理。
3. 检查实物层：产量、出口、船舶流量、库存、基差、现货升贴水、运费、保险、炼化或加工利润，以及适用时的期限结构。
4. 检查金融层：期货价格、成交量、持仓量、期权偏度、仓位、汇率、利率、通胀预期、股票、信用和避险资产。
5. 将当前路径与历史基准或同一交易时段基准比较，避免跨来源伪精确。
6. 提出至少两个竞争假设，其中包括仓位、流动性、合约机制、天气、库存或宏观利率等非事件解释。
7. 为下一交易时段定义可观察的确认和证伪信号。
8. 只有双来源且基础核验通过的材料包才可晋级。贸易结构、资源安全、航线、能源体系或地缘经济秩序的持久变化即便尚未得到当日价格确认，也可使用 `frontier_question`；未解决的单一来源事件转入 `watchlist`。
9. 交接前运行 `python3 scripts/validate_desk_packet.py <packet.json>`。

## 候选闸门

每个候选都必须满足工作流的统一候选契约，并包含：

- `observation_cutoff`、`base_verified: true`，以及 `origin: desk_question` 或 `frontier_question`；
- `question_type`、`observable_trigger`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons` 和 `impact_map`；
- 相互独立的 `source_pair`，其中至少一个来源为 A 或 B 级；
- `verified_facts`，每项重要事件事实都要有两个 source ID；
- 至少两类 `evidence_types` 和两个 `competing_hypotheses`；
- `market_evidence`、`physical_evidence` 和 `cross_asset_checks`；
- 基准、确认信号、证伪信号和已知数据缺口；
- `affected_assets`，以及内部明确的合约或工具标识。

不得给出编辑选题分。百分制评分与 70 分门槛由 `$finance-research-topic-selector` 执行。

## 地缘论断

区分四个层次：

1. 已核验的事件时间线；
2. 已观察的市场与实物证据；
3. 对市场预期的推断；
4. 对政府或军事意图的归因。

价格只能以概率方式支持第三层。第四层必须有直接官方声明、可查证的谈判记录或独立报道的决策证据。

## 交接

输出 `desk: global_commodities`、`observation_cutoff`、`candidates` 和 `watchlist`。保留来源 ID、报价时间、单位、币种、合约月份和比较基准。

## 硬性边界

- 不得把跨来源快照写成已核验的盘中最高价或最低价。
- 没有实物证据或期限结构证据时，不得推断供给短缺。
- 不得只看黄金就断言“市场平静”；还要检验利率、美元、波动率、信用和其他避险资产。
- 不得只凭油价和金价推断“谈判将重启”或“冲突有限”。
- 事实、机制假设、替代解释和判断必须分开。
