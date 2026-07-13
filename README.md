# finance-research

一套面向中文财经晚报的 Codex Skills 工作流，重点解决“新闻覆盖充分，但因果研究不够深入”的问题。

工作流从收盘后的新闻与行情采集开始，经政策、个股、科技、商品与全球市场四个分析台生成研究候选；只选择 1–3 个满足证据门槛的问题交给独立研究 Agent，再经因果审稿、摘要回流、主编合稿和发布门禁生成最终报告。

## 核心约束

- 研究候选同时来自原始新闻/价格异常和四个分析台提出的问题。
- 选题采用固定 100 分量表，低于 70 分不得进入深度研究。
- 每个研究 Agent 生成一篇 3,000–5,000 中文字符的内部论文。
- 作者不能审核自己的文章；所有重要 claim 必须逐条审查。
- 只有同时满足“已批准”和“允许进入摘要”的 claim 才能改变一句话总结。
- 没有文章达到旗舰标准时，不强行刊发旗舰文章。
- 飞书页面未确认互联网公开、免登录访问前，禁止发送邮件。
- 邮件只包含短导读和唯一在线 URL，不发送 HTML 附件。

## 技能包

仓库包含 14 个 `finance-research-*` 技能：

- 新闻采集、市场快照、热点个股、科技赛道、趋势分析和事实核验；
- 政策分析台、全球商品与地缘分析台；
- 选题、深度研究和因果审稿；
- 晚报主编、HTML 发布和总工作流编排。

总入口为 [`finance-research-workflow`](skills/finance-research-workflow/SKILL.md)。

## 安装

```bash
python3 scripts/install_skills.py --install
```

脚本会先验证全部技能，再将它们以符号链接安装到 `${CODEX_HOME:-~/.codex}/skills`。它不会替换原有 `finance-*` 技能。

卸载新技能链接：

```bash
python3 scripts/install_skills.py --uninstall
```

## 验证

```bash
python3 scripts/validate_pack.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

历史影子测试需要显式提供原晚报工作区：

```bash
python3 tests/prepare_shadow_2026_07_13.py --workspace /path/to/finance-report-workspace
```

生成的报告、截图、bundle 和邮件预览保存在 `tests/tmp/`，不会进入 Git。

## 使用

安装后，在新的 Codex 任务中调用：

```text
$finance-research-workflow
```

技能包只提供生产流程和发布闸门，不会自动修改现有定时任务。正式接管自动化前，应先完成一次交易日影子运行。

