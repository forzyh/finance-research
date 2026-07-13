#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
import time
import urllib.request


UA = "Mozilla/5.0"


def fetch_text(url, encoding="utf-8", timeout=20, referer="https://finance.sina.com.cn/"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode(encoding, errors="replace")


def loads_json_or_jsonp(text):
    text = text.strip()
    if text.startswith("{") or text.startswith("["):
        return json.loads(text)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("no JSON object found")


def clean_text(value):
    if value is None:
        return ""
    value = html.unescape(str(value))
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def parse_time_ts(value, now=None):
    if value is None or value == "":
        return None
    if now is None:
        now = dt.datetime.now().astimezone()
    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 10_000_000_000:
            ts = ts / 1000
        return ts
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return parse_time_ts(int(text), now=now)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S"):
        try:
            return now.tzinfo.localize(dt.datetime.strptime(text, fmt)).timestamp()
        except AttributeError:
            try:
                return dt.datetime.strptime(text, fmt).replace(tzinfo=now.tzinfo).timestamp()
            except ValueError:
                pass
        except ValueError:
            pass
    return None


def ts_to_local_iso(ts):
    if ts is None:
        return ""
    return dt.datetime.fromtimestamp(float(ts)).astimezone().isoformat()


def make_fact_id(source, fact, published_time, url):
    seed = "|".join([clean_text(source), clean_text(published_time), clean_text(url), clean_text(fact)])
    return "fact-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def card(source, fact, when="", url="", data=None, related=None, entrypoint="", raw=None):
    time_ts = parse_time_ts(when)
    published_time = ts_to_local_iso(time_ts) if time_ts is not None else clean_text(when)
    source_url = url or entrypoint
    return {
        "fact_id": make_fact_id(source, fact, published_time, source_url),
        "fact": clean_text(fact),
        "event_time": "",
        "published_time": published_time,
        "timezone": str(dt.datetime.now().astimezone().tzinfo),
        "source_name": source,
        "source_url": source_url,
        "entities": [],
        "discovered_by": "fetch_7x24.py",
        # Compatibility fields retained for older normalizers.
        "time": published_time,
        "time_ts": time_ts,
        "time_quality": "parsed" if time_ts is not None else "missing",
        "source": {"name": source, "url": source_url},
        "data": data or {},
        "related_assets": related or [],
        "entrypoint": entrypoint,
        "source_layer": "fast_news",
        "initial_importance": "medium",
        "verification_status": "unverified",
        "raw": raw or {},
    }


def fetch_eastmoney(limit, cutoff_ts=None, max_pages=6):
    items = []
    sort_end = ""
    page_size = min(max(limit, 50), 100)
    for _ in range(max_pages):
        url = (
            "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
            f"?client=web&biz=web_724&fastColumn=102&sortEnd={sort_end}&pageSize={page_size}&req_trace={int(time.time() * 1000)}"
        )
        data = loads_json_or_jsonp(fetch_text(url))
        block = data.get("data", {})
        rows = block.get("fastNewsList", [])
        if not rows:
            break
        page_items = [
            card(
                "东方财富全球财经快讯",
                row.get("summary") or row.get("title"),
                row.get("showTime"),
                data={"title": row.get("title"), "code": row.get("code"), "realSort": row.get("realSort")},
                related=row.get("stockList") or [],
                entrypoint=url,
                raw=row,
            )
            for row in rows
        ]
        items.extend(page_items)
        sort_end = block.get("sortEnd") or rows[-1].get("realSort") or ""
        if not sort_end:
            break
        oldest = min((i["time_ts"] for i in page_items if i.get("time_ts")), default=None)
        if cutoff_ts and oldest and oldest < cutoff_ts:
            break
        if len(items) >= limit and not cutoff_ts:
            break
    return items[: max(limit, len(items) if cutoff_ts else limit)]


def fetch_sina(limit, cutoff_ts=None, max_pages=6):
    items = []
    page_size = min(max(limit, 20), 50)
    for page in range(1, max_pages + 1):
        url = f"https://app.cj.sina.com.cn/api/news/pc?page={page}&size={page_size}"
        data = json.loads(fetch_text(url))
        rows = data.get("result", {}).get("data", {}).get("feed", {}).get("list", [])
        if not rows:
            break
        page_items = []
        for row in rows:
            ext = {}
            try:
                ext = json.loads(row.get("ext") or "{}")
            except Exception:
                ext = {}
            page_items.append(
                card(
                    "新浪财经7x24",
                    row.get("rich_text"),
                    row.get("create_time"),
                    url=ext.get("docurl") or "",
                    data={"id": row.get("id"), "tag": row.get("tag"), "view_num": row.get("view_num")},
                    related=ext.get("stocks") or [],
                    entrypoint=url,
                    raw=row,
                )
            )
        items.extend(page_items)
        oldest = min((i["time_ts"] for i in page_items if i.get("time_ts")), default=None)
        if cutoff_ts and oldest and oldest < cutoff_ts:
            break
        if len(items) >= limit and not cutoff_ts:
            break
    return items[: max(limit, len(items) if cutoff_ts else limit)]


def quote_js_keys(text):
    return re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)", r'\1"\2"\3', text)


def extract_first_js_object(text, anchor="thsRss"):
    anchor_pos = text.find(anchor)
    start = text.find("{", anchor_pos if anchor_pos >= 0 else 0)
    if start < 0:
        return ""
    depth = 0
    in_string = False
    escape = False
    for pos in range(start, len(text)):
        ch = text[pos]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : pos + 1]
    return ""


def fetch_10jqka(limit, cutoff_ts=None, max_pages=6):
    urls = [
        "http://stock.10jqka.com.cn/thsgd/realtimenews.js",
        "http://stock.10jqka.com.cn/thsgd/ywjh.js",
    ]
    items = []
    seen = set()
    for url in urls:
        text = fetch_text(url, encoding="gb18030")
        js_object = extract_first_js_object(text)
        if not js_object:
            continue
        data = json.loads(quote_js_keys(js_object))
        for row in data.get("item", []):
            key = row.get("seq") or row.get("url") or row.get("title")
            if key in seen:
                continue
            seen.add(key)
            items.append(
                card(
                    "同花顺7x24",
                    row.get("content") or row.get("title"),
                    row.get("pubDate"),
                    url=row.get("url") or "",
                    data={"title": row.get("title"), "source": row.get("source"), "seq": row.get("seq")},
                    related=[x for x in [row.get("stockCode")] if x],
                    entrypoint=url,
                    raw=row,
                )
            )
            if len(items) >= limit:
                return items
    return items[:limit]


def decode_json_string(value):
    try:
        return json.loads(f'"{value}"')
    except Exception:
        return value


def fetch_cls(limit, cutoff_ts=None, max_pages=6):
    url = "https://m.cls.cn/telegraph"
    text = fetch_text(url, referer="https://m.cls.cn/")
    items = []
    seen = set()
    structured = re.finditer(
        r'"shareurl"\s*:\s*"((?:\\.|[^"\\])*)".{0,800}?"ctime"\s*:\s*(\d+).{0,1600}?"content"\s*:\s*"((?:\\.|[^"\\]){20,}?)".{0,800}?"id"\s*:\s*(\d+)',
        text,
        flags=re.S,
    )
    for m in structured:
        shareurl = decode_json_string(m.group(1))
        ctime = int(m.group(2))
        fact = clean_text(decode_json_string(m.group(3)))
        article_id = m.group(4)
        if not fact or fact in seen:
            continue
        seen.add(fact)
        items.append(
            card(
                "财联社电报",
                fact,
                ctime,
                url=shareurl,
                data={"id": article_id},
                entrypoint=url,
            )
        )
        if len(items) >= limit:
            break
    if not items:
        matches = re.finditer(r'"content"\s*:\s*"((?:\\.|[^"\\]){20,}?)"', text)
        for m in matches:
            fact = clean_text(decode_json_string(m.group(1)))
            if not fact or fact in seen:
                continue
            seen.add(fact)
            items.append(card("财联社电报", fact, entrypoint=url))
            if len(items) >= limit:
                break
    if not items:
        raise ValueError("no CLS items parsed from page")
    return items


def fetch_wallstreetcn(limit, cutoff_ts=None, max_pages=6):
    url = "https://wallstreetcn.com/live"
    text = fetch_text(url, referer="https://wallstreetcn.com/")
    matches = re.finditer(
        r'"content_text"\s*:\s*"((?:\\.|[^"\\]){20,}?)".{0,1000}?"display_time"\s*:\s*(\d+)',
        text,
        flags=re.S,
    )
    items = []
    seen = set()
    for m in matches:
        fact = clean_text(decode_json_string(m.group(1)))
        display_time = int(m.group(2))
        if not fact or fact in seen:
            continue
        seen.add(fact)
        items.append(card("华尔街见闻快讯", fact, display_time, entrypoint=url))
        if len(items) >= limit:
            break
    if not items:
        raise ValueError("no WallstreetCN items parsed from page")
    return items


FETCHERS = {
    "eastmoney": fetch_eastmoney,
    "sina": fetch_sina,
    "10jqka": fetch_10jqka,
    "cls": fetch_cls,
    "wallstreetcn": fetch_wallstreetcn,
}


def apply_lookback(items, cutoff_ts):
    if cutoff_ts is None:
        return items
    kept = []
    for item in items:
        ts = item.get("time_ts")
        if ts is None:
            item["time_quality"] = "missing_included"
            kept.append(item)
        elif ts >= cutoff_ts:
            kept.append(item)
    return kept


def main():
    parser = argparse.ArgumentParser(description="Fetch Chinese 7x24 finance news as normalized fact cards.")
    parser.add_argument("--limit", type=int, default=120, help="Target maximum items per source before lookback filtering.")
    parser.add_argument("--lookback-hours", type=float, default=30.0, help="Keep items from this many hours back. Use 0 to disable filtering.")
    parser.add_argument("--max-pages", type=int, default=6)
    parser.add_argument("--sources", default="eastmoney,sina,10jqka,cls,wallstreetcn")
    parser.add_argument("--json", action="store_true", help="Print JSON. Markdown is not implemented; JSON is the stable contract.")
    args = parser.parse_args()

    now = dt.datetime.now().astimezone()
    cutoff_ts = None
    if args.lookback_hours and args.lookback_hours > 0:
        cutoff_ts = (now - dt.timedelta(hours=args.lookback_hours)).timestamp()
    fact_cards = []
    collection_errors = []
    source_counts = {}
    for source in [s.strip() for s in args.sources.split(",") if s.strip()]:
        fetcher = FETCHERS.get(source)
        if not fetcher:
            collection_errors.append({"source": source, "error": "unknown source"})
            continue
        try:
            fetched = fetcher(args.limit, cutoff_ts=cutoff_ts, max_pages=args.max_pages)
            kept = apply_lookback(fetched, cutoff_ts)
            fact_cards.extend(kept)
            source_counts[source] = len(kept)
        except Exception as exc:
            collection_errors.append({"source": source, "error": str(exc)})

    output = {
        "schema_version": 2,
        "news_collection": {
            "generated_at": now.isoformat(),
            "lookback_hours": args.lookback_hours,
            "cutoff_time": ts_to_local_iso(cutoff_ts) if cutoff_ts else "",
            "source_coverage": source_counts,
            "collection_errors": collection_errors,
        },
        "fact_cards": fact_cards,
        "raw_anomalies": [],
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
