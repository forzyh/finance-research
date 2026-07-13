---
name: finance-research-policy-desk
description: 为财经简报研究中国及全球宏观政策、监管、财政、货币、产业、消费、卫生、贸易和地缘政策动态。用于把政策发布和市场反应转化为有两个独立来源支持的研究候选，量化政策规模与新意，区分规划与有资金支持的实施，并将合格问题交给财经研究选题器。
---

# 财经研究政策分析台

## 目标

生产证据包和研究问题，不直接写成评论成稿。每个候选必须有两个独立来源；单一来源事项留在观察清单。

## 必读参考

采集或解释政策证据前，完整阅读 [references/policy-source-and-analysis-guide.md](references/policy-source-and-analysis-guide.md)。

## 工作流程

1. 明确观察截止时间和司法辖区。
2. 从政策原文、监管发布、预算文件、统计数据、讲话或立法记录等一手材料开始。
3. 补充第二个独立来源，用于确认重要事实，或独立检验实施进度和市场反应。同源转载、转发或同一来源家族的两个页面不算独立来源。
4. 将每项材料拆分为：
   - 已宣布目标；
   - 有约束力的规则或有资金支持的工具；
   - 实施参数；
   - 已观察的经济或市场反应；
   - 尚未解决的假设。
5. 以相关分母、既有政策、历史基准或市场共识量化规模，估算和压力测试必须标明。
6. 建立至少两个竞争假设和一套基准比较方案，写明确认与证伪信号。
7. 只有通过双来源和基础核验闸门后才能输出候选。规则、制度或长期政策在可测市场影响出现前已经改变激励时，使用 `frontier_question`；其他情况用 `desk_question`。不完整事项进入 `watchlist`。
8. 交接前运行 `python3 scripts/validate_desk_packet.py <packet.json>`。

## 候选闸门

每个候选除统一字段外还必须包含：

- 带时区的 `observation_cutoff`；
- `base_verified: true`；
- `question_type`、`observable_trigger`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons` 和 `impact_map`；
- 至少包含两个独立来源记录的 `source_pair`；
- `verified_facts`，每项重要事实至少引用两个独立 `source_ids`；
- 至少两类 `evidence_types` 和两个 `competing_hypotheses`；
- 可量化的 `benchmark_plan`；
- 非空的 `confirmation_signals` 与 `falsification_signals`；
- `policy_stage`、`novelty_assessment`、`implementation_gap` 和 `affected_assets`。

使用 `origin: desk_question` 或 `frontier_question`。结构性候选还必须说明主导矛盾、受影响的机构与群体、三个分析视角和短中长期范围。不得给出百分制编辑分；评分和70分门槛由 `$finance-research-topic-selector` 负责。

## 交接

输出包含 `desk`、`observation_cutoff`、`candidates` 和 `watchlist` 的精简分析台材料包。保留来源 ID 和精确时间戳，使后续 Agent 无需重建出处即可审查论断。

## 硬性边界

- 目标、规划、征求意见、配额、预算授权、实际拨款、招标和已完成支出是不同事实，必须分别处理。
- 不得只凭标题措辞判断政策力度。
- 未与既有规则或项目比较前，不得声称政策“全新”。
- 不得只凭同日市场变化推断因果。
- 政策事实、量化推断和分析台判断要清楚分开。
- 面向读者的文字不得出现内部字段或置信度标签。
