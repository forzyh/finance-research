---
name: finance-research-publisher
description: 将九部分中文财经晚报（含自然书写的长篇“深度洞悉”和洞悉短评）渲染为精致的响应式 HTML 页面，发布到飞书妙搭并设为互联网公开、免登录访问，再发送只含在线 URL 的短封面邮件。仅用于事实、因果、抽象、真人文风编辑和发布检查全部通过后，或用于不实际发送的本地预览与投递验证。
---

# 财经研究发布器

## 输入

必须提供可直接发布的 `final_report.md` 和版本2的 run bundle。修改版式前完整阅读 `references/html-style.md`。公开报告必须已经通过编辑与事实审查。

## 本地渲染

在当前报告目录运行：

```bash
scripts/render_report_html.py \
  --input final_report.md \
  --bundle run_bundle.json \
  --output report.html
```

明确不可发布的影子预览可增加 `--preview`；该参数绝不能绕过部署或邮件闸门。

预览投递封面时增加 `--email-md sender_body.md`。公开 URL 生成前，邮件文件仅供预览，不得发送。

渲染器要验证九个必需章节，生成固定编辑导航，突出三部分摘要，从适合读者的数据中渲染行情，并为旗舰洞悉提供长文版式。不得虚构缺失章节或暴露原始 bundle 结构。

用带 Playwright 的 Node 运行环境执行 `scripts/qa_rendered_html.js --html report.html --output html_qa.json --screenshot-dir html_qa`。部署前必须同时通过 1440px 桌面端和 390px 移动端检查。

## 发布顺序

只有 `publication_checks` 确认收盘数据新鲜、审查完整且文稿可发布后，才能执行：

1. 渲染 `report.html`，并分别在桌面端与移动端目检。
2. 发布页面：

```bash
scripts/publish_to_lark.py \
  --html report.html \
  --bundle run_bundle.json \
  --report final_report.md \
  --app-name "每日财经晚报 YYYY-MM-DD" \
  --deploy-json lark_deploy.json
```

3. 确认部署记录包含非空 HTTP(S) URL，且访问范围为互联网公开并关闭登录要求。任一检查失败都必须停止。
4. 使用公开 URL 重新生成短封面：

```bash
scripts/render_report_html.py \
  --input final_report.md \
  --bundle run_bundle.json \
  --output report.html \
  --email-md sender_body.md \
  --online-url "<public-url>"
```

5. 只发送 Markdown 封面。发送脚本会独立验证部署为公开、免登录、匿名可访问，且与邮件 URL 完全一致：

```bash
scripts/send_with_sender.py \
  --email-md sender_body.md \
  --deploy-json lark_deploy.json \
  --subject "每日财经晚报 YYYY-MM-DD" \
  --from-name "每日财经晚报" \
  --delivery-json delivery.json \
  --to "recipient@example.com"
```

不得附加 `report.html`。

## 硬闸门

- 公开免登录 URL 未确认前绝不发送邮件。
- 邮件只保留标题、日期/窗口、100–300字导读和一个在线 URL。
- 邮件不得包含完整报告、Markdown 源文、表格或附件。
- 公开文稿出现内部字段、路径、命令、原始代码、Python/JSON 结构、Agent/流程措辞或英文工作流状态时，必须驳回。
- 未通过真人文风闸门的文稿必须驳回，包括模型自指、套路式文章预告、泛泛时代背景、重复机械过渡、连续伪对比或口号结尾。静态检查通过不等于完成编辑目检。
- 行情行只展示读者可理解的名称、价格、涨跌额和涨跌幅；格式异常的行直接跳过。
- 保留事实、推断边界、来源和免责声明，不得添加投资建议。
- 本地预览或验证期间，发布与发送脚本必须保持不执行外部写入。
