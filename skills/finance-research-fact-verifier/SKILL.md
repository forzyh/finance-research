---
name: finance-research-fact-verifier
description: 在选题或发布前，对 finance-research v2 的事实卡、市场快照、分析台观察、异常、趋势和研究候选进行去重、交叉核验、排序与冲突检查。用于来源分级、时效检查、事件核验、候选重估或驳回、论断级溯源、市场反应核查，以及区分事实与因果解释。
---

# 财经研究事实核验

## 目标

为新闻线和研究线建立共同的事实底座。本技能负责选题前闸门，不能替代完整研究报告完成后的因果审稿。

## 流程

1. 阅读 `references/verification-rubric.md`。
2. 按主体、时间、主题和核心论断将事实卡归入事件，同时保留全部来源记录。
3. 优先采用官方、交易所、统计部门、公司和一手市场来源。重要的非一手事实至少用两个独立可靠来源交叉确认。
4. 核对时间、金额、政策措辞、主体、单位、价格、交易时段和百分比冲突，不得掩盖未解决差异。
5. 将价格反应作为证据前，先验证快照新鲜度与交易时段标签。
6. 依据引用的 fact ID 检查个股、科技、趋势、政策以及商品与全球分析台的观察。
7. 审查 `raw_anomalies`、`frontier_questions` 和 `research_candidates`。异常必须存在可观察对比；前沿问题必须确认战略共性真实、来源独立，且不只是单家公司宣传。两类候选都要有不同替代解释、可取得证据、明确结构性矛盾，以及可测量的确认与证伪信号。
8. 将每个候选标记为 `eligible`、`needs_evidence`、`duplicate` 或 `rejected` 并说明理由；不得决定最终 1–3 个题目，也不得给出百分制选题分。
9. 运行 `python3 scripts/apply_candidate_verification.py --bundle <bundle.json> --results <verification.json> --output <verified-bundle.json>`，将规范候选的 `base_verified`、`source_pair`、`verification_status` 与 `candidate_verification` 原子更新。
10. 对已核验事件评估编辑价值，并输出一份精简的未决观察清单。

## v2 输出

合并写入：

- `schema_version`：必须为 `2` 并保持不变；
- `verified_events`；
- `verified_fact_index`：以 `fact_id` 或已核验 claim ID 为键的论断级出处；
- `candidate_verification`：每个异常或候选对应一项结果；
- `publication_checks.fact_gate`：通过/失败和阻断冲突；
- `watchlist`：尚未解决但可能重要的事项。

### 已核验事件

必须包含：

- `event_id`、`event`、`verified_fact` 和 `event_time`；
- `source_basis`：来源 ID、URL 和等级；
- `conflicts`、`affected_assets` 和可选的 `tech_subsector`；
- `impact_chain`：明确标注为解释，不得当作事实；
- `market_reaction`：可观察价格及已对齐的时间窗口；
- `trend_status`、1–10 分的 `news_value_score` 和 `confidence`；
- `confirmation_signal` 和 `falsification_signal`。

### 候选核验

必须包含：

- `candidate_id`、`status` 和 `decision_reason`；
- `source_pair`：允许下游使用、且已独立核验的来源记录；
- `verified_seed_fact_ids` 和 `rejected_seed_fact_ids`；
- `source_grade_summary` 和 `market_data_freshness`；
- `observable_trigger`：true 或 false；合格的前沿问题不一定包含价格异常；
- `independent_evidence_types`：证据类别列表；
- `competing_hypotheses_valid`：true 或 false；
- `benchmark_feasible`、`signals_measurable` 和 `overlap_group`；
- `evidence_gaps` 和 `allowed_claim_scope`。

只有核心事实通过、触发点与结构性矛盾定义清楚、至少两类独立证据可取得、存在两个竞争解释、基准比较可行，并在适当期限内提出具体确认与证伪信号，候选才可标为 `eligible`。

每个输入候选必须预先采用规范字段，包括 `origin: raw_anomaly`、`desk_question` 或 `frontier_question`，以及 `question_type`、`observable_trigger`、`structural_tension`、`required_lenses`、`analysis_horizons`、`impact_map`。对于 `eligible`，原子设置 `base_verified: true`，用核验后的独立来源替换 `source_pair`，并设 `verification_status: eligible`。其他状态一律原子设置 `base_verified: false`，且只保留通过核验的来源记录。不得在同一次写入中只改 `base_verified` 而不改 `source_pair`。

## 来源与置信度规则

- High：一手来源，或多个相互独立且结论一致的可靠来源。
- Medium：一个可靠来源加一致数据，或两个一致的非一手来源。
- Low：只有快讯、只有社交媒体、归属不清、价格陈旧，或重大冲突未解决。

## 硬性边界

- 多个信息流转载同一来源，不能据此把快讯线索升级为已确认事实。
- 趋势观察或分析台解释不能单独作为事实证明。
- 没有对齐时间且缺乏区分性证据时，不得声称某条新闻驱动了价格。
- 单位、基准、重述口径或交易时段截止点含糊时，驳回或缩小论断范围。
- 内部核验标签不得进入公开报告；下游编辑负责把获准事实改写为读者语言。
