#!/usr/bin/env python3
"""Render the reviewed nine-part finance evening report as standalone HTML."""

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
from urllib.parse import urlparse


SECTIONS = [
    ("一句话总结", "summary", "01"),
    ("当天大盘行情走势", "market", "02"),
    ("为什么会这样走", "drivers", "03"),
    ("今天重点新闻与热点个股事件", "news", "04"),
    ("科技股与细分赛道", "tech", "05"),
    ("商品与期货", "commodities", "06"),
    ("世界经济与地缘形势", "global", "07"),
    ("核心深挖", "deep", "08"),
    ("明日验证清单与来源", "tomorrow", "09"),
]

ALIASES = {
    "一句话主线": "一句话总结",
    "今日市场复盘": "当天大盘行情走势",
    "核心原因": "为什么会这样走",
    "重点新闻与热点个股": "今天重点新闻与热点个股事件",
    "重点新闻与热点个股事件": "今天重点新闻与热点个股事件",
    "世界经济、地缘形势分析": "世界经济与地缘形势",
    "世界经济与地缘形势分析": "世界经济与地缘形势",
    "明日跟踪清单与来源": "明日验证清单与来源",
}

PUBLIC_TERMS = {
    "high": "高",
    "medium": "中",
    "low": "低",
    "warming": "升温",
    "cooling": "降温",
    "reversal": "反转",
    "confirmed": "已确认",
    "falsified": "已证伪",
    "unverified": "待核实",
    "follow_up": "后续观察",
    "source_basis": "来源依据",
    "confidence": "置信程度",
}

SYMBOL_LABELS = {
    "nf_JD0": "鸡蛋连续", "nf_C0": "玉米连续", "nf_M0": "豆粕连续",
    "nf_LH0": "生猪连续", "nf_SR0": "白糖连续", "nf_CF0": "棉花连续",
    "nf_RB0": "螺纹钢连续", "nf_I0": "铁矿石连续", "nf_CU0": "沪铜连续",
    "nf_AU0": "沪金连续", "nf_SC0": "原油连续", "nf_AG0": "沪银连续",
    "nf_AL0": "沪铝连续", "nf_HC0": "热卷连续", "nf_FG0": "玻璃连续",
}

FORBIDDEN_PUBLIC_PATTERNS = [
    r"run[_ ]bundle", r"delivery_status", r"sender_body", r"final_report",
    r"publication_checks", r"approved_research_claims", r"research_audits",
    r"source_basis", r"follow_up", r"unverified", r"(?:^|\s)/Users/[^\s]+",
    r"\.py\b", r"Agent\b", r"Python\s+dict", r"JSON\s+字段",
]


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, value):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(value)


def esc(value):
    return html.escape("" if value is None else str(value), quote=False)


def esc_attr(value):
    return html.escape("" if value is None else str(value), quote=True)


def public_text(value):
    text = "" if value is None else str(value)
    if text in SYMBOL_LABELS:
        return SYMBOL_LABELS[text]
    for old, new in PUBLIC_TERMS.items():
        text = re.sub(rf"\b{re.escape(old)}\b", new, text, flags=re.I)
    text = re.sub(r"run[_ ]bundle", "历史资料", text, flags=re.I)
    text = re.sub(r"\bAgent\b", "研究团队", text, flags=re.I)
    return text


def sanitize_markdown(markdown):
    text = public_text(markdown)
    text = re.sub(r"`?[^`\n/]*\.py(?:\s+[^`\n]*)?`?", "公开数据处理", text)
    text = re.sub(r"(?:^|\s)/Users/[^\s]+", "", text)
    return text


def normalize_title(title):
    title = title.strip()
    for alias, canonical in ALIASES.items():
        if title == alias or title.startswith(alias + "｜") or title.startswith(alias + "："):
            return canonical
    for canonical, _, _ in SECTIONS:
        if title == canonical or title.startswith(canonical + "｜") or title.startswith(canonical + "："):
            return canonical
    return title


def parse_report(markdown):
    title = "每日财经晚报"
    intro = []
    sections = []
    current = None
    for line in markdown.splitlines():
        h1 = re.match(r"^#\s+(.+)$", line)
        h2 = re.match(r"^##\s+(.+)$", line)
        if h1 and title == "每日财经晚报":
            title = h1.group(1).strip()
            continue
        if h2:
            if current:
                sections.append(current)
            original = h2.group(1).strip()
            current = {"title": normalize_title(original), "display_title": original, "lines": []}
            continue
        (intro if current is None else current["lines"]).append(line)
    if current:
        sections.append(current)
    return title, intro, sections


def validate_sections(sections):
    found = [section["title"] for section in sections]
    required = [item[0] for item in SECTIONS]
    missing = [title for title in required if title not in found]
    duplicates = sorted({title for title in found if found.count(title) > 1 and title in required})
    if missing or duplicates:
        problems = []
        if missing:
            problems.append("缺少栏目：" + "、".join(missing))
        if duplicates:
            problems.append("重复栏目：" + "、".join(duplicates))
        raise ValueError("；".join(problems))
    positions = [found.index(title) for title in required]
    if positions != sorted(positions):
        raise ValueError("九个公共栏目顺序不符合发布模板")


def extract_meta(markdown, fallback_date=None):
    result = {}
    for key, pattern in [
        ("date", r"日期[:：]\s*([^\n]+)"),
        ("window", r"观察窗口[:：]\s*([^\n]+)"),
        ("market_state", r"市场状态[:：]\s*([^\n]+)"),
    ]:
        match = re.search(pattern, markdown)
        if match:
            result[key] = match.group(1).strip().lstrip("-").strip()
    if fallback_date and not result.get("date"):
        result["date"] = fallback_date
    return result


def safe_url(value):
    try:
        parsed = urlparse(value)
        return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""
    except Exception:
        return ""


def inline_markdown(value):
    value = public_text(value)
    links = []

    def replace_link(match):
        url = safe_url(match.group(2))
        if not url:
            return match.group(1)
        links.append(f'<a href="{esc_attr(url)}" rel="noopener noreferrer">{esc(match.group(1))}</a>')
        return f"@@SAFE_LINK_{len(links) - 1}@@"

    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, value)
    value = esc(value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    for index, link in enumerate(links):
        value = value.replace(f"@@SAFE_LINK_{index}@@", link)
    return value


def markdown_blocks(lines):
    output = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line.strip():
            index += 1
            continue

        heading = re.match(r"^(#{3,6})\s+(.+)$", line)
        if heading:
            level = min(len(heading.group(1)), 5)
            output.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            index += 1
            continue

        if re.match(r"^>\s?", line):
            buffer = []
            while index < len(lines) and re.match(r"^>\s?", lines[index]):
                buffer.append(re.sub(r"^>\s?", "", lines[index].rstrip()))
                index += 1
            output.append(f"<blockquote>{inline_markdown(' '.join(buffer))}</blockquote>")
            continue

        if "|" in line and index + 1 < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$", lines[index + 1]):
            header = [cell.strip() for cell in line.strip().strip("|").split("|")]
            index += 2
            rows = []
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            table = ["<div class=\"table-wrap\"><table><thead><tr>"]
            table.extend(f"<th>{inline_markdown(cell)}</th>" for cell in header)
            table.append("</tr></thead><tbody>")
            for row in rows:
                table.append("<tr>")
                table.extend(f"<td>{inline_markdown(cell)}</td>" for cell in row)
                table.append("</tr>")
            table.append("</tbody></table></div>")
            output.append("".join(table))
            continue

        item_match = re.match(r"^\s*(?:[-*]|\d+\.)\s+", line)
        if item_match:
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            while index < len(lines) and re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[index]):
                item = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[index].rstrip())
                items.append(f"<li>{inline_markdown(item)}</li>")
                index += 1
            output.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue

        if re.match(r"^---+\s*$", line):
            output.append("<hr>")
            index += 1
            continue

        buffer = [line]
        index += 1
        while index < len(lines):
            following = lines[index].rstrip()
            if not following.strip():
                break
            if re.match(r"^(#{3,6})\s+", following) or re.match(r"^\s*(?:[-*]|\d+\.)\s+", following):
                break
            if re.match(r"^>\s?", following):
                break
            if "|" in following and index + 1 < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$", lines[index + 1]):
                break
            buffer.append(following)
            index += 1
        output.append("<p>" + "<br>".join(inline_markdown(part) for part in buffer) + "</p>")
    return "\n".join(output)


def plain_text(lines):
    text = " ".join(line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#"))
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[`*_>#|]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def load_bundle(path):
    if not path:
        raise ValueError("--bundle is required")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        raise ValueError(f"could not parse v2 bundle: {error}") from error
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        raise ValueError("bundle must be a Finance Research schema v2 object")
    return data


def validate_bundle_gate(bundle, preview=False):
    checks = bundle.get("publication_checks")
    if not isinstance(checks, dict):
        raise ValueError("bundle is missing publication_checks")
    if preview:
        return
    if checks.get("publication_eligible") is not True:
        raise ValueError("publication_eligible is not true")
    if checks.get("market_fresh") is not True and not checks.get("market_closure_reason"):
        raise ValueError("market freshness or a closure reason is required")


def first_value(mapping, keys):
    if not isinstance(mapping, dict):
        return None
    lowered = {str(key).lower(): value for key, value in mapping.items()}
    for key in keys:
        value = mapping.get(key, lowered.get(key.lower()))
        if value not in (None, "", [], {}):
            return value
    return None


def reader_friendly_name(value):
    if not isinstance(value, (str, int, float)):
        return ""
    name = public_text(value).strip()
    if not name or len(name) > 24 or re.match(r"^(?:sh|sz|hk|nf_)?\d{5,}$", name, flags=re.I):
        return ""
    if re.search(r"[{}\[\]]", name):
        return ""
    return name


def number_text(value, percent=False, signed=False):
    if value in (None, "") or isinstance(value, (dict, list)):
        return ""
    try:
        number = float(str(value).replace(",", "").replace("%", ""))
        if percent or signed:
            text = f"{number:+.2f}"
        else:
            text = f"{number:,.2f}" if abs(number) >= 100 else f"{number:.2f}"
        text = text.rstrip("0").rstrip(".")
        return text + ("%" if percent else "")
    except (TypeError, ValueError):
        text = public_text(value).strip()
        return text if len(text) <= 24 and not re.search(r"[{}\[\]]", text) else ""


def collect_market_rows(bundle, limit=8):
    rows, seen = [], set()
    name_keys = ["name", "label", "asset", "instrument", "指数", "品种"]
    price_keys = ["price", "last", "close", "value", "收盘", "点位", "现价"]
    change_keys = ["change", "delta", "涨跌", "涨跌额"]
    percent_keys = ["pct", "change_pct", "percent", "涨跌幅", "pct_change"]

    def visit(value, depth=0):
        if depth > 5 or len(rows) >= limit:
            return
        if isinstance(value, dict):
            name = reader_friendly_name(first_value(value, name_keys))
            price = number_text(first_value(value, price_keys))
            raw_change = first_value(value, change_keys)
            if isinstance(raw_change, dict):
                change = number_text(raw_change.get("absolute"), signed=True)
                percent = number_text(raw_change.get("percent"), percent=True)
            else:
                change = number_text(raw_change, signed=True)
                percent = number_text(first_value(value, percent_keys), percent=True)
            if name and price and (change or percent) and name not in seen:
                seen.add(name)
                rows.append({
                    "name": name,
                    "price": price,
                    "change": change,
                    "percent": percent,
                })
            for child in value.values():
                visit(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                visit(child, depth + 1)

    for key in ("market_snapshot", "cross_asset_snapshot", "futures_snapshot"):
        if key in bundle:
            visit(bundle[key])
    return rows


def render_market_belt(bundle):
    rows = collect_market_rows(bundle)
    if not rows:
        return ""
    cards = []
    for row in rows:
        move = " ".join(part for part in [row["change"], row["percent"]] if part)
        css_class = "up" if "+" in move or "涨" in move else ("down" if "-" in move or "−" in move or "跌" in move else "")
        cards.append(
            '<div class="quote"><div class="quote-name">{}</div>'
            '<div class="quote-value">{}</div><div class="quote-change {}">{}</div></div>'.format(
                esc(row["name"]), esc(row["price"]), css_class, esc(move or "—")
            )
        )
    return '<div class="market-belt" aria-label="主要市场行情">' + "".join(cards) + "</div>"


def split_h3(lines):
    groups, current = [], {"title": "", "lines": []}
    for line in lines:
        match = re.match(r"^###\s+(.+)$", line)
        if match:
            if current["title"] or any(item.strip() for item in current["lines"]):
                groups.append(current)
            current = {"title": match.group(1).strip(), "lines": []}
        else:
            current["lines"].append(line)
    if current["title"] or any(item.strip() for item in current["lines"]):
        groups.append(current)
    return groups


def render_drivers(lines):
    groups = [group for group in split_h3(lines) if group["title"]]
    if not groups:
        return markdown_blocks(lines)
    cards = []
    chinese_numbers = ["一", "二", "三", "四"]
    for index, group in enumerate(groups[:4], 1):
        clean_title = re.sub(r"^原因(?:[一二三四五六七八九十]|\d+)\s*[｜|:：-]\s*", "", group["title"])
        cards.append(
            f'<article class="driver"><span>原因{chinese_numbers[index - 1]}</span><h3>{inline_markdown(clean_title)}</h3>'
            f'{markdown_blocks(group["lines"])}</article>'
        )
    return '<div class="driver-grid">' + "".join(cards) + "</div>"


def render_deep(lines):
    groups = split_h3(lines)
    flagship_count = sum(1 for group in groups if group["title"].startswith("旗舰研究"))
    note_count = sum(1 for group in groups if group["title"].startswith("研究短评"))
    if flagship_count > 1:
        raise ValueError("核心深挖最多刊发一篇旗舰研究")
    if note_count > 2:
        raise ValueError("核心深挖最多刊发两篇研究短评")
    output = []
    for group in groups:
        title = group["title"]
        if not title:
            output.append(markdown_blocks(group["lines"]))
            continue
        article_class = "flagship" if title.startswith("旗舰研究") else ("research-note" if title.startswith("研究短评") else "research-block")
        output.append(
            f'<article class="{article_class}"><div class="article-kicker">{esc("旗舰研究" if article_class == "flagship" else "研究短评" if article_class == "research-note" else "研究观察")}</div>'
            f'<h3>{inline_markdown(title)}</h3>{markdown_blocks(group["lines"])}</article>'
        )
    return "\n".join(output)


def section_map(sections):
    return {section["title"]: section for section in sections}


def render_section(title, anchor, number, lines):
    if title == "为什么会这样走":
        body = render_drivers(lines)
    elif title == "核心深挖":
        body = render_deep(lines)
    else:
        body = markdown_blocks(lines)
    return (
        f'<section class="section section-{anchor}" id="{anchor}" data-nav-section>'
        f'<header class="section-heading"><span>{number}</span><h2>{esc(title)}</h2></header>{body}</section>'
    )


def render_nav():
    links = []
    for title, anchor, number in SECTIONS:
        label = "总结、行情与原因" if anchor == "summary" else title
        display_number = "01–03" if anchor == "summary" else number
        if anchor in {"market", "drivers"}:
            continue
        links.append(f'<li><a href="#{anchor}"><span>{display_number}</span>{esc(label)}</a></li>')
    return "".join(links)


def build_html(title, meta, sections, bundle, generated_at):
    by_title = section_map(sections)
    lead = plain_text(by_title["一句话总结"]["lines"])
    if not lead:
        raise ValueError("一句话总结不能为空")
    main_sections = []
    main_sections.append(
        '<header class="hero" id="summary" data-nav-section>'
        '<div class="masthead"><div>每日财经晚报</div><time>{}</time></div>'
        '<h1>{}</h1><p class="deck"><b>01｜一句话总结</b><br>{}</p>'
        '<div class="meta"><span>{}</span><span>{}</span><span>{}</span></div>{}</header>'.format(
            esc(meta.get("date", "")), esc(title), inline_markdown(lead),
            esc(meta.get("date", "日期待核定")), esc(meta.get("window", "最近30小时")),
            esc(meta.get("market_state", "收盘复盘")), render_market_belt(bundle)
        )
    )
    for section_title, anchor, number in SECTIONS[1:]:
        main_sections.append(render_section(section_title, anchor, number, by_title[section_title]["lines"]))

    nav = render_nav()
    page_title = esc(title)
    css = """
:root{--paper:#fff;--wash:#f5f7fa;--ink:#162238;--navy:#071f4a;--muted:#60708a;--rule:#cbd5e1;--light:#e5eaf0;--risk:#c8322b;--confirm:#0b8b82;--serif:"Songti SC","STSong","Noto Serif CJK SC",Georgia,serif;--sans:"PingFang SC","Hiragino Sans GB","Noto Sans CJK SC",system-ui,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#eef1f5;color:var(--ink);font:16px/1.8 var(--sans);text-rendering:optimizeLegibility}.progress{position:fixed;z-index:20;left:0;top:0;height:3px;background:var(--risk);width:0}.paper{width:min(1240px,100%);margin:auto;min-height:100vh;background:var(--paper);box-shadow:0 0 40px rgba(7,31,74,.08);display:grid;grid-template-columns:190px minmax(0,1fr)}.sidebar{position:sticky;top:0;height:100vh;border-right:1px solid var(--rule);padding:28px 20px;display:flex;flex-direction:column}.sidebar-title{font:700 17px/1.4 var(--serif);color:var(--navy);letter-spacing:.06em;padding-bottom:17px;border-bottom:1px solid var(--rule)}.toc{list-style:none;padding:12px 0;margin:0;overflow:auto}.toc li{margin:0}.toc a{position:relative;display:grid;grid-template-columns:42px 1fr;gap:3px;padding:10px 0;color:var(--navy);text-decoration:none;font-size:12px;line-height:1.4}.toc a span{font-variant-numeric:tabular-nums;font-weight:700}.toc a.active{font-weight:800}.toc a.active:before{content:"";position:absolute;left:-20px;top:9px;bottom:9px;width:2px;background:var(--risk)}.sidebar-note{margin-top:auto;padding-top:14px;border-top:1px solid var(--rule);color:var(--muted);font-size:11px}.mobile-nav{display:none}main{min-width:0;padding:34px 54px 72px}.masthead{display:flex;align-items:baseline;justify-content:space-between;gap:20px;border-bottom:2px solid var(--navy);padding-bottom:12px;margin-bottom:30px;color:var(--navy);font-weight:700}.masthead div{font:800 clamp(24px,3vw,34px)/1.3 var(--serif);letter-spacing:.06em}.masthead time{white-space:nowrap}.hero{padding-bottom:42px}.hero h1{max-width:850px;margin:0 0 20px;color:var(--navy);font:800 clamp(34px,5vw,58px)/1.14 var(--serif);letter-spacing:-.02em}.deck{max-width:840px;margin:0;color:#263957;font:400 clamp(18px,2.2vw,24px)/1.65 var(--serif)}.deck b{color:var(--navy);font:800 13px/1.5 var(--sans);letter-spacing:.08em}.meta{display:flex;flex-wrap:wrap;gap:8px 18px;margin:20px 0 26px;color:var(--muted);font-size:12px}.market-belt{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}.quote{padding:13px 14px;border-right:1px solid var(--light)}.quote:nth-child(4n){border-right:0}.quote:nth-child(n+5){border-top:1px solid var(--light)}.quote-name{min-height:26px;color:var(--muted);font-size:11px;line-height:1.35}.quote-value{color:var(--navy);font:800 20px/1.3 var(--serif);font-variant-numeric:tabular-nums}.quote-change{font-size:12px}.up{color:var(--confirm)}.down{color:var(--risk)}.section{padding:38px 0 10px;border-top:1px solid var(--rule);scroll-margin-top:20px}.section-heading{display:grid;grid-template-columns:52px 1fr;align-items:baseline;margin-bottom:22px;border-bottom:1px solid var(--navy);padding-bottom:12px}.section-heading span{color:var(--risk);font:800 13px/1 var(--sans);letter-spacing:.08em}.section-heading h2{margin:0;color:var(--navy);font:800 clamp(25px,3vw,34px)/1.25 var(--serif)}.section p{margin:0 0 1.15em;max-width:820px}.section h3{margin:28px 0 12px;color:var(--navy);font:800 23px/1.4 var(--serif)}.section h4{margin:23px 0 9px;color:var(--navy);font:800 17px/1.4 var(--serif)}.section h5{margin:18px 0 8px;color:var(--navy);font-size:15px}.section ul,.section ol{max-width:820px;padding-left:1.35em}.section li{margin:.45em 0}a{color:var(--navy);text-underline-offset:3px}blockquote{max-width:820px;margin:24px 0;padding:17px 20px;border-left:4px solid var(--navy);background:var(--wash);font:600 17px/1.75 var(--serif)}code{padding:.1em .3em;background:var(--wash);border-radius:3px}.driver-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--navy);border-bottom:1px solid var(--navy)}.driver{padding:20px}.driver:first-child{padding-left:0}.driver+.driver{border-left:1px solid var(--rule)}.driver>span{color:var(--risk);font-size:11px;font-weight:800;letter-spacing:.08em}.driver h3{margin:4px 0 10px;font-size:19px}.driver p{font-size:13px;line-height:1.72}.table-wrap{max-width:100%;margin:22px 0;overflow-x:auto;border:1px solid var(--rule)}table{width:100%;min-width:620px;border-collapse:collapse;font-size:13px}th,td{padding:10px 12px;border:1px solid var(--rule);text-align:left;vertical-align:top}thead th{background:var(--navy);color:#fff}.section-deep{padding-top:50px}.flagship{margin:18px -22px 42px;padding:34px 44px 46px;border-top:3px solid var(--navy);border-bottom:1px solid var(--navy);background:linear-gradient(180deg,#f8fafc 0,#fff 180px)}.article-kicker{color:var(--risk);font-size:11px;font-weight:800;letter-spacing:.16em}.flagship>h3{max-width:780px;margin:8px 0 26px;font-size:clamp(30px,4vw,45px);line-height:1.2}.flagship p,.flagship ul,.flagship ol,.flagship blockquote{max-width:760px;margin-left:auto;margin-right:auto}.flagship p{font:17px/1.95 var(--serif)}.flagship h4,.flagship h5{max-width:760px;margin-left:auto;margin-right:auto}.flagship h4{padding-top:18px;border-top:1px solid var(--light);font-size:21px}.research-note{max-width:820px;margin:28px 0;padding:23px 0;border-top:1px solid var(--navy);border-bottom:1px solid var(--rule)}.research-note>h3{margin:5px 0 13px}.research-note p{font-size:15px}.research-block{max-width:820px}.section-tomorrow{margin-top:30px}.disclaimer{margin-top:44px;padding-top:18px;border-top:1px solid var(--rule);color:var(--muted);font-size:11px}.footer{display:flex;justify-content:space-between;gap:20px;margin-top:20px;color:var(--muted);font-size:11px}
@media(max-width:980px){body{background:#fff}.paper{display:block;box-shadow:none}.sidebar{display:none}.mobile-nav{position:sticky;z-index:10;top:0;display:flex;gap:18px;padding:10px 16px;overflow-x:auto;border-bottom:1px solid var(--rule);background:rgba(255,255,255,.96)}.mobile-nav a{color:var(--navy);text-decoration:none;white-space:nowrap;font-size:12px}.mobile-nav a.active{color:var(--risk);font-weight:800}main{padding:28px 24px 60px}}
@media(max-width:680px){main{padding:20px 18px 50px}.masthead{align-items:flex-start}.masthead div{font-size:25px}.hero h1{font-size:36px}.market-belt{grid-template-columns:repeat(2,minmax(0,1fr))}.quote:nth-child(2n){border-right:0}.quote:nth-child(n+3){border-top:1px solid var(--light)}.driver-grid{grid-template-columns:1fr}.driver,.driver:first-child{padding:18px 0}.driver+.driver{border-left:0;border-top:1px solid var(--rule)}.section-heading{grid-template-columns:42px 1fr}.section-heading h2{font-size:26px}.flagship{margin:14px -8px 34px;padding:27px 18px 36px}.flagship>h3{font-size:31px}.flagship p{font-size:16px;line-height:1.9}.footer{display:block}}
@media print{body{background:#fff}.paper{display:block;width:auto;box-shadow:none}.sidebar,.mobile-nav,.progress{display:none}main{padding:0}.section{break-inside:auto}.flagship{margin-left:0;margin-right:0;background:#fff}}
"""
    mobile_links = "".join(f'<a href="#{anchor}">{esc(title)}</a>' for title, anchor, _ in SECTIONS if anchor not in {"market", "drivers"})
    script = """
const bar=document.querySelector('.progress');const links=[...document.querySelectorAll('.toc a,.mobile-nav a')];
function update(){const h=document.documentElement;const max=h.scrollHeight-innerHeight;bar.style.width=(max?scrollY/max*100:0)+'%';let active='summary';document.querySelectorAll('[data-nav-section]').forEach(s=>{if(s.getBoundingClientRect().top<innerHeight*.34)active=s.id});links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+active))}
addEventListener('scroll',update,{passive:true});addEventListener('resize',update);update();
"""
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071f4a"><title>{page_title}</title><style>{css}</style></head>
<body><div class="progress" aria-hidden="true"></div><nav class="mobile-nav" aria-label="章节导航">{mobile_links}</nav><div class="paper"><aside class="sidebar"><div class="sidebar-title">本报告导航</div><ol class="toc">{nav}</ol><div class="sidebar-note">收盘总结 · 研究审稿 · 次日验证<br>本文不构成个性化投资建议。</div></aside><main>{''.join(main_sections)}<p class="disclaimer">本报告区分公开事实、研究推断与编辑判断，仅供信息参考，不构成任何个性化投资建议或交易指令。</p><footer class="footer"><span>每日财经晚报</span><span>更新时间：{esc(generated_at)}</span></footer></main></div><script>{script}</script></body></html>'''


def build_email(title, meta, sections, online_url=None):
    by_title = section_map(sections)
    lead = plain_text(by_title["一句话总结"]["lines"])
    market = plain_text(by_title["当天大盘行情走势"]["lines"])
    guide = re.sub(r"\s+", " ", (lead + " " + market)).strip()
    if len(guide) < 100:
        guide += " 本期从收盘结构、政策与公司事件、科技赛道、商品期货以及海外市场交叉核对当日主线，并列出下一交易时段用于确认或证伪当前判断的关键观察项。"
    guide = guide[:300].rstrip("，；。 ") + "。"
    lines = [
        f"# {title}", "",
        f"日期：{meta.get('date', '')}",
        f"观察窗口：{meta.get('window', '最近30小时')}", "", guide,
    ]
    if online_url:
        url = safe_url(online_url)
        if not url:
            raise ValueError("在线地址必须是有效的 HTTP(S) 公开链接")
        lines.extend(["", url])
    return "\n".join(lines).strip() + "\n"


def assert_no_public_leaks(value):
    violations = [pattern for pattern in FORBIDDEN_PUBLIC_PATTERNS if re.search(pattern, value, flags=re.I | re.M)]
    if violations:
        raise ValueError("公共稿仍包含内部实现信息，请先完成发布级文字审查")


def main():
    parser = argparse.ArgumentParser(description="Render a reviewed finance research evening report.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--preview", action="store_true", help="Render locally without requiring publication eligibility.")
    parser.add_argument("--email-md")
    parser.add_argument("--online-url")
    parser.add_argument("--title")
    parser.add_argument("--date")
    parser.add_argument("--variant", choices=["auto", "report"], default="auto")
    args = parser.parse_args()

    markdown = sanitize_markdown(read_text(args.input))
    assert_no_public_leaks(markdown)
    title, _, sections = parse_report(markdown)
    validate_sections(sections)
    if args.title:
        title = args.title
    meta = extract_meta(markdown, fallback_date=args.date)
    bundle = load_bundle(args.bundle)
    validate_bundle_gate(bundle, preview=args.preview)
    generated_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    document = build_html(title, meta, sections, bundle, generated_at)
    assert_no_public_leaks(document)
    write_text(args.output, document)
    if args.email_md:
        email = build_email(title, meta, sections, args.online_url)
        assert_no_public_leaks(email)
        write_text(args.email_md, email)
    print(json.dumps({"html": os.path.abspath(args.output), "email_md": os.path.abspath(args.email_md) if args.email_md else None, "sections": len(SECTIONS)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"render failed: {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
