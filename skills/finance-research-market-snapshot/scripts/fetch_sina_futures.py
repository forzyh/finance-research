#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36"

WATCHLISTS = {
    "agriculture": {
        "nf_JD0": "鸡蛋连续",
        "nf_C0": "玉米连续",
        "nf_M0": "豆粕连续",
        "nf_A0": "豆一连续",
        "nf_Y0": "豆油连续",
        "nf_P0": "棕榈油连续",
        "nf_RM0": "菜粕连续",
        "nf_SR0": "白糖连续",
        "nf_CF0": "棉花连续",
        "nf_AP0": "苹果连续",
        "nf_LH0": "生猪连续",
    },
    "black": {
        "nf_RB0": "螺纹钢连续",
        "nf_HC0": "热卷连续",
        "nf_I0": "铁矿石连续",
        "nf_J0": "焦炭连续",
        "nf_JM0": "焦煤连续",
        "nf_FG0": "玻璃连续",
        "nf_SA0": "纯碱连续",
    },
    "energy_chem": {
        "nf_SC0": "上海原油连续",
        "nf_FU0": "燃油连续",
        "nf_PG0": "LPG连续",
        "nf_TA0": "PTA连续",
        "nf_MA0": "甲醇连续",
        "nf_V0": "PVC连续",
        "nf_L0": "聚乙烯连续",
    },
    "metals": {
        "nf_CU0": "铜连续",
        "nf_AL0": "铝连续",
        "nf_ZN0": "锌连续",
        "nf_NI0": "镍连续",
        "nf_AU0": "黄金连续",
        "nf_AG0": "白银连续",
    },
}
WATCHLISTS["core"] = {
    **WATCHLISTS["agriculture"],
    **WATCHLISTS["black"],
    **WATCHLISTS["energy_chem"],
    **WATCHLISTS["metals"],
}


def parse_float(value):
    try:
        parsed = float(value)
        return parsed if parsed != 0 else None
    except Exception:
        return None


def fetch(symbols):
    list_arg = ",".join(symbols)
    url = "https://hq.sinajs.cn/list=" + urllib.parse.quote(list_arg, safe=",_")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        text = resp.read().decode("gb18030", errors="replace")
    return url, text


def parse_quote(symbol, raw_value, fallback_name):
    fields = raw_value.split(",")
    name = fields[0] if fields else fallback_name
    quote_time = fields[1] if len(fields) > 1 else ""
    trade_date = fields[17] if len(fields) > 17 else ""
    last = parse_float(fields[8] if len(fields) > 8 else "") or parse_float(fields[6] if len(fields) > 6 else "")
    previous = parse_float(fields[10] if len(fields) > 10 else "")
    change = None
    change_pct = None
    if last is not None and previous:
        change = round(last - previous, 4)
        change_pct = round((last - previous) / previous * 100, 4)
    quote_timestamp = f"{trade_date} {quote_time}".strip()
    snapshot_id = "snapshot-" + hashlib.sha256(
        f"sina-futures|{symbol}|{quote_timestamp}".encode("utf-8")
    ).hexdigest()[:16]
    return {
        "snapshot_id": snapshot_id,
        "asset": name or fallback_name,
        "symbol": symbol,
        "market": fields[15] if len(fields) > 15 else "",
        "session": "china_futures_continuous",
        "price": last,
        "change_absolute": change,
        "change_percent": change_pct,
        "currency": "CNY",
        "unit": "contract_quote",
        "quote_time": quote_timestamp,
        "source_name": "新浪期货行情",
        "source_url_or_endpoint": "https://hq.sinajs.cn/",
        "observation": "",
        "possible_context": [],
        # Compatibility fields retained for legacy readers.
        "change": {"absolute": change, "percent": change_pct},
        "time": quote_timestamp,
        "source": {"name": "新浪期货行情", "url": "https://hq.sinajs.cn/"},
        "interpretation": "",
        "data_quality": "live" if last is not None else "missing",
        "raw_fields": fields,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch Sina Chinese futures continuous-contract snapshot.")
    parser.add_argument("--watchlist", default="core", choices=sorted(WATCHLISTS))
    parser.add_argument("--symbols", default="", help="Comma-separated Sina symbols. Overrides --watchlist.")
    parser.add_argument("--json", action="store_true", help="Print JSON. JSON is the stable output contract.")
    args = parser.parse_args()

    if args.symbols.strip():
        names = {s.strip(): s.strip() for s in args.symbols.split(",") if s.strip()}
    else:
        names = WATCHLISTS[args.watchlist]

    generated_at = dt.datetime.now(dt.timezone.utc).astimezone().isoformat()
    output = {
        "snapshot_cards": [],
        "collection_errors": [],
    }

    try:
        url, text = fetch(names.keys())
        output["entrypoint"] = url
        pattern = re.compile(r'var\s+hq_str_([A-Za-z0-9_]+)\s*=\s*"(.*?)";')
        found = set()
        for match in pattern.finditer(text):
            symbol = match.group(1)
            if not symbol.startswith("nf_"):
                symbol = "nf_" + symbol
            found.add(symbol)
            output["snapshot_cards"].append(parse_quote(symbol, match.group(2), names.get(symbol, symbol)))
        missing = sorted(set(names) - found)
        for symbol in missing:
            snapshot_id = "snapshot-" + hashlib.sha256(
                f"sina-futures|{symbol}|missing".encode("utf-8")
            ).hexdigest()[:16]
            output["snapshot_cards"].append(
                {
                    "snapshot_id": snapshot_id,
                    "asset": names[symbol],
                    "symbol": symbol,
                    "market": "",
                    "session": "china_futures_continuous",
                    "price": None,
                    "change_absolute": None,
                    "change_percent": None,
                    "currency": "CNY",
                    "unit": "contract_quote",
                    "quote_time": "",
                    "source_name": "新浪期货行情",
                    "source_url_or_endpoint": url,
                    "observation": "",
                    "possible_context": [],
                    "change": {"absolute": None, "percent": None},
                    "time": "",
                    "source": {"name": "新浪期货行情", "url": url},
                    "interpretation": "",
                    "data_quality": "missing",
                }
            )
    except Exception as exc:
        output["collection_errors"].append({"source": "sina_futures", "error": str(exc)})

    result = {
        "schema_version": 2,
        "market_snapshot": {
            "as_of": generated_at,
            "session_labels": ["china_futures_continuous"],
            **output,
        },
        "market_comparisons": [],
        "raw_anomalies": [],
        "publication_checks": {
            "market_fresh": False,
            "market_freshness_details": {
                "checked_at": generated_at,
                "component": "china_futures_continuous",
                "component_fresh": bool(output["snapshot_cards"]) and all(
                    card.get("data_quality") == "live" for card in output["snapshot_cards"]
                ),
                "checked_snapshot_count": len(output["snapshot_cards"]),
                "blocking_reasons": [
                    "full A-share, Hong Kong, and domestic-futures close coverage has not been assembled"
                ],
            },
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
