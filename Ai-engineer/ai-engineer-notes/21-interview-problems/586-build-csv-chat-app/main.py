"""CSV chat: the LLM writes a JSON *query plan*, we execute it with a whitelist (no eval/exec).

Offline: `mock_llm_plan` maps a few question shapes to plans (stand-in for structured output).
"""
from __future__ import annotations

import asyncio
import csv
import io
import json
from statistics import mean
from typing import Any

CSV_TEXT = """product,country,value_usd,duty_usd
smartphone,CN,1000,200
laptop,CN,1500,0
tshirt,IN,50,6
smartphone,IN,900,180
"""

ALLOWED_AGG = {"sum", "mean", "count", "max"}


def load(text: str) -> list[dict[str, Any]]:
    """Parse CSV and convert numeric-looking columns to float."""
    rows = list(csv.DictReader(io.StringIO(text)))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except ValueError:
                pass
    return rows


def mock_llm_plan(question: str) -> str:
    """Pretend structured-output LLM: returns JSON plan."""
    q = question.lower()
    if "total duty" in q and "smartphone" in q:
        return json.dumps({"filter": {"product": "smartphone"}, "agg": "sum", "column": "duty_usd"})
    if "average value" in q:
        return json.dumps({"filter": {}, "agg": "mean", "column": "value_usd"})
    return json.dumps({"filter": {}, "agg": "delete_all", "column": "x"})  # a bad plan on purpose


def execute(rows: list[dict[str, Any]], plan: dict[str, Any]) -> float:
    """Validate the plan against the schema/whitelist, then compute."""
    agg, col = plan.get("agg"), plan.get("column")
    if agg not in ALLOWED_AGG:
        raise ValueError(f"aggregation {agg!r} not allowed")
    if col not in rows[0]:
        raise ValueError(f"unknown column {col!r}")
    sel = [r for r in rows if all(r.get(k) == v for k, v in plan.get("filter", {}).items())]
    if agg == "count":
        return float(len(sel))
    vals = [r[col] for r in sel]
    if not vals:
        raise ValueError("filter matched no rows")
    return {"sum": sum, "mean": mean, "max": max}[agg](vals)


async def chat(question: str) -> str:
    """Question -> plan -> validated execution -> sentence. Errors are explained, not raised."""
    rows = load(CSV_TEXT)
    try:
        plan = json.loads(mock_llm_plan(question))
        return f"Result: {execute(rows, plan)}"
    except (ValueError, json.JSONDecodeError) as exc:
        return f"Could not answer safely: {exc}"


if __name__ == "__main__":
    for q in ["What is the total duty on smartphone?", "average value?", "drop the table"]:
        print(q, "->", asyncio.run(chat(q)))
