---

# 113. Flow + Crew Together
# हिंदी में: Flow और Crew को एक साथ इस्तेमाल करना
# Framework: CrewAI
# Already Known: No

> Verified against crewai 1.15.41 (offline, with a fake LLM; no real model calls were made).

---

## 🔵 Simple Definition (2-3 lines)
A **Flow** is the deterministic "backbone" of your app: typed state, steps, branching. A **Crew** is a team of LLM agents that does the fuzzy thinking inside one step. Together: Flow controls the order and the rules, Crew does the reasoning when reasoning is needed.

## 🔵 सरल परिभाषा (Hindi)
**Flow** आपके app की पक्की "रीढ़" है: typed state, steps और branching। **Crew** LLM agents की टीम है जो किसी एक step के अंदर सोचने वाला काम करती है। दोनों साथ में: Flow क्रम और नियम तय करता है, Crew तब reasoning करती है जब उसकी ज़रूरत हो।

---

## 🔴 Problem it Solves
A crew alone is hard to control: you cannot easily say "validate input first, run the crew only if the item is valid, then save to DB". Plain Python glue code works but has no shared state, no event tracking, no resume. A pure Flow with no agents cannot handle open-ended text tasks like HS-code classification.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ Crew को control करना मुश्किल है: "पहले input validate करो, item सही हो तभी crew चलाओ, फिर DB में save करो" जैसा क्रम आसानी से नहीं बनता। साधारण Python glue code चलता है, पर उसमें shared state, event tracking और resume नहीं होता। सिर्फ Flow (बिना agents) HS-code classification जैसे खुले text काम नहीं कर सकता।

---

## 🟢 How it Works

```
Step 1 → class MyFlow(Flow[State]) with a pydantic State
Step 2 → @start() method: validate / normalise input, write to self.state
Step 3 → @listen(step) method: build a Crew, call crew.kickoff(inputs=...)
Step 4 → Store crew output (out.raw / out.pydantic) back into self.state
Step 5 → Next @listen method: plain Python (DB save, rules, formatting)
Step 6 → flow.kickoff(inputs={...}) returns the LAST method's return value
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → class MyFlow(Flow[State]) बनाओ, pydantic State के साथ
Step 2 → @start() method: input validate / साफ़ करो, self.state में लिखो
Step 3 → @listen(step) method: Crew बनाओ, crew.kickoff(inputs=...) चलाओ
Step 4 → Crew का output (out.raw / out.pydantic) वापस self.state में रखो
Step 5 → अगला @listen method: साधारण Python (DB save, rules, formatting)
Step 6 → flow.kickoff(inputs={...}) आख़िरी method की return value लौटाता है
```

---

## 🟡 Real World Example
**Tariff Agent**: user sends "100 cotton t-shirts from Vietnam". Flow step 1 normalises the text. Step 2 runs a 1-agent Crew (Tariff Analyst) that returns an HS code. Step 3 is plain Python: look up the duty rate table for that code and compute landed cost. The LLM is used only where language understanding is needed; money maths stays in code.

## 🟡 Real Example Hindi mein
**Tariff Agent**: user लिखता है "Vietnam से 100 cotton t-shirts"। Flow का step 1 text साफ़ करता है। Step 2 में 1-agent Crew (Tariff Analyst) HS code निकालती है। Step 3 साधारण Python है: उस code की duty rate table देखो और landed cost निकालो। LLM सिर्फ़ वहीं लगता है जहाँ भाषा समझनी हो; पैसों का हिसाब code में रहता है।

---

## 💻 Code Example — Basic
```python
# Run directly: python flow_crew_basic.py  (no API key needed, uses a fake LLM)
import os                                              # to switch off telemetry for the demo
os.environ["OTEL_SDK_DISABLED"] = "true"               # no tracing export during local run
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # no telemetry in the demo

from typing import Any                                 # type hint helper
from pydantic import BaseModel                         # typed Flow state
from crewai import Agent, Task, Crew, BaseLLM, Flow    # core CrewAI classes
from crewai.flow.flow import listen, start             # Flow decorators


class FakeLLM(BaseLLM):                                # offline stand-in for a real model
    def __init__(self, text: str = "Thought: ok\nFinal Answer: HS 6109.10") -> None:
        super().__init__(model="fake")                 # BaseLLM needs a model name
        self._text = text                              # canned reply

    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        return self._text                              # always return the canned answer

    def supports_function_calling(self) -> bool:       # tell CrewAI to use ReAct text mode
        return False


class TariffState(BaseModel):                          # shared state for all Flow steps
    item: str = ""                                     # raw user text
    hs_code: str = ""                                  # filled by the crew


class TariffFlow(Flow[TariffState]):                   # Flow generic over our state
    @start()                                           # entry point
    def intake(self) -> str:
        self.state.item = self.state.item.strip().lower()  # normalise input
        return self.state.item                         # passed to the next listener

    @listen(intake)                                    # runs after intake finishes
    def classify(self) -> str:
        agent = Agent(role="Tariff Analyst", goal="Find the HS code",
                      backstory="Customs expert", llm=FakeLLM(),
                      allow_delegation=False)          # one worker agent
        task = Task(description="Classify {item}", expected_output="HS code",
                    agent=agent)                       # one task for it
        out = Crew(agents=[agent], tasks=[task], tracing=False).kickoff(
            inputs={"item": self.state.item})          # run the crew INSIDE the flow
        self.state.hs_code = out.raw                   # save result in shared state
        return out.raw                                 # last return = flow result


flow = TariffFlow()                                    # create flow instance
print(flow.kickoff(inputs={"item": "  Cotton T-Shirt "}))  # prints: HS 6109.10
print(flow.state.hs_code)                              # state survives after kickoff
```
Ran offline: prints `HS 6109.10`. **Tokens**: with a real LLM, one ReAct run is roughly 600-1500 tokens (approximate, depends on prompt).

## 💻 Code Example — Advanced
```python
# Production-style: Flow + Crew behind FastAPI, async, timeout, error handling, token usage
# Run: python flow_crew_api.py  (uses FakeLLM + TestClient; swap FakeLLM for a real LLM in prod)
import asyncio                                         # async primitives + timeout
import os                                              # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only

from typing import Any                                 # type hints
from fastapi import FastAPI, HTTPException             # web layer
from fastapi.testclient import TestClient              # offline testing of the API
from pydantic import BaseModel                         # request/response/state models
from crewai import Agent, Task, Crew, BaseLLM, Flow    # CrewAI core
from crewai.flow.flow import listen, start             # Flow decorators


class FakeLLM(BaseLLM):                                # same offline model as above
    def __init__(self) -> None:
        super().__init__(model="fake")
    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        return "Thought: ok\nFinal Answer: HS 6109.10"
    def supports_function_calling(self) -> bool:
        return False


DUTY_TABLE: dict[str, float] = {"6109.10": 0.12}       # deterministic data lives in code, not in LLM


class State(BaseModel):                                # typed flow state
    item: str = ""                                     # input
    hs_code: str = ""                                  # crew output
    duty_rate: float = 0.0                             # table lookup
    total_tokens: int = 0                              # usage reported by the crew


class TariffFlow(Flow[State]):
    @start()
    def validate(self) -> None:
        if len(self.state.item) < 3:                   # cheap check BEFORE spending tokens
            raise ValueError("item too short")         # flow fails fast, no LLM call

    @listen(validate)
    def run_crew(self) -> None:
        agent = Agent(role="Tariff Analyst", goal="HS code for {item}",
                      backstory="Customs expert", llm=FakeLLM(), allow_delegation=False)
        task = Task(description="Classify {item}", expected_output="HS code", agent=agent)
        out = Crew(agents=[agent], tasks=[task], tracing=False).kickoff(
            inputs={"item": self.state.item})          # sync call; flow runs it in a worker
        self.state.hs_code = out.raw.replace("HS ", "").strip()  # keep only the code
        self.state.total_tokens = out.token_usage.total_tokens   # real LLMs fill this field

    @listen(run_crew)
    def price(self) -> dict[str, Any]:
        self.state.duty_rate = DUTY_TABLE.get(self.state.hs_code, 0.0)  # pure Python rule
        return {"hs_code": self.state.hs_code, "duty_rate": self.state.duty_rate,
                "tokens": self.state.total_tokens}     # final API payload


app = FastAPI()                                        # web app


class Req(BaseModel):                                  # request body
    item: str


@app.post("/tariff")
async def tariff(req: Req) -> dict[str, Any]:
    try:                                               # wrap the whole run
        result = await asyncio.wait_for(               # hard time limit protects the worker
            TariffFlow().kickoff_async(inputs={"item": req.item}), timeout=60)
        return result                                  # dict from price()
    except asyncio.TimeoutError:                       # slow LLM / stuck tool
        raise HTTPException(504, "flow timeout")
    except ValueError as e:                            # our own validation errors
        raise HTTPException(422, str(e))
    except Exception as e:                             # anything else: do not leak internals
        raise HTTPException(502, f"flow failed: {type(e).__name__}")


with TestClient(app) as client:                        # offline smoke test
    print(client.post("/tariff", json={"item": "cotton t-shirt"}).json())
```
Ran offline: returns `{'hs_code': '6109.10', 'duty_rate': 0.12, 'tokens': 0}` (tokens are 0 only because the fake LLM reports no usage).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Deterministic backbone | `StateGraph` nodes + edges | `Flow` with `@start/@listen/@router` | Plain Python around `Runner.run` | `GraphFlow` / custom runtime |
| Agent team inside a step | Sub-graph or agent node | `Crew` inside a Flow method | Handoffs between agents | `RoundRobinGroupChat` etc. |
| Shared typed state | `TypedDict`/pydantic state | pydantic `Flow[State]` | Context object | Message history / agent state |
| Learning curve | Medium | Low | Low | Medium-High |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Putting every step in a Crew, so even simple "save to DB" or tax maths goes through an LLM.
✅ Correct: Use Flow methods (plain Python) for deterministic work; call a Crew only for language/reasoning steps.

❌ Mistake 2: Creating a global Crew object and reusing it across requests.
✅ Correct: Build the Crew inside the Flow method (or a factory) so each request has clean state and inputs.

❌ Mistake 3: Forgetting that `flow.kickoff()` returns only the last method's value.
✅ Correct: Keep what you need in `self.state` and return an explicit final payload from the last step.

---

## 🧠 Tricky Interview Question
Your Flow calls a Crew in step 2. Under load, the API worker freezes for minutes. Why, and how do you fix it?

Answer: `crew.kickoff()` is synchronous and blocks the thread. Inside an `async` FastAPI route it also blocks the event loop if called directly. Fix: use `await flow.kickoff_async(...)` (or `crew.kickoff_async`), wrap it with `asyncio.wait_for` for a timeout, set `max_iter` / `max_execution_time` on agents, and bound concurrency with a semaphore so one slow provider does not exhaust workers.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is the difference between a Flow and a Crew?
A1: A Crew is a team of agents solving tasks (LLM-driven). A Flow is event-driven Python orchestration with typed state (code-driven). Flows can contain Crews.

Q2: [Medium] How does data move between Flow steps?
A2: Through `self.state` (a pydantic model or dict) and through return values passed to `@listen` methods.

Q3: [Hard] Why not build everything as one big Crew?
A3: Cost, latency and unpredictability. LLM steps are non-deterministic and billed per token. Rules, validation and DB writes are cheaper and safer as code. Flow gives you that split with tracing and resume.

Q4: [Hard] How would you test a Flow that contains a Crew without calling an LLM?
A4: Subclass `BaseLLM` with a canned `call()` (as above) or monkeypatch the crew factory; assert on `flow.state` and the returned payload. Test each step's pure-Python logic separately.

Q5: [System Design] Design a customs classification service that handles 50 requests per second.
A5: FastAPI + a queue (e.g. Redis/Celery) in front; workers run `TariffFlow.kickoff_async`; cache `(item text -> HS code)` to skip repeat LLM calls; per-request timeout and retry; rate limit per provider (`max_rpm`); store flow state for audit; autoscale workers on queue depth.

---

## 💰 Cost Impact
- Tokens per run = sum over crew LLM calls of (prompt + completion). Formula: `cost = (prompt_tokens x input_price + completion_tokens x output_price) / 1M`.
- A 1-agent, 1-task ReAct run is typically on the order of hundreds to low thousands of tokens (approximate; verify with `out.token_usage` on your real model).
- Tips: validate in the Flow before the Crew; cache repeated inputs; use a small model for classification and a large one only for hard cases; keep `max_iter` low.

---

## 🔷 When to Use
✅ Use when:
- You need rules/validation/DB steps around LLM reasoning
- You want typed shared state and event tracing
- Different steps need different agent teams

❌ Avoid when:
- A single prompt or single agent is enough
- You only need a quick prototype with one Crew

---

## 📊 Visual Diagram
```
 request
    |
    v
+---------+     +--------------------+     +-----------+
| @start  | --> | @listen: Crew run  | --> | @listen:  |
| validate|     |  Agent -> Task ->  |     | price()   |
| (code)  |     |  LLM (tokens $)    |     | (code)    |
+---------+     +--------------------+     +-----------+
      \________ self.state (pydantic) shared by all ______/
                              |
                              v
                        JSON response
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Flow | Event-driven orchestration class | इवेंट-आधारित orchestration class |
| Crew | Team of agents and tasks | agents और tasks की टीम |
| `@start` | First step of a Flow | Flow का पहला step |
| `@listen` | Runs after another step | किसी step के बाद चलने वाला step |
| State | Shared typed data | साझा typed डेटा |
| kickoff | Start execution | चलाना शुरू करना |

---

## ⚡ 3-Line Summary
English: Flow = deterministic backbone with typed state. Crew = LLM team used only inside the steps that need reasoning. Build Crews inside Flow methods, keep money/validation in code, run async with timeouts.
Hindi: Flow = typed state वाली पक्की रीढ़। Crew = LLM टीम जो सिर्फ़ सोचने वाले steps में लगती है। Crew को Flow method के अंदर बनाओ, पैसे/validation code में रखो, async और timeout के साथ चलाओ।

---

## ➡️ Next Topic
**114. Flow Conditional Branching** — real systems must route differently (auto-approve vs human review) depending on confidence; `@router` does exactly that.

---
