---
name: finance-research-causal-reviewer
description: 独立审查供编辑使用的财经“深度洞悉”内部文章。用于核查证据、因果关系、抽象推演、估值桥梁和不确定性，判断文字是否自然、是否存在模板化或“AI味”，给出四种发布结论之一，并确保摘要只能使用明确获准的论断。
---

# 财经研究因果审稿

## 目标

以独立、对抗性审稿人的身份逐条检查论断，防止把听起来合理的叙事误写成已经证实的因果关系。

## 独立性闸门

不得由同一个 Agent 或同一角色审查自己写的报告。审稿记录中的 `report_id`、`topic_id`、`author_id` 必须与报告完全一致，`reviewer_id` 必须不同。无法确认身份或独立性时，退回重新分派，不得批准任何论断。

## 必读参考

审稿前完整阅读 [references/causal-review-rubric.md](references/causal-review-rubric.md)。

## 四层审查

1. **L1 事实与来源：** 核对表述、出处、来源独立性、冲突和时效性。
2. **L2 数字、时间与可比性：** 复算关键数字；对齐时区、交易时段、合约、单位、币种和修订口径。
3. **L3 机制与边界：** 检验时间先后、抽象链条、作用机制、替代解释、混杂因素、价值迁移、期限变化、反馈回路、反证、基准概率和可证伪性。
4. **L4 解释、文风与发布：** 质疑宿命论、无依据的估值跳跃、伪精确、哲学拔高、臆测动机、内部术语、模板化表达、虚假对称、重复脚手架以及缺乏依据的摘要压缩。

每项重要论断都要经过四层审查，并给出唯一结论：`approved`、`qualified`、`revise` 或 `rejected`。

## 四种审稿结论

只能给出一种总体结论：

- `publish_full`：完成所列非实质性修改后，可完整刊发为旗舰洞悉；
- `publish_note`：只能压缩为辅助短评刊发；
- `summary_only`：只有明确批准的论断可以进入摘要或简要原因；
- `reject`：该报告任何内容均不得公开刊发。

总体结论不等于自动批准任何具体论断。

## 摘要硬闸门

`abstract_claim_ids` 和 `summary_claim_ids` 只能来自结论恰为 `approved` 且 `summary_eligible` 为 true 的论断。`qualified`、`revise`、`rejected`、未解决或未审查的内容不得进入任何公开摘要。编辑可以在不强化原意的前提下缩写；实质性改写必须重新审查。

## 工作流程

1. 不依赖作者结论，重新建立“来源—论断”映射。
2. 复算所有关系到主论点的数字，并核对观察截止时间。
3. 以最强形式重述至少一个替代解释，指出哪些证据可以区分它与首选解释。
4. 从触发事实、一般原则、作用机制到经济后果，重建抽象阶梯；标出所有跨级跳跃、范畴错误和期限偷换。
5. 分别审查各利益相关方的影响。涉及相关论断时，必须明确写出从战略意图到技术可行性、采用、单位经济、产业结构、盈利和估值的桥梁。
6. 每项重要论断只审一次，但必须完整经过 L1–L4，并给出结论；不得引入未知 claim ID。
7. 在不改变论断边界的前提下单独审文风。将 `style_review.verdict` 标为 `pass` 或 `revise`，记录模板化短语、段落模式、伪平衡、抽象填充和具体修改要求。
8. 输出获准与驳回的 claim ID、事实冲突、因果薄弱点和必要修改。
9. 按评分表给出四种总体结论之一。`publish_full` 和 `publish_note` 在修改后都必须满足 `style_review.verdict: pass`。
10. 对每个非 `reject` 结论按评分表给出 0–100 的 `publication_quality_score`；不得沿用选题分数。
11. 只用获准且可进入摘要的 claim ID 起草可公开摘要，再改成直接、自然的中文。
12. 交接前运行 `python3 scripts/validate_audit.py <audit.json> --report <report.json>`。

## 必需输出

返回 `report_id`、`topic_id`、`author_id`、`reviewer_id`、总体 `verdict`，并为所有非 reject 结论提供 `publication_quality_score`；同时返回 `claim_reviews`、`approved_claim_ids`、`rejected_claim_ids`、`factual_conflicts`、`causal_weaknesses`、`required_edits`、`style_review`、`public_safe_abstract`、`abstract_claim_ids` 和 `summary_claim_ids`。

只有 `approved_claim_ids` 可以进入 `approved_research_claims`。选题由 `$finance-research-topic-selector` 评分，不得事后修改其百分制得分。

## 硬性边界

- 价格同向变化只是证据，不自动构成因果关系。
- 价格没有明显反应，不能证明相关方意图温和，也不能证明最终风险较低。
- 多家公司采取同一战略只能证明意图存在共性，不能证明技术成功、经济性更优、趋势必然或现有龙头将被替代。
- 判断谁受益、谁受损时，必须写明传导渠道、时间范围、应对选项以及影响方向可能反转的条件。
- 哲学框架可以组织证据，不能替代证据。无法回到可测量主体和机制的宏大判断应予驳回。
- 不得靠闲聊式填充、每节设问、表演式第一人称或无依据的确定语气来“去AI味”。自然文风来自取舍、具体行动者、节奏和比例。
- 官方声明只能证实“官方说了什么”，不能自动证实其中的预测或归因为真。
- 即便计算无误，日期、合约或分母不同也会使结论失效。
- 不得用含糊限定语掩盖重大冲突。
- 不得仅因总体结论为 `publish_full` 就批准某句摘要。
