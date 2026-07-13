---
name: finance-research-trend-analyst
description: 将当前 finance-research v2 运行与最近1–7次历史运行比较，同时兼容旧版 v1 bundle，以识别路径依赖、确认、证伪、反转、价格与事实背离以及值得研究的预期差。用于盘后报告回答此前跟踪项哪些得到确认、哪些被推翻、哪些问题应延续到明天。
---

# 财经研究趋势分析

## 目标

解释当天收盘如何改变此前叙事，为新闻台和研究候选池提供历史证据，但不能把反复出现的说法当成事实。

## 流程

1. 阅读 `references/trend-rubric.md`。
2. 接受 v2 和旧版 bundle。读取旧版时，在存在的情况下提取 `fact_cards` 或 `news_collection.items`、原有快照字段、个股/科技观察、趋势、已核验事件和观察清单。
3. 新 bundle 存放在 `work/finance-research-runs/YYYY-MM-DD/`；同日重跑使用带时间戳的子目录。
4. 运行 `scripts/compare_runs.py --current <bundle> --runs-dir work/finance-research-runs --history 7 --json --bundle-output <updated-bundle>`。导入旧历史时把 `--runs-dir` 指向旧运行根目录。脚本原子写入 `run_comparison` 和 `desk_briefs.trend.machine_comparison`，同时保留分析师已有观察与候选。
5. 最近1–3次运行用于判断即时路径，最多7次用于一周背景。
6. 用当前事实和价格检验每个延续项，标记为已确认、减弱、反转、证伪、不变或待定。
7. 识别路径依赖：当天波动是否早于最新标题、反弹是否失败、反应范围是扩散还是收窄。
8. 只有历史比较显示重大矛盾或未解决机制时，才生成候选问题。

## v2 输出

合并写入：

- `schema_version`：规范输出写 `2`；
- `trend_observations`；
- `run_comparison`：历史文件、窗口、冷启动状态和机器比较；
- `desk_briefs.trend`：已确认、已证伪和延续清单；
- `research_candidates`：必要时追加趋势来源候选。

### 趋势观察

必须包含：

- `observation_id`、`trend` 和 `status`：`strengthening`、`weakening`、`reversal`、`confirmed`、`falsified`、`unchanged` 或 `pending`；
- `current_evidence_ids`、`historical_evidence` 和精确比较窗口；
- `affected_assets`、`price_or_sentiment_change` 和 `path_read`；
- `alternative_explanations`、`confidence`、`confirmation_signal` 和 `falsification_signal`。

### 趋势研究候选

使用规范 DTO：`candidate_id`、`origin: desk_question`、`question_type: market_anomaly`、`research_question`、`observable_trigger`、`structural_tension`、至少三个 `required_lenses`、`analysis_horizons`、`impact_map`、`evidence_types`、`competing_hypotheses`、`source_pair`、`benchmark_plan`、`confirmation_signals`、`falsification_signals` 和 `overlap_key`。同时保留 `why_now`、`seed_fact_ids`、历史异常或预期差、受影响资产和证据缺口。在 `$finance-research-fact-verifier` 完成原子核验更新前，设 `verification_status: pending`、`base_verified: false`，并令 `source_pair` 为空。

## 硬性边界

- 历史缺失按冷启动处理。
- 旧的未核验论断不能因为重复出现而升级。
- 可观察顺序与推断机制必须分开。
- 不得仅以提及次数证明市场重要性。
- 明日跟踪尽可能使用可测量条件。
