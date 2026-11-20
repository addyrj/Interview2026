---

# 67. SDK Testing
# हिंदी में: OpenAI Agents SDK की Testing
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0, pytest 9.2.0, pytest-asyncio 1.5.0, fastapi 0.163.0 (Python 3.13.3). All five tests below were actually run and passed (`5 passed`), offline, using a scripted model (`fake.py`, full listing in note #57). Tests with a real model (evals) were NOT run - they need OPENAI_API_KEY. `tariff_app.py` uses a real model name only in its production dependency, which the tests override.

---

## 🔵 Simple Definition (2-3 lines)
Test an agent like any async function: replace the LLM with a scripted fake model that returns pre-written tool calls and answers, then assert on the final output, the tools that ran and the token accounting. Tests become fast, free and deterministic. A smaller set of live "eval" tests checks real model quality separately.

## 🔵 सरल परिभाषा (Hindi)
Agent को किसी भी async function की तरह test करें: LLM की जगह scripted fake model लगाएँ जो पहले से लिखे tool calls और जवाब लौटाता है, फिर final output, चले हुए tools और token accounting पर assert करें। Tests तेज़, मुफ़्त और deterministic बनते हैं। असली model की गुणवत्ता जाँचने वाले "eval" tests अलग रखें।

---

## 🔴 Problem it Solves
Real LLM tests are slow, cost money, need keys in CI and are flaky (output changes run to run). Without tests, refactoring a prompt or adding a tool silently breaks routing, tool arguments, guardrails and error mapping, and you only find out in production.

## 🔴 यह क्यों बना? (Hindi)
असली LLM tests धीमे, महँगे, CI में keys माँगने वाले और अस्थिर (flaky) होते हैं। Tests के बिना prompt बदलने या नया tool जोड़ने पर routing, tool arguments, guardrails और error mapping चुपचाप टूटते हैं और पता production में चलता है।

---

## 🟢 How it Works

```
Layer 1  Unit      scripted Model + real tools -> assert flow (this note)
Layer 2  API       FastAPI TestClient + dependency_overrides -> assert HTTP
Layer 3  Contract  assert tool schemas / guardrails / hooks fire
Layer 4  Eval      real model, small dataset, scored (needs API key; not run here)

Scripted model:
  steps = [ [tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')],   # LLM turn 1
            [text("Duty is 20%")] ]                                    # LLM turn 2
  -> Runner.run drives the REAL loop; only the LLM is fake
  -> assert result.final_output, model.calls, result.new_items[1].output,
     result.context_wrapper.usage.total_tokens
```

## 🟢 कैसे काम करता है? (Hindi)

```
Layer 1  Unit      scripted Model + असली tools -> flow पर assert (यह note)
Layer 2  API       FastAPI TestClient + dependency_overrides -> HTTP पर assert
Layer 3  Contract  tool schemas / guardrails / hooks चल रहे हैं यह जाँचें
Layer 4  Eval      असली model, छोटा dataset, scoring (API key चाहिए; यहाँ नहीं चलाया)

Scripted model:
  steps = [ [tool_call(...)],  # LLM turn 1
            [text("Duty is 20%")] ]  # LLM turn 2
  -> Runner.run असली loop चलाता है; सिर्फ़ LLM नकली है
```

**How the fake works (verified):** subclass `agents.Model` and implement `get_response` (returns `ModelResponse(output=[...], usage=Usage(...), response_id=None)`) and `stream_response`. Pass the instance as `Agent(model=...)`. Each call returns the next scripted step, so `model.calls` counts LLM turns. Tool call items are `ResponseFunctionToolCall`; text is `ResponseOutputMessage`.

**Useful assertions:** `result.final_output`; `model.calls` (number of LLM turns); `result.new_items[1].output` (the tool item's output, which proves the tool really ran); `result.context_wrapper.usage.total_tokens` (our fake reports 15 per call, so 2 turns = 30).

**Hindi नोट:** Tool असली चलता है, इसलिए tool की अपनी branches (जैसे "unknown") भी test होती हैं। Network guard fixture जोड़ें ताकि गलती से असली OpenAI call हो तो test तुरंत fail हो। `set_tracing_disabled(True)` से tests tracing backend को कुछ नहीं भेजते।

---

## 🟡 Real World Example
**Tariff Agent.** Tests: (1) known HS code gives "20%", (2) unknown HS code goes down the tool's `unknown` branch, (3) `/ask` returns 200 with 30 tokens for a two-turn run, (4) empty body returns 422 before any agent runs. CI runs these in under a second with no API key. A nightly job runs 20 real-model eval questions and tracks accuracy.

**Customer Support Agent:** a scripted run asserts that a refund request triggers `issue_refund` exactly once and that the input guardrail blocks "ignore previous instructions".

## 🟡 Real Example Hindi mein
**Tariff Agent.** Tests: (1) ज्ञात HS code पर "20%" मिलता है, (2) अज्ञात HS code tool की `unknown` branch से गुज़रता है, (3) दो-turn run के लिए `/ask` 200 और 30 tokens लौटाता है, (4) खाली body पर agent चलने से पहले ही 422 आता है। CI यह सब API key के बिना एक सेकंड से कम में चलाता है। रात का job 20 असली-model eval सवाल चलाकर accuracy track करता है।

**Customer Support Agent:** scripted run assert करता है कि refund माँगने पर `issue_refund` ठीक एक बार चला और input guardrail "ignore previous instructions" को रोकता है।

---

## 💻 Code Example — Basic
`test_basic.py` (2 tests, async, pytest-asyncio):

```python
# Basic: unit-test an agent with a scripted model - fast, free, deterministic.
# verified against openai-agents 0.24.0, pytest 9.2.0, pytest-asyncio 1.5.0
import pytest                                                     # test runner
from agents import Agent, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text                   # the helper from note 57

set_tracing_disabled(True)                                        # never talk to the tracing backend in tests

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    return {"6109.10": "20%"}.get(hs_code, "unknown")

@pytest.mark.asyncio                                              # async test (pytest-asyncio)
async def test_agent_calls_tool_then_answers() -> None:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text("Duty is 20%")]])
    agent = Agent(name="Tariff", instructions="x", tools=[get_tariff_rate], model=m)
    res = await Runner.run(agent, "rate?")
    assert res.final_output == "Duty is 20%"                      # final answer
    assert m.calls == 2                                           # exactly 2 LLM turns
    assert res.new_items[1].output == "20%"                       # the tool really ran and returned this

@pytest.mark.asyncio
async def test_unknown_hs_code() -> None:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"0000"}')], [text("No data")]])
    res = await Runner.run(Agent(name="T", instructions="x", tools=[get_tariff_rate], model=m), "rate?")
    assert res.new_items[1].output == "unknown"                   # the tool's own branch is covered too
```

## 💻 Code Example — Advanced
Two files. `tariff_app.py` injects the agent through `Depends`, so tests can swap it. `test_api.py` uses `dependency_overrides`, a network guard and parametrised cases.

```python
# tariff_app.py - App under test: agent injected via a FastAPI dependency so tests can swap the model.
from typing import Any
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from agents import Agent, Runner, function_tool

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    return {"6109.10": "20%"}.get(hs_code, "unknown")

def get_agent() -> Agent:                                         # production dependency: real model name (needs OPENAI_API_KEY)
    return Agent(name="Tariff", instructions="Use tools.", tools=[get_tariff_rate], model="gpt-4.1-mini")  # model name: use any you have access to

class Q(BaseModel):
    question: str

app = FastAPI()

@app.post("/ask")
async def ask(q: Q, agent: Agent = Depends(get_agent)) -> dict[str, Any]:
    res = await Runner.run(agent, q.question, max_turns=5)
    return {"answer": str(res.final_output), "tokens": res.context_wrapper.usage.total_tokens}
```

```python
# test_api.py - Advanced: test the FastAPI app with dependency_overrides, a network guard and parametrised cases.
import pytest
from fastapi.testclient import TestClient
from agents import Agent, set_tracing_disabled
from fake import ScriptedModel, tool_call, text
from tariff_app import app, get_agent, get_tariff_rate

set_tracing_disabled(True)

def make_agent(steps: list) -> Agent:                             # build an agent whose model is scripted
    return Agent(name="Tariff", instructions="x", tools=[get_tariff_rate], model=ScriptedModel(steps))

@pytest.fixture(autouse=True)
def no_real_network(monkeypatch: pytest.MonkeyPatch) -> None:     # fail loudly if a test accidentally hits OpenAI
    import httpx
    def blocked(*a, **k):
        raise AssertionError("network call in unit test")
    monkeypatch.setattr(httpx.AsyncClient, "send", blocked)

@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()                              # always reset overrides

@pytest.mark.parametrize("hs,expected", [("6109.10", "20%"), ("0000", "unknown")])
def test_ask_returns_tool_value(client: TestClient, hs: str, expected: str) -> None:
    steps = [[tool_call("get_tariff_rate", '{"hs_code":"%s"}' % hs)], [text(f"Duty: {expected}")]]
    app.dependency_overrides[get_agent] = lambda: make_agent(steps)
    r = client.post("/ask", json={"question": "rate?"})
    assert r.status_code == 200
    assert r.json()["answer"] == f"Duty: {expected}"
    assert r.json()["tokens"] == 30                               # 2 scripted turns x 15 tokens: tests token accounting wiring

def test_validation_error(client: TestClient) -> None:
    assert client.post("/ask", json={}).status_code == 422        # FastAPI rejects bad input before any agent runs
```

**Observed result** (running `pytest -q` in the folder with both test files and `fake.py`): `5 passed in 0.76s`. A pytest-asyncio deprecation warning about `asyncio_default_fixture_loop_scope` was printed; set it in `pytest.ini` to silence it.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Fake LLM for tests | Fake chat models in `langchain_core` | Mock the LLM / patch calls | Subclass `Model` (this note) | `ReplayChatCompletionClient` |
| Test the loop | Invoke compiled graph | `kickoff()` with mocked LLM | `Runner.run` with scripted model | `agent.run` with replay client |
| Assert intermediate steps | State snapshots, stream | Task outputs | `result.new_items` | Message list |
| HTTP layer | FastAPI TestClient | FastAPI TestClient | FastAPI TestClient + `dependency_overrides` | FastAPI TestClient |

_OpenAI SDK column verified in openai-agents 0.24.0; other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Unit tests that call the real model.
✅ Correct: Script the model; keep a few separate, marked eval tests for the real one.

❌ Mistake 2: Asserting on exact LLM wording in eval tests.
✅ Correct: Assert on tool calls, structured fields, or use a rubric/grader; exact strings flake.

❌ Mistake 3: Forgetting to clear `dependency_overrides`.
✅ Correct: Reset in a fixture teardown so one test's fake agent cannot leak into the next.

❌ Mistake 4: Leaving tracing on in tests.
✅ Correct: `set_tracing_disabled(True)` (or a no-op processor) so tests do not try to upload traces.

---

## 🧠 Tricky Interview Question
Your scripted tests are all green but production still routes refunds to the wrong agent. Why, and what do you add?

**Answer:** A scripted model returns exactly the tool call you wrote, so tests prove your plumbing (tool code, hooks, handoff wiring, error mapping), not the model's judgement. Routing quality depends on instructions and the real model. Add an eval suite: 30 to 100 labelled prompts (including edge cases from production logs), run against the real model, score "correct agent chosen" and "correct tool args", track the pass rate over time, run on prompt/model changes, and gate releases on it. Keep scripted tests for deterministic regressions and evals for probabilistic quality.

---

## ⚫ Interview Questions + Answers

**Q1:** How do you test an agent without an API key?

**A1:** Subclass `agents.Model` as a scripted fake that returns pre-written tool calls and messages, and pass it as `Agent(model=...)`.

**Q2:** What do you assert on?

**A2:** `final_output`, number of LLM turns, tool outputs in `new_items`, token usage, hook side effects and HTTP status codes.

**Q3:** How do you test a FastAPI endpoint using an agent?

**A3:** Inject the agent with `Depends` and replace it via `app.dependency_overrides` using a scripted agent.

**Q4:** Unit test vs eval?

**A4:** Unit tests are deterministic and test your code with a fake model; evals use the real model on a dataset and measure probabilistic quality.

**Q5:** System design: CI for a multi-agent product.

**A5:** Per PR: scripted unit and API tests plus lint/type checks (seconds, free). Nightly or on prompt change: eval suite against the real model with cost cap and score thresholds. Record traces of failures, add them to the dataset, and block deploys on regression.

---

## 💰 Cost Impact
Scripted tests cost zero tokens. Evals cost real tokens: `cases x runs x tokens per run x price`. Keep the dataset small, use a cheaper model for graders where acceptable, cache results by prompt hash, and run the full suite only on prompt/model/tool changes. Prices approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Any agent that will reach production
- Refactoring prompts, tools or routing
- CI must run without secrets

❌ Avoid when:
- You rely on scripted tests alone to judge answer quality
- Asserting exact free-text output from a real model
- Tests share state through overrides or globals

---

## 📊 Visual Diagram
```
   pytest
     |
     +--> unit:  Runner.run(Agent(model=ScriptedModel(steps)))
     |             real tools + real loop, fake LLM
     |
     +--> api:   TestClient(app)
     |             app.dependency_overrides[get_agent] = scripted agent
     |             network guard: httpx send -> AssertionError
     |
     +--> eval:  real model on labelled prompts -> score -> threshold
                  (needs OPENAI_API_KEY; separate job)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Scripted model | Fake LLM with fixed replies | निश्चित जवाबों वाला नकली LLM |
| dependency_overrides | Swap FastAPI dependencies in tests | tests में dependencies बदलना |
| Eval | Scored test with real model | असली model से scored test |
| Deterministic | Same result every run | हर बार एक जैसा नतीजा |
| Flaky | Sometimes passes, sometimes fails | कभी pass, कभी fail |
| Network guard | Fails on unexpected HTTP | अनचाहे HTTP पर fail |

---

## ⚡ 3-Line Summary
English: Replace the LLM with a scripted Model and test the real loop, tools and HTTP layer offline.
Use dependency_overrides for FastAPI and a network guard to prevent accidental real calls.
Add a separate eval suite for real model quality.

Hindi: LLM की जगह scripted Model रखें और असली loop, tools और HTTP layer को offline test करें।
FastAPI के लिए dependency_overrides और अनचाहे असली calls रोकने के लिए network guard इस्तेमाल करें।
असली model की गुणवत्ता के लिए अलग eval suite जोड़ें।

---

## ➡️ Next Topic
**#68 SDK vs LangGraph - When to Choose** - the decision framework: model-driven agents versus explicit graphs with checkpoints.

---
