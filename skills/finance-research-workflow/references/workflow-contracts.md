# 工作流契约

## 阶段产物

规范 `run_bundle.json` 存在运行根目录，各阶段证据存于：

- `00_intake/`：原始采集、规范事实卡、采集错误；
- `01_market/`：市场快照和新鲜度检查；
- `02_desks/`：政策、个股、科技和全球/商品简报；
- `03_verification/`：趋势比较与已核验事件；
- `04_research/`：候选、入选题目、任务包、报告和审稿；
- `05_editorial/`：摘要材料包和最终 Markdown 报告；
- `06_publish/`：HTML、部署结果、邮件封面和投递结果。

## 候选契约

每个规范候选必须包含 `candidate_id`、`title`、`research_question`、`origin`、`question_type`、`observable_trigger`、`structural_tension`、`required_lenses`、`analysis_horizons`、`impact_map`、`seed_fact_ids`、`source_pair`、`evidence_types`、`competing_hypotheses`、`benchmark_plan`、`confirmation_signals`、`falsification_signals`、`overlap_key`、`base_verified`、`scores` 和 `score_rationale`。`origin` 为 `raw_anomaly`、`desk_question` 或 `frontier_question`。评分前运行 `normalize_candidates.py`；上游不得把私有别名直接传给选题器。

评分上限依次为：结构重要性20、解释力15、证据可得性15、机制可检验性15、跨层影响15、历史可比性10、未来可证伪性10。合格条件包括至少70分、基础核验通过、具体触发点和结构性矛盾、三个分析视角、明确时间范围和影响图、两类证据、两个竞争假设、一套基准、确认与证伪信号，并且不与更高分题目实质重叠。

## 研究任务与报告

任务包含题目、观察截止时间、已核验种子事实、已知冲突、问题类型、结构性矛盾、分析视角、时间范围、影响图、必需证据类别、输出路径和截止时间。报告包含3000–5000字文章，以及抽象原则、假设、时间线、证据、反证、基准、因果与价值迁移图、利益相关方和期限影响、二阶效应、哲学边界、概率性结论、论断和来源。

不得向研究 Agent 暴露预期答案，也不得让研究 Agent 审查自己的因果论断。

## 审稿契约

每份审稿给出 `publish_full`、`publish_note`、`summary_only` 或 `reject`。记录获准、驳回和可进入摘要的 claim ID、事实冲突、因果薄弱点、必要修改、`style_review`、0–100 的 `publication_quality_score` 和可公开摘要。`publish_full` 与 `publish_note` 要求 `style_review.verdict: pass`。只有同时处于获准集合和摘要合格集合的 ID 才能进入 `approved_summary_claims` 及其兼容别名 `approved_research_claims`；所有正文获准论断单独存入 `approved_body_claims`。

主编选择质量最高的 `publish_full` 作为唯一旗舰。其他 `publish_full` 除非因重叠被驳回，否则降为短评；短评最多两篇。

## 公开报告契约

公开报告顺序为：一句话总结；大盘走势；核心原因；重点新闻与热点个股；科技细分赛道；商品与期货；世界经济与地缘；深度洞悉（最多一篇旗舰洞悉和两篇洞悉短评）；未来验证与来源。

公开页面和邮件不得出现路径、脚本名、JSON 字段、原始置信度/状态标签、Agent 指令、来源层标签或投递内部信息。区分事实、推断和判断，但不要反复贴表格式标签。使用自然、具体的中文；拒绝套路开头、机械过渡、装饰性对称、重复结论和泛泛励志结尾。不提供个性化投资建议。

## 运行资格

交易日必须取得当日 A股、港股和国内期货收盘，或明确说明休市原因。美欧数据标明收盘、盘中、早盘或盘前。缺少飞书公开免登录访问属于投递硬失败。
