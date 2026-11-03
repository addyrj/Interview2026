"""Build a chat-format fine-tuning JSONL dataset: clean, dedupe, validate, split. Offline."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

SYSTEM = "You are a tariff classification assistant. Reply with HS code and reason."
ROLES = {"system", "user", "assistant"}

RAW = [
    {"product": "LED bulb 9W", "hs": "8539.50", "why": "LED lamps fall under 8539.50"},
    {"product": "led bulb 9w ", "hs": "8539.50", "why": "LED lamps fall under 8539.50"},  # dup
    {"product": "Cotton t-shirt", "hs": "6109.10", "why": "Knitted cotton T-shirts"},
    {"product": "", "hs": "0000.00", "why": "bad row"},  # invalid
    {"product": "Smartphone", "hs": "8517.13", "why": "Smartphones are 8517.13"},
    {"product": "Laptop", "hs": "8471.30", "why": "Portable computers"},
    {"product": "Basmati rice", "hs": "1006.30", "why": "Milled rice"},
]


def to_example(row: dict[str, str]) -> dict:
    product = " ".join(row["product"].split()).strip()  # normalise whitespace
    if not product or not row["hs"].strip():  # validate raw fields too
        raise ValueError("empty product or hs code")
    return {"messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Classify: {product}"},
        {"role": "assistant", "content": f"HS {row['hs']} - {row['why']}"},
    ]}


def validate(ex: dict) -> None:
    msgs = ex.get("messages")
    if not isinstance(msgs, list) or len(msgs) < 2:
        raise ValueError("need >= 2 messages")
    for m in msgs:
        if m.get("role") not in ROLES or not str(m.get("content", "")).strip():
            raise ValueError(f"bad message: {m}")
    if msgs[-1]["role"] != "assistant":
        raise ValueError("last message must be assistant")


def build(rows: list[dict[str, str]]) -> tuple[list[dict], dict[str, int]]:
    seen: set[str] = set()
    out: list[dict] = []
    stats = {"input": len(rows), "invalid": 0, "duplicate": 0}
    for row in rows:
        try:
            ex = to_example(row)
            validate(ex)
        except (KeyError, ValueError):
            stats["invalid"] += 1
            continue
        key = hashlib.md5(ex["messages"][1]["content"].lower().encode()).hexdigest()
        if key in seen:  # same prompt twice -> keep first only
            stats["duplicate"] += 1
            continue
        seen.add(key)
        out.append(ex)
    stats["kept"] = len(out)
    return out, stats


def split(data: list[dict], val_frac: float = 0.2, seed: int = 42) -> tuple[list[dict], list[dict]]:
    data = data[:]
    random.Random(seed).shuffle(data)  # deterministic shuffle
    n_val = max(1, int(len(data) * val_frac))
    return data[n_val:], data[:n_val]


def write_jsonl(path: Path, data: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for ex in data:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    data, stats = build(RAW)
    train, val = split(data)
    print(stats, "train:", len(train), "val:", len(val))
    print(json.dumps(train[0], ensure_ascii=False)[:120], "...")
    # write_jsonl(Path("train.jsonl"), train)  # uncomment to save
