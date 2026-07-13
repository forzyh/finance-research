---
name: finance-research-workflow
description: 编排带“深度洞悉”研究线、具有自然作者感的中文盘后财经报告，覆盖广泛采集、隔离研究 Agent、因果/抽象/文风审查、摘要回流、主编合稿、HTML 质检、飞书公开发布和只含 URL 的邮件投递。用于完整《每日财经晚报》流程、前沿问题分析、影子运行、历史回放或120分钟硬截止下的阶段恢复。
---

# 财经研究工作流

## 运行契约

运行流程前完整阅读 `references/workflow-contracts.md`。创建或验证 bundle 时使用 `references/run-bundle-v2.schema.json`。实现标签和内部状态字段不得进入公开稿。

工作流负责编排与闸门，领域技能负责分析，发布器负责渲染与投递。不得用写稿代替缺失的研究或核验阶段。

## 生产流程

1. 运行 `scripts/init_run.py --runs-dir <runs-dir> --date YYYY-MM-DD` 创建运行目录。
2. 读取此前1–7个 bundle。趋势比较前用 `scripts/normalize_bundle.py` 规范旧版 bundle。
3. 运行 `$finance-research-news-intake` 和 `$finance-research-market-snapshot`，生成 `fact_cards`、`market_snapshot`、`raw_anomalies` 和 `frontier_questions`。前沿发现覆盖技术、公司战略、制度、商业模式、人口、科学和社会经济变化，不局限于已反映在价格中的财经异常。
4. 并发槽允许时，并行运行四个分析台：`$finance-research-policy-desk`、`$finance-research-stock-analyst`、`$finance-research-tech-analyst` 和 `$finance-research-global-commodities-desk`。
5. 运行 `$finance-research-trend-analyst` 和 `$finance-research-fact-verifier`。基础核验可以驳回研究候选或降低其权重。
6. 合并原始异常、分析台问题和前沿问题。先运行 `scripts/normalize_candidates.py`，由 `$finance-research-topic-selector` 填写规范分数和理由，再运行 `scripts/select_topics.py`；选择零至三个合格且互不重复的题目。不得让低于闸门的题目强行入选，也不得要求一定存在当日价格变化。
7. 运行 `scripts/build_assignments.py`。每个入选题目分派一个隔离的洞悉 Agent。只提供任务包、已核验种子事实、观察截止时间和 `$finance-research-deep-dive`（“深度洞悉”的内部 skill ID），不得提供预期结论。
8. 每个洞悉 Agent 必须返回完整内部报告和机器可读论断，包括抽象原则、跨期限影响图、价值迁移、二阶效应与哲学边界。迟交或不完整报告不得成为旗舰文章。
9. 每篇报告及其来源都要单独交给 `$finance-research-causal-reviewer` 审查。新事实、因果论断、抽象步骤、受益/受损影响、估值桥梁和公开文风必须通过后，才能进入摘要或公开文章。
10. 运行 `scripts/merge_research.py` 汇总审稿结论和获准论断。生成摘要时只能使用 `approved_summary_claims`；`approved_research_claims` 是兼容别名，内容必须完全一致。
11. 运行 `$finance-research-evening-editor`。最多发布一篇完整“旗舰洞悉”和两篇“洞悉短评”；没有报告合格时仍保留“深度洞悉”章节，但以克制的空状态呈现。
12. 依次运行 `scripts/finalize_content.py` 和 `scripts/validate_publication.py`。验证器阻止明显模型自指、套路开头/结尾和过度模板化脚手架；段落节奏和判断仍由人工式编辑把关。全部通过后才调用 `$finance-research-publisher`。发送只含 URL 的封面邮件前，必须获得匿名、免登录的公开 URL。

## 时间安排与降级

- T+0–15：历史、采集和市场快照；
- T+15–30：四个分析台、趋势比较、基础核验和候选生成；
- T+30–75：一至三个研究 Agent；
- T+75–95：因果审稿、获准论断回流和编辑；
- T+95–105：渲染、视觉质检、公开访问检查和投递；
- T+120：硬截止，迟交报告不得发布。

没有题目通过时，只发布已核验的市场与新闻报告，不强凑旗舰文章。高质量前沿问题可以跨多次运行持续研究，确认窗口不必局限于下一交易日。关键交易日收盘数据陈旧时，将本次运行标为不可发布。公开访问失败时不得发送邮件。

## 确定性脚本

- `init_run.py`：创建 v2 运行与阶段目录；
- `normalize_bundle.py`：将旧 bundle 转换为 v2 外壳，不虚构研究输出；
- `normalize_candidates.py`：把各类异常和分析台产物映射到唯一规范候选 DTO；
- `select_topics.py`：调用选题器的资格和评分规则，去重并选择候选；
- `build_assignments.py`：创建隔离研究 Agent 任务包；
- `merge_research.py`：应用审稿结论，建立获准论断信息流；
- `finalize_content.py`：原子标记只有数据新鲜、审查完成且适合公开的报告可被渲染；
- `validate_publication.py`：执行时效、研究出处、公开稿和邮件闸门。
