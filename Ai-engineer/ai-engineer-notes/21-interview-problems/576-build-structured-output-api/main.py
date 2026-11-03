"""576. Build Structured Output API - Tariff Classification.

Runs offline: the LLM is mocked. Uses only the standard library, so the
validation logic is visible. In production swap `validate()` for Pydantic
and `mock_llm()` for a real client call.
Run:  python main.py
"""
from __future__ import annotations

import asyncio  # async version of the pipeline
import json  # parse the model's JSON text
import re  # strip markdown fences
from dataclasses import dataclass, asdict  # simple typed result object
from typing import Any, Awaitable, Callable  # type hints

# JSON Schema we would send to the LLM (provider-side structured output).
TARIFF_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "hs_code": {"type": "string", "pattern": r"^\d{4}\.\d{2}$"},
        "description": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["hs_code", "description", "confidence"],
    "additionalProperties": False,
}


class StructuredOutputError(Exception):
    """Raised when the model never returns valid output."""


@dataclass
class TariffResult:
    """Validated, typed result."""

    hs_code: str  # e.g. "8517.13"
    description: str  # short product description
    confidence: float  # 0..1


def extract_json(raw: str) -> dict[str, Any]:
    """Pull a JSON object out of raw model text."""
    text = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()  # drop fences
    start, end = text.find("{"), text.rfind("}")  # locate the object
    if start == -1 or end == -1:  # nothing that looks like JSON
        raise ValueError("no JSON object found")
    return json.loads(text[start : end + 1])  # may raise JSONDecodeError (a ValueError)


def validate(data: dict[str, Any]) -> TariffResult:
    """Manual schema validation (Pydantic does this for you in production)."""
    extra = set(data) - set(TARIFF_SCHEMA["properties"])  # unknown keys
    if extra:
        raise ValueError(f"unexpected fields: {sorted(extra)}")
    for key in TARIFF_SCHEMA["required"]:  # required keys present?
        if key not in data:
            raise ValueError(f"missing field: {key}")
    if not re.match(TARIFF_SCHEMA["properties"]["hs_code"]["pattern"], str(data["hs_code"])):
        raise ValueError(f"bad hs_code: {data['hs_code']!r}")
    conf = data["confidence"]
    if isinstance(conf, bool) or not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        raise ValueError(f"bad confidence: {conf!r}")
    return TariffResult(str(data["hs_code"]), str(data["description"]), float(conf))


# ---- Mock LLM: first call is messy, later calls are clean (simulates retry) ----
_calls = {"n": 0}


async def mock_llm(prompt: str) -> str:
    """Fake LLM. Replace with a real API call."""
    await asyncio.sleep(0)  # pretend network I/O
    _calls["n"] += 1
    if _calls["n"] % 2 == 1:  # odd calls: broken output
        return 'Sure! Here you go: {"hs_code": "85171", "description": "Smartphone", "confidence": 1.4}'
    return '```json\n{"hs_code": "8517.13", "description": "Smartphone", "confidence": 0.93}\n```'


async def classify(
    product: str,
    llm: Callable[[str], Awaitable[str]] = mock_llm,
    max_retries: int = 3,
) -> TariffResult:
    """Ask the LLM, validate, and retry with the error fed back."""
    prompt = f"Classify this product into an HS code as JSON: {product}"  # base prompt
    last_error = ""  # remember last failure
    for attempt in range(1, max_retries + 1):  # bounded retries
        raw = await llm(prompt)  # call the model
        try:
            return validate(extract_json(raw))  # success path
        except ValueError as exc:  # JSON or schema failure
            last_error = str(exc)
            print(f"  attempt {attempt} failed: {last_error}")
            prompt += f"\nYour last answer was invalid ({last_error}). Return only valid JSON."
    raise StructuredOutputError(f"gave up after {max_retries} tries: {last_error}")


# ---- Optional FastAPI layer (only if fastapi is installed) ----
try:
    from fastapi import FastAPI, HTTPException

    app = FastAPI(title="Structured Tariff API")

    @app.post("/classify")
    async def classify_route(body: dict[str, str]) -> dict[str, Any]:
        """POST {"product": "..."} -> validated JSON."""
        try:
            return asdict(await classify(body.get("product", "")))
        except StructuredOutputError as exc:
            raise HTTPException(status_code=502, detail=str(exc))
except ImportError:  # fastapi missing: the demo below still works
    app = None  # type: ignore[assignment]


if __name__ == "__main__":
    result = asyncio.run(classify("Apple iPhone 15, 128GB"))  # run the demo
    print(result)
    # Negative test: validator rejects bad data
    try:
        validate({"hs_code": "x", "description": "d", "confidence": 0.5})
    except ValueError as err:
        print("rejected:", err)
