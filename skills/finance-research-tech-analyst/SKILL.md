---
name: finance-research-tech-analyst
description: 分析跨市场科技风险偏好、科技细分赛道和新兴战略变化，输出结构化分析台观察、市场异常问题与前沿洞悉问题。用于 AI 基础设施、模型企业芯片战略、软硬协同、AI 应用、半导体、平台、消费电子、机器人、通信、数据中心、电力、网络安全、科技商业模式、产业组织或全球向中国市场的传导。
---

# 财经研究科技赛道分析

## 目标

判断哪些科技赛道得到市场与基本面的真实确认，哪些拥挤赛道退潮，以及哪些盘后变量可能改变下一交易日。把“科技”视为多条不同产业链，而不是一个笼统交易。

## 流程

1. 阅读 `references/tech-sector-taxonomy.md`。
2. 结合科创50、创业板、恒生科技、纳斯达克/纳斯达克100、费城半导体、利率、汇率及代表性龙头或 ETF，判断整体风险偏好。
3. 将重要事实、个股和价格归入定义好的细分赛道。
4. 对每条活跃赛道比较驱动因素、市场反应、龙头、同行、落后者、产业链证据、估值或拥挤风险及盘后披露。
5. 区分需求证据、资本开支、业绩、订单、政策、产品周期、出口管制和传闻驱动的波动。
6. 只有对齐交易时段和信息截止点后，才能比较 A/H/美股传导。
7. 对安静但重要的赛道标记 `no_material_new_signal`，不得虚构市场宽度。
8. 重大背离或预期差若能支持竞争假设与基准比较，则生成市场候选。
9. 独立核验的发展显示能力、企业边界、瓶颈、标准、商业模式或价值获取可能持久变化时，即使当天价格平静，也可生成 `frontier_question`。
10. 前沿问题要跨期限分析技术可行性、单位经济、供应链、公司激励、竞争反应、资本配置、政策/地缘和最终用户后果。不得认为公告等于规模化成功。

## v2 输出

合并写入：

- `schema_version`：必须为 `2` 并保持；
- `tech_sector_observations`：赛道级证据和状态；
- `desk_briefs.technology`：整体风险判断、确认赛道、退潮赛道、盘后变量和后续检查；
- `research_candidates`：追加科技分析台候选；
- `frontier_questions`：追加有独立依据的结构性候选。

### 科技赛道观察

必须包含：

- `observation_id`、`subsector`、`market_scope` 和 `data_cutoff`；
- `headline_read`、`price_action`、`confirmed_driver` 和 `source_fact_ids`；
- `leading_names`，包括角色、同行与落后者证据，以及 `supply_chain_link`；
- `status`：`strengthening`、`weakening`、`reversal`、`confirmed`、`falsified`、`unchanged`、`no_material_new_signal` 或 `insufficient_history`；
- `risk_flags`、`evidence_gaps`、`next_signal` 和 `confidence`。

### 分析台研究候选

必须包含 `candidate_id`、`origin: desk_question`、`question_type`、`research_question`、`why_now`、`observable_trigger`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons`、`impact_map`、`seed_fact_ids`、`anomaly_or_expectation_gap`、`affected_assets`、至少两个 `competing_hypotheses`、不同的 `evidence_types`、`source_pair` 数组、`benchmark_plan`、`evidence_gaps`、`confirmation_signals`、`falsification_signals` 和稳定的 `overlap_key`。在 `$finance-research-fact-verifier` 原子更新 `base_verified` 与 `source_pair` 前，设置 `verification_status: pending` 和 `base_verified: false`。

新 v2 输出不得使用 `tech_desk`、`alternative_hypotheses`、`evidence_types_available` 或 `desk_briefs.tech_sectors` 别名。

对于 `frontier_question`，以 `observable_trigger` 替代 `anomaly_or_expectation_gap`，并要求 `question_type`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons` 和 `impact_map`；证据、竞争假设、基准和核验闸门保持一致。

不得确定最终候选分数或选题。

## 必须覆盖的赛道

- AI 算力与基础设施；
- AI 应用与软件；
- 半导体设计、代工、存储、设备、材料、EDA/IP 和封装；
- 互联网平台；
- 消费电子；
- 智能汽车与机器人；
- 通信、光模块、数据中心、电力、液冷、卫星和网络安全。

## 硬性边界

- 宣布赛道得到确认前，必须有同行、产业链、业绩、资本开支、政策或产品证据。
- 渠道调研、未具名订单、产品泄露和跑分在获得支持前均视为未核验。
- 区分全球久期/风险偏好与中国特定政策及国产替代影响。
- 描述技术迁移前，要区分战略意图、原型、量产、工作负载适配、经济性、采用、生态支持和现有企业反应。
- 既追踪替代品，也追踪互补品的价值迁移。某项变化可能压制芯片设计公司，同时有条件地利好代工、先进封装、存储、网络、电力或软件工具。
- 因果表述只能是检验多个解释后的倾向性结论，不能由价格共振直接断言。
