---

# 561. Testing AI Apps in CI
# हिंदी में: CI में AI Apps की Testing

---

## 🔵 Simple Definition (English)
Testing AI apps in CI means automatically checking both the normal code (routes, parsing, retrieval logic) and the AI behaviour (does the answer stay correct, safe and cheap?). LLM output is non-deterministic, so you test in layers: fast mocked tests, contract tests on structure, and small eval sets for quality.

## 🔵 सरल परिभाषा (Hindi)
CI में AI apps की testing का मतलब है सामान्य code (routes, parsing, retrieval logic) और AI behaviour (जवाब सही, सुरक्षित और सस्ता रहता है या नहीं) दोनों को अपने आप जाँचना। LLM output non-deterministic होता है, इसलिए layers में test करते हैं: तेज़ mocked tests, structure के contract tests और quality के लिए छोटे eval sets।

---

## 🔴 Problem it Solves
Classic asserts like `assert answer == "8517.13"` break because wording changes between runs. Real API calls in tests are slow, costly and flaky (rate limits, outages). Yet skipping tests lets prompt regressions reach users.

## 🔴 यह क्यों बना? (Hindi)
`assert answer == "8517.13"` जैसे asserts टूट जाते हैं क्योंकि हर run में शब्द बदलते हैं। Tests में real API calls धीमे, महँगे और अस्थिर होते हैं। फिर भी tests छोड़ने पर prompt regressions users तक पहुँचते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Layer 1: pure-logic unit tests (chunking, HS-code regex, cost math) - no LLM
Step 2 → Layer 2: LLM mocked/faked - test routes, retries, error handling, parsing
Step 3 → Layer 3: structured-output contract tests (Pydantic schema validates)
Step 4 → Layer 4: retrieval tests on a tiny fixed corpus (recall@k)
Step 5 → Layer 5: small real-LLM eval (20-50 cases, temperature=0) - threshold gate
Step 6 → Safety tests: prompt-injection and PII cases must be refused/redacted
Step 7 → Record cost/tokens per eval run and fail if it exceeds budget
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Layer 1: pure-logic tests (chunking, HS-code regex, cost math) - LLM नहीं
Step 2 → Layer 2: LLM mock/fake - routes, retries, error handling, parsing
Step 3 → Layer 3: structured-output contract tests (Pydantic schema)
Step 4 → Layer 4: छोटे fixed corpus पर retrieval tests (recall@k)
Step 5 → Layer 5: छोटा real-LLM eval (20-50 cases, temperature=0), threshold gate
Step 6 → Safety tests: prompt-injection और PII cases
Step 7 → हर eval run का cost/tokens record करें, budget पार हो तो fail
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tests include: (a) the LLM returns JSON that parses into `HSResult(code, confidence)`; (b) a fake LLM that returns invalid JSON makes the API retry once then return a 502 with a clear message; (c) a 30-invoice golden set must score >= 90% on 4-digit HS prefix; (d) an invoice containing "ignore previous instructions" must not change the output format.

**Amazon-style**: Retrieval tests check that "wireless earbuds" returns known product IDs in the top 5.

## 🟡 Real Example Hindi mein
**Tariff System**: Tests: (a) LLM का JSON `HSResult(code, confidence)` में parse हो; (b) fake LLM invalid JSON दे तो API एक बार retry करे फिर साफ संदेश के साथ 502 दे; (c) 30-invoice golden set पर 4-digit HS prefix का score >= 90%; (d) "ignore previous instructions" वाला invoice output format न बदले।

---

## 💻 Code Example — Basic
```python
# Basic: test with a fake LLM using plain pytest style (run: pytest this_file.py)
import json  # parse the model output


class FakeLLM:
    """Deterministic stand-in for a real model."""

    def __init__(self, reply: str) -> None:
        self.reply = reply                      # canned answer

    def invoke(self, prompt: str) -> str:
        return self.reply                       # ignore the prompt, return canned text


def classify(llm: FakeLLM, item: str) -> dict[str, str]:
    raw = llm.invoke(f"HS code for {item}. Reply JSON {{'code': ...}}")  # ask model
    return json.loads(raw)                      # may raise on bad JSON


def test_classify_ok() -> None:
    out = classify(FakeLLM('{"code": "8517"}'), "phone")   # good JSON
    assert out["code"] == "8517"                            # exact, because fake is deterministic


def test_classify_bad_json() -> None:
    try:
        classify(FakeLLM("not json"), "phone")              # bad JSON
    except json.JSONDecodeError:
        return                                              # expected
    raise AssertionError("should have raised")              # test fails if no error
```

## 💻 Code Example — Advanced
```python
# Advanced: async tests, retries, Pydantic contract, budget guard (pytest + pytest-asyncio)
import asyncio                                   # async
import json                                      # parse
from typing import Awaitable, Callable           # types
from pydantic import BaseModel, ValidationError  # schema validation

LLMFn = Callable[[str], Awaitable[str]]          # async model function type


class HSResult(BaseModel):
    code: str                                    # HS code
    confidence: float                            # 0..1


class ClassifyError(Exception):
    """Raised when the model never returns valid output."""


async def classify(llm: LLMFn, item: str, retries: int = 1) -> HSResult:
    last: Exception | None = None                # remember last failure
    for _ in range(retries + 1):                 # first try + retries
        try:
            raw = await asyncio.wait_for(llm(item), timeout=10)   # bounded call
            return HSResult(**json.loads(raw))                    # parse + validate
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            last = exc                                            # bad output: retry
        except asyncio.TimeoutError as exc:
            last = exc                                            # slow: retry
    raise ClassifyError(str(last))                                # give up clearly


# ---- tests (pytest-asyncio: mark async tests with @pytest.mark.asyncio) ----
async def test_retry_then_success() -> None:
    calls = {"n": 0}                             # count invocations

    async def flaky(_: str) -> str:
        calls["n"] += 1                          # track
        return "oops" if calls["n"] == 1 else '{"code": "8517", "confidence": 0.9}'

    res = await classify(flaky, "phone")         # should retry once
    assert res.code == "8517" and calls["n"] == 2


async def test_gives_up() -> None:
    async def bad(_: str) -> str:
        return "never json"                      # always invalid

    try:
        await classify(bad, "phone")             # should raise
    except ClassifyError:
        return                                   # expected
    raise AssertionError("expected ClassifyError")


if __name__ == "__main__":
    asyncio.run(test_retry_then_success())       # allow running without pytest
    asyncio.run(test_gives_up())
    print("ok")
```

---

## 🟠 FastAPI Integration
Use `TestClient` and FastAPI's `dependency_overrides` to swap the real LLM service with a fake.

```python
# FastAPI route + dependency override test (pip install fastapi httpx)
from fastapi import Depends, FastAPI            # framework
from fastapi.testclient import TestClient       # in-process client

app = FastAPI()                                 # app


class LLMService:
    async def classify(self, text: str) -> str:
        raise RuntimeError("real LLM - not used in tests")   # real impl would call the API


def get_llm() -> LLMService:
    return LLMService()                          # dependency provider


@app.post("/classify")
async def classify(text: str, llm: LLMService = Depends(get_llm)) -> dict[str, str]:
    return {"code": await llm.classify(text)}    # route uses injected service


class FakeService(LLMService):
    async def classify(self, text: str) -> str:
        return "8517"                            # deterministic fake


app.dependency_overrides[get_llm] = FakeService  # swap for tests
client = TestClient(app)                         # test client
assert client.post("/classify", params={"text": "phone"}).json() == {"code": "8517"}
```

---

## 🔗 LangChain / LangGraph Connection
Use LangChain's fake chat models for chains/graphs. For LangGraph, build the graph with node functions that accept an injected model so tests pass a fake. For quality, use LangSmith datasets and evaluators on a schedule or on prompt PRs (confirm current SDK API names in the docs).

```python
# Test a chain deterministically
from langchain_core.language_models.fake_chat_models import FakeListChatModel   # fake
from langchain_core.output_parsers import StrOutputParser                        # parser
from langchain_core.prompts import ChatPromptTemplate                            # prompt

chain = (ChatPromptTemplate.from_template("HS for {x}")      # build prompt
         | FakeListChatModel(responses=["8517"])             # fake model
         | StrOutputParser())                                # to string
assert chain.invoke({"x": "phone"}) == "8517"                # no network, no cost
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asserting exact text from a real LLM
✅ Correct: Assert structure, key facts, or use a threshold over many cases.
```python
# Wrong
assert llm.invoke("HS for phone") == "The HS code is 8517."   # flaky
# Right
assert "8517" in llm.invoke("HS for phone")                   # fact check, or schema validation
```

❌ Mistake 2: Hitting real APIs in the default test run
✅ Correct: Mark real-LLM tests and run them only in the eval job.
```python
# Wrong: every pytest run costs tokens and fails on rate limits
# Right: @pytest.mark.llm  +  `pytest -m "not llm"` by default, `pytest -m llm` in eval job
```

---

## 🧠 Tricky Interview Question
**Q**: "You set `temperature=0` but your CI eval still varies between runs. Why, and does it matter?"

**Answer**: temperature=0 reduces but does not guarantee determinism: GPU floating-point ordering, batching, silent model updates by the provider, and tool/retrieval nondeterminism (ANN search ties, changing index) all introduce drift. It matters for gating, so use a tolerance band, larger sample, pin the model snapshot version, fix a seed where offered, and keep retrieval fixtures frozen.

---

## ⚫ Interview Questions + Answers

Q1: Why mock the LLM in unit tests?
A1: Speed, zero cost, determinism, and no dependence on network or rate limits.

Q2: What is a contract test for LLM output?
A2: Validating the response against a schema (Pydantic/JSON schema) rather than exact text.

Q3: How do you test retrieval?
A3: Fixed small corpus plus labelled queries; measure recall@k/MRR and assert thresholds.

Q4: How do you test for prompt injection?
A4: Adversarial cases in the suite (e.g. "ignore previous instructions") asserting the output still follows the schema and does not leak the system prompt.

Q5: Design a CI test strategy that keeps cost under $1 per PR.
A5: Mock-heavy unit layer (free); a 30-case eval on a small model with response caching and path filters; budgets enforced by counting tokens and failing above a cap; nightly bigger eval instead of per-PR; LLM-as-judge only for sampled cases.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every PR on any AI app with real users
- Prompt, model or retriever changes

❌ Avoid when:
- Running full-scale evals on every commit (do nightly instead)
- Using LLM-as-judge as the only check without human-labelled calibration

---

## 📊 Visual Diagram
```
 cheap/fast                                              slow/costly
 ┌────────────┬──────────────┬─────────────┬─────────────┬───────────┐
 │ pure logic │ mocked LLM   │ schema /    │ retrieval   │ real-LLM  │
 │ unit tests │ route+retry  │ contract    │ recall@k    │ eval set  │
 └────────────┴──────────────┴─────────────┴─────────────┴───────────┘
 every commit ───────────────────────────────►  PRs touching prompts / nightly
```

---

## 💰 Cost Impact
Layers 1-4 cost zero tokens. Only the real eval spends: for example 40 cases x (900 input + 150 output) tokens is about 42k tokens per run. Use a small model, `max_tokens` caps, caching by input hash, and run only when relevant paths change. Track token usage per run and fail the job if it exceeds a budget.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mock/Fake | Replacement for real dependency | असली dependency की जगह नकली |
| Contract test | Check output shape | Output के ढाँचे की जाँच |
| Golden set | Labelled test cases | Labelled test cases |
| recall@k | Relevant found in top k | Top k में सही मिले |
| Flaky test | Passes/fails randomly | कभी pass कभी fail |
| LLM-as-judge | Model grades answers | Model से जवाब grade कराना |

---

## ⚡ 3-Line Summary
English: Test AI apps in layers: logic, mocked LLM, schema contracts, retrieval, then a small real eval. Assert structure and thresholds, not exact text. Keep real-LLM tests few, cached and budgeted.
Hindi: AI apps को layers में test करें: logic, mocked LLM, schema contracts, retrieval और फिर छोटा real eval। Exact text नहीं, structure और thresholds assert करें। Real-LLM tests कम, cached और budgeted रखें।

---

## ➡️ Next Topic
**562. Model Version Management** — pinning, upgrading and rolling back model versions safely once tests are in place.
