---
name: finance-research-stock-analyst
description: 盘后分析信息量较高的 A股、港股、美股及全球个股，把个股事件转化为 finance-research v2 的已核验分析台观察与研究问题候选。用于异常涨跌、高成交、公告、交易所问询、业绩、回购、大宗交易、内部人或股东变动、龙头确认、主题扩散、风险重估或炒作退潮。
---

# 财经研究热点个股分析

## 目标

解释入选个股对公司基本面、行业结构和市场预期透露了什么，同时产出精简个股简报和可供深入研究的问题候选。

## 流程

1. 阅读 `references/stock-hotspot-rubric.md`。
2. 从事实卡、涨跌幅榜、成交额、公告、问询、龙虎榜、大宗交易、回购、持仓变化、历史重复样本和相关海外走势中建立候选池。
3. 选出信息价值最高的 3–8 个个股或逻辑一致的集群，不得只按涨跌幅排序。
4. 建立事件时间线：价格何时变化、信息何时公开、预期是否提前显现。
5. 用公告、交易所材料、公司投资者关系资料或可靠独立证据核验公司层驱动因素，传闻单独处理。
6. 先比较龙头、同行、落后者和产业链公司，再判断板块是否扩散。
7. 将观察分类为 `leader_confirmation`、`theme_diffusion`、`risk_repricing`、`speculation_retreat`、`macro_sensitive` 或 `idiosyncratic`。
8. 当个股证据暴露重大预期差或矛盾、需要检验假设时，提炼市场研究问题。
9. 多家公司或一家系统重要公司显示企业边界、技术控制、资本强度、商业模式、生态权力或产业价值分配可能持久变化时，提炼 `frontier_question`；管理层叙事之外必须有独立证据。

## v2 输出

合并写入：

- `schema_version`：必须为 `2` 并保持；
- `stock_observations`：3–8 条高信号观察；
- `desk_briefs.stock_events`：分析台摘要、证据缺口和下一交易时段检查项；
- `research_candidates`：追加个股分析台问题候选；
- `frontier_questions`：追加通过结构性闸门的公司战略问题。

### 个股观察

必须包含：

- `observation_id`、`stock`、`ticker`、`market` 和 `event_time`；
- `move_or_attention`、`turnover_or_volume`，以及相对披露时间；
- `verified_driver`、`source_fact_ids` 和 `source_urls`；
- `theme`、可选的 `tech_subsector`、同行证据和产业链位置；
- `classification`、`stock_read`、`theme_read`、`risk_flags` 和 `confidence`；
- `confirmation_signals` 与 `falsification_signals`。

### 分析台研究候选

必须包含：

- `candidate_id`、`origin: desk_question`、`research_question` 和 `why_now`；
- `question_type`、`observable_trigger`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons` 和 `impact_map`；
- `seed_fact_ids`、`anomaly_or_expectation_gap` 和 `affected_assets`；
- 至少两个 `competing_hypotheses`；
- `evidence_types`：标明不同证据类型，而不只是来源数量；
- `source_pair`：除非已确认来源独立，否则初始为空；
- `benchmark_plan`、`evidence_gaps`、`confirmation_signals` 和 `falsification_signals`；
- 稳定的 `overlap_key`、`verification_status: pending` 和 `base_verified: false`。

新 v2 候选不得输出 `stock_desk`、`alternative_hypotheses` 或 `evidence_types_available` 别名。`base_verified` 和 `source_pair` 的原子更新由 `$finance-research-fact-verifier` 负责。

不得给出最终百分制选题分；核验后由 `$finance-research-topic-selector` 评分。

`frontier_question` 使用 `origin: frontier_question`，以具体战略触发点替代预期差要求。影响分析不能停留在焦点个股，还要追踪竞争者、互补方、供应商、客户、资本需求、监管和可能的社会影响。

## 交接

- 科技集群交给 `$finance-research-tech-analyst`；
- 观察与候选交给 `$finance-research-fact-verifier`；
- 被驳回或未解决的个股保留为观察项，不得用来填充报告。

## 硬性边界

- 不得从一个个股的大幅波动推断板块趋势。
- 澄清公告、问询、异常波动公告和减持计划都属于重要反证。
- 标题利润增长必须与经常性利润、现金流、基数效应和市场预期分开。
- 避免买卖措辞和个性化投资建议。
