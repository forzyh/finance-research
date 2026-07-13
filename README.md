# finance-research

一套面向中文财经晚报的 Codex Skills 工作流，重点解决“新闻覆盖充分，但缺少能解释未来的结构性洞悉”的问题。

全部 `SKILL.md`、直接引用的 Markdown 规则和 Agent 界面提示均以中文书写，方便人工逐项检查；JSON 字段、枚举值、脚本名和命令行接口保留英文，以维持机器契约稳定。

工作流从收盘后的新闻、行情和前沿变化采集开始，经政策、个股、科技、商品与全球市场四个分析台生成候选；只选择 1–3 个满足证据门槛的问题交给独立洞悉 Agent，再经事实、因果、抽象层级和影响链审稿，回流摘要并生成最终报告。

## 核心约束

- 洞悉候选来自三类入口：原始新闻/价格异常、四个分析台问题、没有明显盘面异动但可能改变未来的新兴结构性议题。
- 选题采用固定 100 分量表，优先衡量结构重要性、解释力、跨层影响和未来可验证性；低于 70 分不得进入深度洞悉。
- 每个洞悉 Agent 生成一篇 3,000–5,000 中文字符的内部论文，从触发点抽象出一般原则，再回到企业、产业、资本市场、政策和社会后果。
- “哲学视角”必须以事实和机制为锚，讨论稀缺、控制、依赖、专业化、协调、标准或权力，不能用宏大叙事替代证据。
- 终稿采用有作者判断的自然中文：不写套话开场，不强求正反对称，不用机械转场填充段落，也不以空泛升华收尾。
- 作者不能审核自己的文章；所有重要 claim 必须逐条审查。
- 只有同时满足“已批准”和“允许进入摘要”的 claim 才能改变一句话总结。
- 没有文章达到旗舰标准时，不强行刊发旗舰文章。
- 飞书页面未确认互联网公开、免登录访问前，禁止发送邮件。
- 邮件只包含短导读和唯一在线 URL，不发送 HTML 附件。

## 技能包

仓库包含 14 个 `finance-research-*` 技能：

- 新闻采集、市场快照、热点个股、科技赛道、趋势分析和事实核验；
- 政策分析台、全球商品与地缘分析台；
- 选题、深度洞悉和因果/抽象审稿；
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
