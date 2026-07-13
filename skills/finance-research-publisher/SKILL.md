---
name: finance-research-publisher
description: Render the nine-part Chinese finance evening report, including a naturally written long-form “深度洞悉” essay and insight notes, into a polished responsive HTML page; publish it to Lark Miaoda with internet-public no-login access; and send a short URL-only cover email. Use only after factual, causal, abstraction, human-voice editorial, and publication checks have passed, or for local preview and delivery validation without sending.
---

# Finance Research Publisher

## Inputs

Require a publication-ready `final_report.md` and run bundle version 2. Read `references/html-style.md` before changing layout. The public report must already have passed editorial and factual review.

## Local rendering

Run from the current report directory:

```bash
scripts/render_report_html.py \
  --input final_report.md \
  --bundle run_bundle.json \
  --output report.html
```

For an explicitly non-publishable shadow preview, add `--preview`. This flag never bypasses deployment or email gates.

For a delivery cover preview, add `--email-md sender_body.md`. Before a public URL exists, the email file is a preview only and must not be sent.

The renderer validates the nine required sections, creates a fixed editorial navigation, emphasizes the three-part summary, renders market quotes from reader-safe bundle data, and gives 旗舰洞悉 a long-form essay layout. It must never invent a missing section or expose raw bundle structures.

Run `scripts/qa_rendered_html.js --html report.html --output html_qa.json --screenshot-dir html_qa` with a Node runtime that provides Playwright. Require both 1440px desktop and 390px mobile checks to pass before deployment.

## Publication sequence

Only run this sequence after `publication_checks` confirms fresh close data, completed review and publishable copy:

1. Render and visually inspect `report.html` on desktop and mobile.
2. Publish the page:

```bash
scripts/publish_to_lark.py \
  --html report.html \
  --bundle run_bundle.json \
  --report final_report.md \
  --app-name "每日财经晚报 YYYY-MM-DD" \
  --deploy-json lark_deploy.json
```

3. Confirm the deployment record contains a non-empty HTTP(S) URL and confirms public scope with login disabled. If either check fails, stop.
4. Regenerate the short cover with the public URL:

```bash
scripts/render_report_html.py \
  --input final_report.md \
  --bundle run_bundle.json \
  --output report.html \
  --email-md sender_body.md \
  --online-url "<public-url>"
```

5. Send only the Markdown cover. The sender script independently verifies that the deployment is public, login-free, anonymously reachable and identical to the email URL:

```bash
scripts/send_with_sender.py \
  --email-md sender_body.md \
  --deploy-json lark_deploy.json \
  --subject "每日财经晚报 YYYY-MM-DD" \
  --from-name "每日财经晚报" \
  --delivery-json delivery.json \
  --to "recipient@example.com"
```

Do not attach `report.html`.

## Hard gates

- Never send before the public no-login URL is confirmed.
- Keep the email to title, date/window, a 100–300 Chinese-character introduction and one online URL.
- Do not include the full report, Markdown source, tables or attachments in the email.
- Reject public copy containing internal field names, paths, commands, raw codes, Python/JSON structures, Agent/process wording or English workflow states.
- Reject copy that fails the human-voice gate: model self-reference, canned article announcements, generic era framing, repeated mechanical transitions, serial fake contrasts, or slogan endings. Do not mistake passing the static check for a completed editorial read.
- Display market rows only as reader-facing name, price, change and percentage. Skip malformed rows.
- Preserve facts, inference boundaries, sources and disclaimers; do not add investment advice.
- Keep publishing and sending scripts inert during local preview or validation work.
