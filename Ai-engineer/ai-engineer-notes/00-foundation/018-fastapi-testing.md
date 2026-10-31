---

# 018. FastAPI Testing
# हिंदी में: FastAPI Testing

---

## 🔵 Simple Definition (English)
FastAPI testing means calling your API in code and checking the result, using `TestClient` (sync) or `httpx.AsyncClient` with `ASGITransport` (async), and `pytest`. For AI apps the key trick is replacing the real LLM, DB and cache with fakes through dependency overrides, so tests are fast, free and deterministic.

## 🔵 सरल परिभाषा (Hindi)
FastAPI testing का मतलब code से अपनी API call करके result जाँचना है, `TestClient` (sync) या `httpx.AsyncClient` + `ASGITransport` (async) और `pytest` से। AI apps में मुख्य तरकीब है असली LLM, DB और cache की जगह dependency overrides से fakes लगाना, ताकि tests तेज़, मुफ़्त और deterministic हों।

---

## 🔴 Problem it Solves
LLM outputs are random, slow and cost money. Tests that call a real model are flaky (answers change), slow (seconds each) and expensive (tokens on every commit), and they fail when the network is down. You still need confidence that routes, validation, error handling and prompts' plumbing work, so you test your code with fakes and separately evaluate model quality.

## 🔴 यह क्यों बना? (Hindi)
LLM outputs random, धीमे और महँगे होते हैं। असली model call करने वाले tests flaky (answers बदलते हैं), धीमे (हर एक में seconds) और महँगे (हर commit पर tokens) होते हैं, और network बंद होने पर fail होते हैं। फिर भी routes, validation, error handling और prompts की plumbing पर भरोसा चाहिए, इसलिए अपना code fakes से test करते हैं और model quality का अलग evaluation करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build the app with an app factory or import `app` (see topic 016)
Step 2 → Create a client: TestClient(app) (sync) or httpx.AsyncClient(transport=ASGITransport(app=app))
Step 3 → Override dependencies: app.dependency_overrides[get_llm] = lambda: FakeLLM()
Step 4 → Call the route: client.post("/v1/classify", json={...})
Step 5 → Assert status code, JSON body, headers, and side effects (fake DB rows, fake LLM call count)
Step 6 → Test failures: make the fake raise errors (timeout, 429, invalid JSON) and assert 502/429/etc.
Step 7 → Clean up overrides after each test (pytest fixture with yield); run in CI with no API keys
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → App factory या `app` import करो (topic 016 देखें)
Step 2 → Client बनाओ: TestClient(app) (sync) या httpx.AsyncClient(transport=ASGITransport(app=app))
Step 3 → Dependencies override करो: app.dependency_overrides[get_llm] = lambda: FakeLLM()
Step 4 → Route call करो: client.post("/v1/classify", json={...})
Step 5 → Status code, JSON body, headers और side effects (fake DB rows, fake LLM call count) जाँचो
Step 6 → Failures test करो: fake से errors (timeout, 429, गलत JSON) उठवाओ और 502/429 आदि जाँचो
Step 7 → हर test के बाद overrides साफ़ करो (yield वाला pytest fixture); CI में बिना API keys चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tests: (1) valid request returns HS code and saves one row; (2) description of 2 characters returns 422 and never calls the LLM; (3) LLM fake raising timeout returns 504; (4) LLM fake returning broken JSON triggers one retry and then a 502; (5) the same description twice calls the LLM once (cache). A separate nightly evaluation runs 200 labeled products against the real model and reports accuracy.

**Zomato AI**: Tests assert that the recommender falls back to a normal list (`degraded: true`) when the LLM fake fails.

## 🟡 Real Example Hindi mein
**Tariff System**: Tests: (1) सही request HS code देती है और एक row save करती है; (2) 2 अक्षरों की description 422 देती है और LLM कभी call नहीं होता; (3) timeout उठाने वाला LLM fake 504 देता है; (4) टूटा JSON लौटाने वाला fake एक retry के बाद 502 देता है; (5) वही description दो बार देने पर LLM एक बार call होता है (cache)। अलग nightly evaluation 200 labeled products को असली model पर चलाकर accuracy बताता है।

**Zomato AI**: Tests जाँचते हैं कि LLM fake fail होने पर recommender सामान्य list (`degraded: true`) पर लौटता है।

---

## 💻 Code Example — Basic
```python
# Basic tests - needs: fastapi httpx pytest. Run: pytest -q  (or run this file directly)
from fastapi import Depends, FastAPI  # tools
from fastapi.testclient import TestClient  # sync client
from pydantic import BaseModel, Field  # models


class RealLLM:  # would call OpenAI in production
    def complete(self, text: str) -> str:  # method
        raise RuntimeError("real LLM must not be called in tests")  # protects against accidental spend


class FakeLLM:  # deterministic stand-in
    def complete(self, text: str) -> str:  # same interface
        return "8517.13"  # fixed answer


def get_llm() -> RealLLM:  # dependency
    return RealLLM()  # production provider


class In(BaseModel):  # request
    description: str = Field(min_length=3)  # at least 3 chars


app = FastAPI()  # app


@app.post("/classify")  # route
def classify(body: In, llm: RealLLM = Depends(get_llm)) -> dict[str, str]:  # handler
    return {"hs_code": llm.complete(body.description)}  # use injected LLM


def test_classify_ok() -> None:  # a pytest test
    app.dependency_overrides[get_llm] = lambda: FakeLLM()  # swap in the fake
    try:  # always clean up
        r = TestClient(app).post("/classify", json={"description": "Android phone"})  # call API
        assert r.status_code == 200  # success
        assert r.json() == {"hs_code": "8517.13"}  # exact body
    finally:  # cleanup
        app.dependency_overrides.clear()  # remove overrides


def test_validation_never_calls_llm() -> None:  # 422 should happen before the LLM
    app.dependency_overrides[get_llm] = lambda: RealLLM()  # real one would raise if called
    try:  # cleanup
        r = TestClient(app).post("/classify", json={"description": "x"})  # too short
        assert r.status_code == 422  # validation error, LLM untouched
    finally:  # cleanup
        app.dependency_overrides.clear()  # reset


if __name__ == "__main__":  # run without pytest
    test_classify_ok()  # run
    test_validation_never_calls_llm()  # run
    print("2 tests passed")  # done
```

## 💻 Code Example — Advanced
```python
# Production-style tests: pytest fixtures, async client, parametrize, fake failures, call counting,
# lifespan-aware client, and a streaming test. Needs: pytest pytest-asyncio httpx fastapi.
# Run: pytest -q  (this file also has a main runner for demonstration without pytest)
import asyncio  # async tools
import json  # parse events
from collections.abc import AsyncIterator  # type

import httpx  # async client
import pytest  # test framework
from fastapi import Depends, FastAPI, HTTPException  # FastAPI
from fastapi.responses import StreamingResponse  # streaming
from pydantic import BaseModel, Field  # models


class LLMError(Exception): ...  # domain error


class FakeLLM:  # configurable fake
    def __init__(self, answer: str = "8517.13", error: Exception | None = None) -> None:  # config
        self.answer, self.error, self.calls = answer, error, 0  # state

    async def complete(self, prompt: str) -> str:  # async call
        self.calls += 1  # count
        if self.error:  # simulate failure
            raise self.error  # raise it
        return self.answer  # return canned answer

    async def stream(self, prompt: str) -> AsyncIterator[str]:  # fake token stream
        for tok in ["8517", ".13"]:  # tokens
            yield tok  # one by one


def get_llm() -> FakeLLM:  # production would return the real client; here a safe default
    return FakeLLM(error=RuntimeError("real LLM called in test!"))  # fails loudly if not overridden


class In(BaseModel):  # request
    description: str = Field(min_length=3, max_length=2000)  # bounds


app = FastAPI()  # app


@app.post("/classify")  # route
async def classify(body: In, llm: FakeLLM = Depends(get_llm)) -> dict[str, str]:  # handler
    try:  # map errors
        return {"hs_code": await llm.complete(body.description)}  # call
    except asyncio.TimeoutError:  # slow provider
        raise HTTPException(504, "LLM timeout")  # gateway timeout
    except LLMError:  # provider failure
        raise HTTPException(502, "LLM failed")  # bad gateway


@app.post("/stream")  # streaming route
async def stream(body: In, llm: FakeLLM = Depends(get_llm)) -> StreamingResponse:  # handler
    async def gen() -> AsyncIterator[str]:  # generator
        async for tok in llm.stream(body.description):  # fake tokens
            yield f"data: {json.dumps({'t': tok})}\n\n"  # SSE line
    return StreamingResponse(gen(), media_type="text/event-stream")  # response


@pytest.fixture  # reusable setup
def make_client():  # factory fixture
    clients: list[httpx.AsyncClient] = []  # track for cleanup

    def _make(fake: FakeLLM) -> httpx.AsyncClient:  # build client with a given fake
        app.dependency_overrides[get_llm] = lambda: fake  # override
        c = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")  # in-process
        clients.append(c)  # remember
        return c  # give to test

    yield _make  # run the test
    app.dependency_overrides.clear()  # cleanup overrides


@pytest.mark.asyncio  # async test
async def test_ok(make_client) -> None:  # success path
    fake = FakeLLM()  # fake
    async with make_client(fake) as c:  # client
        r = await c.post("/classify", json={"description": "Android phone"})  # call
    assert r.status_code == 200 and r.json() == {"hs_code": "8517.13"}  # assertions
    assert fake.calls == 1  # exactly one LLM call


@pytest.mark.asyncio  # parametrised failure tests
@pytest.mark.parametrize("error,expected", [(asyncio.TimeoutError(), 504), (LLMError("boom"), 502)])  # cases
async def test_llm_failures(make_client, error, expected) -> None:  # error mapping
    async with make_client(FakeLLM(error=error)) as c:  # client
        r = await c.post("/classify", json={"description": "Android phone"})  # call
    assert r.status_code == expected  # mapped status


@pytest.mark.asyncio  # validation
async def test_validation_costs_no_tokens(make_client) -> None:  # 422 before LLM
    fake = FakeLLM()  # fake
    async with make_client(fake) as c:  # client
        r = await c.post("/classify", json={"description": "x"})  # invalid
    assert r.status_code == 422 and fake.calls == 0  # LLM never called


@pytest.mark.asyncio  # streaming
async def test_stream(make_client) -> None:  # SSE test
    async with make_client(FakeLLM()) as c:  # client
        r = await c.post("/stream", json={"description": "Android phone"})  # call
    assert r.headers["content-type"].startswith("text/event-stream")  # media type
    assert r.text.count("data:") == 2  # two token events


if __name__ == "__main__":  # run without pytest for demonstration
    raise SystemExit(pytest.main([__file__, "-q"]))  # delegate to pytest
```

---

## 🟠 FastAPI Integration
Testing is a FastAPI feature (`TestClient` is built on httpx). Tips: use `with TestClient(app) as c:` so lifespan events run; use `httpx.AsyncClient` when the test itself must be async (for example awaiting a fake DB); keep a `conftest.py` with fixtures (`client`, `fake_llm`, `fake_db`); override settings through dependencies instead of environment mutation.

```python
# conftest.py - shared fixtures
import pytest  # fixtures
from fastapi.testclient import TestClient  # client

from app.main import create_app  # app factory from topic 016


@pytest.fixture  # provides a client with fake services
def client():  # fixture function
    app = create_app()  # build app (uses fakes by default in tests)
    with TestClient(app) as c:  # runs lifespan startup/shutdown
        yield c  # test uses it
```

---

## 🔗 LangChain / LangGraph Connection
LangChain ships fake models for tests: `FakeListChatModel` (returns responses from a list in order) and `GenericFakeChatModel` (from an iterator of messages) in `langchain_core.language_models`. Build the chain with the fake and test your prompt wiring, parsers and graph routing with zero tokens. Use LangSmith or your own eval set for quality tests of the real model.

```python
# Test a LangChain chain with a fake model - zero tokens (pip install langchain-core)
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # fake chat model
from langchain_core.output_parsers import StrOutputParser  # parser
from langchain_core.prompts import ChatPromptTemplate  # prompt

fake = FakeListChatModel(responses=["8517.13"])  # returns this for the first call
chain = ChatPromptTemplate.from_template("HS code for {item}") | fake | StrOutputParser()  # same shape as production chain


def test_chain() -> None:  # test
    assert chain.invoke({"item": "phone"}) == "8517.13"  # deterministic


test_chain()  # run
print("chain test passed")  # confirm
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Tests that call the real LLM
✅ Correct: fake it; run a separate, small evaluation suite on schedule.

```python
# Wrong: flaky, slow, costs tokens on every commit
def test_classify():
    r = client.post("/classify", json={"description": "phone"})
    assert r.json()["hs_code"] == "8517.13"   # may be 8517.12 tomorrow
# Right: override dependency with FakeLLM; assert your logic, not model luck
```

❌ Mistake 2: Forgetting to clear `dependency_overrides` (tests affect each other)
✅ Correct: use a fixture with cleanup.

```python
# Wrong
app.dependency_overrides[get_llm] = lambda: fake   # never cleared; later tests see the fake
# Right
@pytest.fixture
def override():
    yield
    app.dependency_overrides.clear()
```

❌ Mistake 3: Asserting full free-text LLM output equality in evaluation tests. Check structure, required facts, or use scored evaluation (labels, LLM-as-judge) with thresholds.

---

## 🧠 Tricky Interview Question

**Q**: "Your CI is green, but production returns wrong HS codes after a prompt change. Your tests use a fake LLM. Are the tests useless?"

**Answer**: No, but they test a different thing. Fake-LLM tests verify code behaviour: validation, routing, error mapping, caching, retries and parsing. They cannot detect prompt or model quality regressions. You also need an evaluation suite: a labeled dataset (for example 200 products with expected codes), run against the real model on prompt changes or nightly, reporting accuracy, token usage and latency, with a threshold that blocks release. Add a small canary/smoke test in staging, plus production monitoring of confidence distribution and user corrections.

---

## ⚫ Interview Questions + Answers

Q1: What is `TestClient`? (Easy)
A1: A test client from Starlette/FastAPI (built on httpx) that sends requests to your app in-process, without a running server, so tests are fast.

Q2: How do you replace a dependency in a test? (Easy)
A2: `app.dependency_overrides[original] = replacement`, then `.clear()` afterwards (ideally in a fixture).

Q3: When do you need `httpx.AsyncClient` instead of `TestClient`? (Medium)
A3: When the test itself needs `await` (for example inspecting an async DB or running concurrent requests with `asyncio.gather`) or you want to test async behaviour. With `ASGITransport`, requests go straight to the ASGI app. Note: `AsyncClient` does not run lifespan events by default; use `asgi-lifespan`'s `LifespanManager` or manage startup in fixtures.

Q4: How do you test error handling for flaky LLM providers? (Medium)
A4: Make the fake raise specific exceptions (timeout, rate limit, invalid JSON) via parametrised tests and assert status codes, retry counts (`fake.calls`), fallback behaviour and that no tokens are wasted on permanent errors. Use fake clocks or patch `asyncio.sleep` so backoff does not slow tests.

Q5: How do you test and evaluate non-deterministic LLM behaviour in CI? (Hard)
A5: Split into layers. Unit and API tests with fakes (fast, deterministic, every commit). Contract tests on parsing using recorded real responses (VCR-style cassettes or stored fixtures) so schema changes are caught. Evaluation tests on a labeled golden set with real calls, at temperature 0, scored by exact match for structured fields or an LLM-judge/rubric for text, with thresholds and cost caps, run on prompt changes and nightly rather than on every commit. Track results over time (LangSmith, custom DB). Use a small smoke test in staging for wiring and keys.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every route, dependency, validator and error mapping
- Retry, fallback and caching logic
- Before changing prompts, models or infrastructure

❌ Avoid when:
- Trying to prove answer quality with fakes (use evaluation sets)
- Writing tests that only mirror the implementation line by line
- Running expensive real-model tests on every commit

---

## 📊 Visual Diagram
```
                 ┌────────────── test pyramid for AI APIs ───────────────┐
  many, fast     │ Unit: parsers, validators, prompt rendering (no I/O)   │ 0 tokens
                 ├────────────────────────────────────────────────────────┤
                 │ API tests: TestClient + FakeLLM/FakeDB/FakeCache        │ 0 tokens
                 ├────────────────────────────────────────────────────────┤
                 │ Contract tests: recorded real responses vs. schema      │ 0 tokens
                 ├────────────────────────────────────────────────────────┤
  few, slow      │ Eval set: real model on labeled data (nightly/PR gate)  │ tokens $$
                 └────────────────────────────────────────────────────────┘

 test ──► client.post() ──► app (overrides: get_llm→Fake) ──► assert status, body, fake.calls
```

---

## 💰 Cost Impact
Fake-based tests cost zero tokens, so CI can run thousands of tests per day for free. If 300 tests each used a real call of 1,000 tokens, every CI run would burn 300K tokens (about $0.05 on gpt-4o-mini input pricing, but much more with larger models and output, plus flakiness), multiplied by every commit. Budget the evaluation suite: 200 items x 1,500 tokens = 300K tokens per run; run nightly or on prompt changes, use a cheaper judge model, cache results by (prompt version, input hash), and set a hard spending cap in the CI key.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TestClient | In-process API test client | in-process API test client |
| dependency_overrides | Swap dependencies in tests | tests में dependencies बदलना |
| Fake | Simple stand-in object | सरल नकली object |
| Fixture | Reusable test setup | reusable test setup |
| Parametrize | Run a test with many inputs | एक test कई inputs पर |
| Golden set | Labeled evaluation data | labeled evaluation data |
| Flaky | Sometimes passes, sometimes fails | कभी पास कभी फेल |
| Contract test | Checks data shape agreement | data shape की सहमति जाँच |

---

## ⚡ 3-Line Summary
English: Test FastAPI apps with `TestClient` or `httpx.AsyncClient` and replace the LLM, DB and cache using `dependency_overrides`. Fakes make tests fast, free and deterministic; separate evaluation sets measure real model quality. Test failure paths and token-saving behaviour (validation, cache).
Hindi: FastAPI apps को `TestClient` या `httpx.AsyncClient` से test करो और `dependency_overrides` से LLM, DB, cache बदलो। Fakes tests को तेज़, मुफ़्त और deterministic बनाते हैं; असली model की quality के लिए अलग evaluation set चलाओ। Failure paths और tokens बचाने वाले व्यवहार (validation, cache) भी test करो।

---

## ➡️ Next Topic
**019. PostgreSQL Async Queries** — next we go deeper into writing efficient, safe async SQL for usage reports and retrieval.
