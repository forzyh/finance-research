---
name: finance-research-news-intake
description: 为研究级中文盘后报告采集并规范化最新财经、科技、公司战略、政策、科学、地缘和社会经济动态，形成可追溯来源的事实卡、市场异常和新兴结构性问题。用于7x24信息流、一手发布、公告、前沿企业动态、跨公司战略共性、双来源洞悉发现或30小时晚报窗口。
---

# 财经研究新闻采集

## 目标

为新闻报道和研究线建立共同的发现层。快讯只能作为线索，不能作为最终证据；采集阶段不得预定旗舰文章结论。

## 流程

1. 需要中文实时快讯时，运行 `scripts/fetch_7x24.py --lookback-hours 30 --limit 120 --json`。
2. 选择信息流、官方来源、公告系统和搜索词前，完整阅读 `references/sources.md`。
3. 默认覆盖最近30小时；只有未决事件、基准比较或多日路径才扩展到72小时。
4. 每项重要论断尽量采集最一手来源；找到一手来源后仍保留最初发现来源。
5. 将有效信息规范为事实卡。只去除同一来源的完全重复项；跨来源的事件级去重交给 `$finance-research-fact-verifier`。
6. 独立于编辑台识别异常：新闻与价格不一致、重大标题下反应平淡、反转、相关资产冲突、时间异常，或论断与近期基准矛盾。
7. 即使没有价格异常，也要识别前沿信号：多家重要主体采取相似战略；新技术能力开始落地；瓶颈改变公司边界；商业模式、监管、标准、人口结构或社会行为开始重塑激励。
8. 按结构性共性而不是关键词聚类前沿信号。单一新闻稿只能保留为事实卡或观察项，除非机制和外部相关性获得独立支持。
9. 只输出有证据支撑的异常观察和候选问题。不得把价格共振、公司意图或有感染力的未来叙事直接写成因果。
10. 失败来源写入 `collection_errors`，不得静默降低覆盖范围。

## v2 输出

在当前 `run_bundle.json` 中写入或合并：

- `schema_version`：`2`；
- `news_collection`：采集窗口、来源覆盖、查询日志和 `collection_errors`；
- `fact_cards`：下述规范事实卡；
- `raw_anomalies`：下述异常记录；
- `frontier_questions`：下述新兴结构性问题。

### 事实卡

必须包含：

- `fact_id`、`fact`、`event_time`、`published_time` 和时区；
- `source_name`、`source_url`、`source_layer` 和 `entrypoint`；
- `data`、`entities`、`related_assets` 和可选的 `tech_subsector`；
- `initial_importance`：`high`、`medium` 或 `low`；
- `verification_status`：`primary_confirmed`、`cross_confirmed` 或 `unverified`；
- `discovered_by`：信息流、查询、分析台或 Agent 标识。

不得用发布时间覆盖事件时间；数字和单位必须能精确追溯到所引来源。

### 原始异常

必须包含：

- `candidate_id`、`research_question` 和 `origin: raw_anomaly`；
- `question_type: market_anomaly`、`observable_trigger`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons` 和 `impact_map`；
- `title`、`observed_pattern` 和 `comparison_baseline`；
- `seed_fact_ids` 和 `affected_assets`；
- `why_unusual`，并尽可能提供至少两个 `competing_hypotheses`；
- 不同的 `evidence_types`、`source_pair` 数组和具体 `benchmark_plan`；
- `evidence_gaps`、`confirmation_signals` 和 `falsification_signals`；
- 对实质相同因果问题稳定一致的 `overlap_key`；
- `verification_status`：核验前通常为 `pending`。

新闻异常与市场异常都使用这一规范候选 DTO。采集时除非已确认来源独立，否则 `source_pair` 保持为空，并设 `base_verified: false`；只有 `$finance-research-fact-verifier` 可在核验后原子替换这些字段。

异常必须写出可观察对比，才有资格进入研究候选池。“这个话题很重要”不构成异常。

### 前沿问题

使用 `origin: frontier_question` 的规范候选 DTO，并要求：

- 具体的 `observable_trigger`，由至少两个独立来源家族或多个独立行动主体支持；
- `question_type`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons` 和 `impact_map`；
- 问题必须从事件上升到一般机制，再落回具体经济后果；
- 至少两个竞争解释，适用时包括实施落差或期权价值解释；
- 与该主题时间范围匹配的证据、基准、确认和证伪方案。

示例：Meta、OpenAI 及其他模型或云企业推进自研 AI 芯片，可以形成关于算力纵向一体化、软硬协同、议价权、供应保障，以及价值如何在加速器厂商、晶圆代工、封装、存储、能源基础设施和 AI 应用成本之间迁移的问题。任务包不得预先写入“自研芯片是必然趋势”这一答案。

## 交接

- 公司与股票标签事实交给 `$finance-research-stock-analyst`；
- 科技事实交给 `$finance-research-tech-analyst`；
- 全部事实卡和异常交给 `$finance-research-fact-verifier`；
- `raw_anomalies` 只有经核验器重估后才能交给选题器。

## 硬性边界

- 重大非官方论断发布前必须有官方来源或两个独立可靠来源。
- 传闻、券商渠道信息和转载必须明确标为未核验。
- 相互冲突的版本分别保留为事实卡，并用同一事件键关联。
- 不得包含投资指令或个性化建议。
