#!/usr/bin/env python3
import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
import tempfile
from pathlib import Path


STOPWORDS = {
    "财联社", "日讯", "公告", "表示", "显示", "公司", "市场", "美国", "中国",
    "今日", "昨日", "北京时间", "消息", "快讯", "来源", "截至", "相关",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, target)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def find_bundles(runs_dir, current_path):
    root = Path(runs_dir)
    current = Path(current_path).resolve()
    if not root.exists():
        return []
    candidates = []
    for path in root.rglob("*.json"):
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved == current:
            continue
        candidates.append(path)
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates


def iter_fact_cards(bundle):
    for key in ("fact_cards", "items", "news_items"):
        value = bundle.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield item
    collection = bundle.get("news_collection")
    if isinstance(collection, dict):
        for key in ("fact_cards", "items", "news_items"):
            for item in collection.get(key, []):
                if isinstance(item, dict):
                    yield item


def iter_market_cards(bundle):
    for key in ("market_snapshot", "snapshot_cards", "market_cards"):
        value = bundle.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield item
        elif isinstance(value, dict):
            for key in ("snapshot_cards", "cards", "items"):
                for item in value.get(key, []):
                    if isinstance(item, dict):
                        yield item


def extract_terms(text):
    text = text or ""
    terms = []
    terms.extend(re.findall(r"[A-Za-z][A-Za-z0-9_.-]{1,12}", text))
    terms.extend(re.findall(r"[\u4e00-\u9fff]{2,8}", text))
    cleaned = []
    for term in terms:
        if term in STOPWORDS:
            continue
        if len(term) > 8 and re.match(r"^[\u4e00-\u9fff]+$", term):
            for i in range(0, len(term), 4):
                piece = term[i : i + 4]
                if len(piece) >= 2 and piece not in STOPWORDS:
                    cleaned.append(piece)
        else:
            cleaned.append(term)
    return cleaned


def topic_counter(bundle):
    counter = collections.Counter()
    for card in iter_fact_cards(bundle):
        related = card.get("related_assets", [])
        if isinstance(related, list):
            for asset in related:
                if isinstance(asset, dict):
                    label = asset.get("key") or asset.get("symbol") or asset.get("name")
                else:
                    label = asset
                if label:
                    counter.update([str(label)])
        text = " ".join(
            str(x)
            for x in [
                card.get("fact"),
                card.get("title"),
                card.get("event"),
                card.get("verified_fact"),
                json.dumps(card.get("related_assets", []), ensure_ascii=False),
            ]
            if x
        )
        counter.update(extract_terms(text))
    return counter


def market_moves(bundle):
    moves = {}
    for card in iter_market_cards(bundle):
        symbol = card.get("symbol") or card.get("asset")
        if not symbol:
            continue
        change = card.get("change")
        pct = None
        if isinstance(change, dict):
            pct = change.get("percent")
        elif isinstance(change, (int, float)):
            pct = change
        if pct is None:
            pct = card.get("change_percent")
        try:
            pct = float(pct)
        except (TypeError, ValueError):
            pct = None
        moves[symbol] = {
            "asset": card.get("asset") or symbol,
            "symbol": symbol,
            "price": card.get("price"),
            "change_percent": pct,
            "time": card.get("quote_time") or card.get("time"),
        }
    return moves


def summarize(current, histories, history_files=None):
    current_topics = topic_counter(current)
    historical_topics = collections.Counter()
    for bundle in histories:
        historical_topics.update(topic_counter(bundle))

    warming = []
    for term, count in current_topics.most_common(30):
        prev = historical_topics.get(term, 0)
        if count >= 2 and (prev == 0 or count >= prev):
            warming.append({"term": term, "current_mentions": count, "historical_mentions": prev})

    cooling = []
    for term, prev in historical_topics.most_common(30):
        curr = current_topics.get(term, 0)
        if prev >= 2 and curr == 0:
            cooling.append({"term": term, "current_mentions": curr, "historical_mentions": prev})

    current_moves = market_moves(current)
    previous_moves = {}
    for bundle in histories:
        for symbol, move in market_moves(bundle).items():
            previous_moves.setdefault(symbol, move)

    price_inflections = []
    for symbol, curr in current_moves.items():
        prev = previous_moves.get(symbol)
        if not prev:
            continue
        curr_pct = curr.get("change_percent")
        prev_pct = prev.get("change_percent")
        if curr_pct is None or prev_pct is None:
            continue
        if (curr_pct > 0 and prev_pct < 0) or (curr_pct < 0 and prev_pct > 0):
            price_inflections.append({"symbol": symbol, "asset": curr.get("asset"), "current_change_percent": curr_pct, "previous_change_percent": prev_pct, "status": "reversal"})
        elif abs(curr_pct) >= 1 and abs(curr_pct) > abs(prev_pct):
            price_inflections.append({"symbol": symbol, "asset": curr.get("asset"), "current_change_percent": curr_pct, "previous_change_percent": prev_pct, "status": "warming"})

    return {
        "schema_version": 2,
        "generated_at": dt.datetime.now().astimezone().isoformat(),
        "history_count": len(histories),
        "history_files": [str(path) for path in (history_files or [])],
        "windows": {"immediate_runs": min(3, len(histories)), "context_runs": len(histories)},
        "observations": {
            "warming_topics": warming[:12],
            "cooling_topics": cooling[:12],
            "price_inflections": price_inflections[:20],
        },
        "cold_start": len(histories) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare current finance run bundle against historical run bundles.")
    parser.add_argument("--current", required=True, help="Current run bundle JSON.")
    parser.add_argument("--runs-dir", default="work/finance-research-runs")
    parser.add_argument("--history", type=int, default=7)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--bundle-output", help="Atomically write run_comparison into a v2 bundle.")
    args = parser.parse_args()

    current = load_json(args.current)
    history_paths = find_bundles(args.runs_dir, args.current)[: args.history]
    histories = []
    for path in history_paths:
        try:
            histories.append(load_json(path))
        except Exception:
            continue
    comparison = summarize(current, histories, history_paths)
    if args.bundle_output:
        if current.get("schema_version") != 2:
            raise SystemExit("--bundle-output requires a schema_version 2 current bundle")
        updated = dict(current)
        updated["run_comparison"] = comparison
        desk_briefs = dict(updated.get("desk_briefs") or {})
        trend = dict(desk_briefs.get("trend") or {})
        trend["machine_comparison"] = comparison
        desk_briefs["trend"] = trend
        updated["desk_briefs"] = desk_briefs
        save_json_atomic(args.bundle_output, updated)
    print(json.dumps(comparison, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
