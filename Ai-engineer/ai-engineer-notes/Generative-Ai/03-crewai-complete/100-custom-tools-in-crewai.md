---

# 100. Custom Tools in CrewAI
# हिंदी में: CrewAI में अपने Custom Tools बनाना
# Framework: CrewAI
# Already Known: No

---

> Verified against crewai 1.15.41 (Python 3.13.3, httpx, fastapi 0.163.1). Both code samples were run offline: the LLM is the scripted `ScriptedLLM` from note #99 (`fake.py`), and the "HTTP API" is served by `httpx.MockTransport`, so no network or API key was needed. NOT run: any real LLM call (needs an LLM key) and any real tariff API. No token or latency numbers are claimed.

---

## 🔵 Simple Definition (2-3 lines)
A custom tool is your own Python function or class that an agent may call. In CrewAI you make one with the `@tool("name")` decorator (quick) or by subclassing `BaseTool` with a Pydantic `args_schema` (full control). CrewAI validates the arguments before your code runs.

## 🔵 सरल परिभाषा (Hindi)
Custom tool आपका अपना Python function या class है जिसे agent बुला सकता है। CrewAI में इसे `@tool("नाम")` decorator से (जल्दी) या `BaseTool` को subclass करके Pydantic `args_schema` के साथ (पूरा control) बनाते हैं। आपका code चलने से पहले CrewAI arguments को validate करता है।

---

## 🔴 Problem it Solves
Built-in tools (note #99) cannot know your tariff API, your database or your business rules. Without a proper tool the agent either hallucinates the answer or you paste raw data into the prompt (expensive and leaky). A tool gives the model a narrow, validated, auditable way to act.

## 🔴 यह क्यों बना? (Hindi)
Built-in tools (note #99) आपकी tariff API, database या business rules नहीं जानते। सही tool के बिना agent जवाब गढ़ देता है या आप raw data prompt में चिपकाते हैं (महँगा और जोखिम भरा)। Tool मॉडल को काम करने का एक संकरा, validated और audit-योग्य रास्ता देता है।

---

## 🟢 How it Works

```
Step 1 → define tool: name + description + args_schema (type hints or Pydantic)
Step 2 → Agent(tools=[tool]) : name/description/schema go into the prompt
Step 3 → LLM emits Action: <name>  Action Input: {json}
Step 4 → CrewAI validates json against args_schema
           bad args  -> error text goes back to the LLM (it can retry)
Step 5 → tool.run(...) -> your _run()/_arun() executes
           returns str  -> Observation
           returns ToolFailure -> framework records "tool did not succeed"
Step 6 → guards: max_usage_count, cache_function, result_as_answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → tool परिभाषित करो: नाम + description + args_schema (type hints या Pydantic)
Step 2 → Agent(tools=[tool]) : नाम/description/schema prompt में जाते हैं
Step 3 → LLM लिखता है Action: <नाम>  Action Input: {json}
Step 4 → CrewAI json को args_schema से validate करता है
           गलत args -> error text LLM को वापस जाता है (वह फिर कोशिश कर सकता है)
Step 5 → tool.run(...) -> आपका _run()/_arun() चलता है
           str लौटाया  -> Observation
           ToolFailure लौटाया -> framework दर्ज करता है "tool सफल नहीं हुआ"
Step 6 → guards: max_usage_count, cache_function, result_as_answer
```

**What we confirmed by running it (crewai 1.15.41):**
- `@tool("Tariff Lookup")` on a typed function gives a `Tool` object; its `args_schema` is built from the type hints (`hs_code: str` -> required string) and its description from the docstring.
- `BaseTool` subclass fields we used successfully: `name`, `description`, `args_schema`, `max_usage_count`, `cache_function`, `result_as_answer`. `BaseTool.model_fields` on this version also lists `env_vars`, `result_schema`, `tool_failure_policy` and `current_usage_count`.
- Calling `tool.run(q=5)` where a `str` is required raised `ValueError: Tool 'T' arguments validation failed ...` before `_run` executed.
- With `max_usage_count=2`, the third `run()` did not raise; it returned a `ToolFailure(... reason=USAGE_LIMIT ...)` object. Call `tool.reset_usage_count()` to reset.
- If your `_run` raises (we raised `ValueError("bad")`), a direct `tool.run()` re-raises it. Inside a crew, the framework catches tool exceptions and feeds the text back to the agent (`ToolFailureReason.EXCEPTION`, from the installed source; we did not force that path in a crew run).
- `async def _arun` is used by `await tool.arun(...)`. `tool.to_structured_tool()` exists (used internally).
- `from crewai.tools import ToolFailure` works; returning one from `_run`/`_arun` marks the call as failed with `message`, `code`, `retryable`, `details`. The default policy is `WARN` (record + emit event + continue).

**Hindi नोट:** Tool में हमेशा (1) साफ़ description लिखो, (2) `args_schema` से input validate कराओ, (3) failure पर exception दबाकर "सब ठीक है" मत लौटाओ, `ToolFailure` लौटाओ, (4) `max_usage_count` से खर्च की सीमा रखो।

---

## 🟡 Real World Example
**Tariff Agent.** Two custom tools: `Tariff Lookup` (HS code -> duty rate, from the company DB) and `Duty Calculator` (value x rate). The agent first looks up the rate, then calculates duty. The calculator is deterministic Python, so the LLM never does arithmetic.

**Code Agent:** a `Run Tests` tool with `max_usage_count=3` so it cannot loop forever.

## 🟡 Real Example Hindi mein
**Tariff Agent.** दो custom tools: `Tariff Lookup` (HS code -> duty दर, कंपनी के DB से) और `Duty Calculator` (value x दर)। Agent पहले दर खोजता है, फिर duty निकालता है। Calculator साधारण Python है, इसलिए गणित LLM को नहीं करना पड़ता।

**Code Agent:** `Run Tests` tool जिस पर `max_usage_count=3` है ताकि वह अनंत loop में न फँसे।

---

## 💻 Code Example — Basic
Runs offline (needs `fake.py` from note #99).

```python
# Basic: two ways to build a custom CrewAI tool - @tool decorator and BaseTool subclass. Runs offline.
# verified against crewai 1.15.41
import os
os.environ["OTEL_SDK_DISABLED"] = "true"; os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
from typing import Type                                            # for args_schema annotation
from pydantic import BaseModel, Field                              # input schema
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool, tool                            # both ways to define tools
from fake import ScriptedLLM

RATES: dict[str, str] = {"8471": "0%", "6403": "8%"}               # fake tariff table

@tool("Tariff Lookup")                                             # way 1: decorator; docstring becomes the description
def tariff_lookup(hs_code: str) -> str:                            # type hints become the args schema
    """Return the duty rate for a 4-digit HS code."""
    return RATES.get(hs_code, "unknown")                           # plain dict lookup

class DutyInput(BaseModel):                                        # way 2: explicit schema
    value_usd: float = Field(..., description="Customs value in USD")
    rate_pct: float = Field(..., description="Duty rate in percent")

class DutyCalculator(BaseTool):                                    # way 2: subclass BaseTool
    name: str = "Duty Calculator"                                  # name the LLM sees
    description: str = "Compute duty = value * rate / 100."        # tells the LLM when to use it
    args_schema: Type[BaseModel] = DutyInput                       # arguments are validated against this
    def _run(self, value_usd: float, rate_pct: float) -> str:      # sync implementation
        return f"{value_usd * rate_pct / 100:.2f} USD"

calc = DutyCalculator()
print(tariff_lookup.name, "->", tariff_lookup.run(hs_code="6403"))          # Tariff Lookup -> 8%
print(calc.name, "->", calc.run(value_usd=1000, rate_pct=8))                # 80.00 USD
print(sorted(DutyInput.model_json_schema()["properties"]))                  # ['rate_pct', 'value_usd']

llm = ScriptedLLM(model="fake", replies=[
    'Thought: lookup\nAction: Tariff Lookup\nAction Input: {"hs_code": "6403"}',
    'Thought: calc\nAction: Duty Calculator\nAction Input: {"value_usd": 1000, "rate_pct": 8}',
    'Thought: done\nFinal Answer: Duty is 80.00 USD.'])
agent = Agent(role="Tariff Agent", goal="Compute duty", backstory="Broker", tools=[tariff_lookup, calc], llm=llm)
task = Task(description="Duty on 1000 USD of HS 6403?", expected_output="amount", agent=agent)
print(Crew(agents=[agent], tasks=[task], verbose=False).kickoff().raw)       # Duty is 80.00 USD.
```

Output we got: `Tariff Lookup -> 8%`, `Duty Calculator -> 80.00 USD`, `['rate_pct', 'value_usd']`, `Duty is 80.00 USD.`

## 💻 Code Example — Advanced
Async HTTP tool with timeout, `ToolFailure` for business and transport errors, a usage cap, a cache policy that never caches failures, pattern-validated input, and a FastAPI endpoint. The HTTP service is simulated with `httpx.MockTransport`.

```python
# Advanced: production-style custom tool - async HTTP, ToolFailure, usage cap, cache policy, FastAPI.
# verified against crewai 1.15.41, httpx, fastapi 0.163.1. HTTP is served by httpx.MockTransport (no network).
# Real LLM: not run - needs an LLM key. (ScriptedLLM stands in.)
import os
os.environ["OTEL_SDK_DISABLED"] = "true"; os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
from typing import Any, Type
import httpx                                                       # async HTTP client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool, ToolFailure                     # ToolFailure = "I ran but did not succeed"
from fake import ScriptedLLM

def _handler(request: httpx.Request) -> httpx.Response:            # fake tariff API
    code = request.url.params.get("hs")
    if code == "8471":
        return httpx.Response(200, json={"hs": code, "rate": "0%"})
    return httpx.Response(404, json={"error": "unknown hs"})
TRANSPORT = httpx.MockTransport(_handler)                          # swap for real transport in production

class RateInput(BaseModel):
    hs_code: str = Field(..., pattern=r"^\d{4}$", description="4-digit HS code")   # validated BEFORE _run

def cache_only_success(args: dict[str, Any], result: Any) -> bool:  # cache policy: never cache failures
    return not isinstance(result, ToolFailure)

class TariffRateTool(BaseTool):
    name: str = "Tariff Rate API"
    description: str = "Look up the duty rate for a 4-digit HS code from the tariff service."
    args_schema: Type[BaseModel] = RateInput
    max_usage_count: int | None = 3                                # hard cap on calls per tool instance (cost guard)
    cache_function: Any = cache_only_success                       # field on BaseTool; decides if a result is cached

    def _run(self, hs_code: str) -> str | ToolFailure:             # sync path
        import asyncio
        return asyncio.run(self._arun(hs_code))                    # reuse async code (only safe outside a running loop)

    async def _arun(self, hs_code: str) -> str | ToolFailure:      # async path used by async crews
        try:
            async with httpx.AsyncClient(transport=TRANSPORT, timeout=5.0) as c:   # timeout always
                r = await c.get("http://tariff.local/rate", params={"hs": hs_code})
            if r.status_code == 404:                               # business failure: tell the framework
                return ToolFailure(message=f"HS {hs_code} not found", code="not_found", retryable=False)
            r.raise_for_status()                                   # other HTTP errors raise
            return f"{hs_code}: {r.json()['rate']}"
        except httpx.HTTPError as e:                               # transport errors -> retryable failure
            return ToolFailure(message=f"tariff API error: {e}", code="http_error", retryable=True)

tool = TariffRateTool()
app = FastAPI()

class Q(BaseModel):
    hs_code: str

@app.post("/duty")
async def duty(q: Q) -> dict[str, str]:
    llm = ScriptedLLM(model="fake", replies=[
        f'Thought: call API\nAction: Tariff Rate API\nAction Input: {{"hs_code": "{q.hs_code}"}}',
        'Thought: done\nFinal Answer: see tool result'])
    agent = Agent(role="Tariff Agent", goal="Get rate", backstory="b", tools=[tool], llm=llm, max_iter=4)
    task = Task(description=f"Rate for {q.hs_code}", expected_output="rate", agent=agent)
    try:
        out = await Crew(agents=[agent], tasks=[task], verbose=False).kickoff_async()
    except Exception as e:
        raise HTTPException(502, f"{type(e).__name__}: {e}")
    return {"answer": out.raw, "tool_result_seen": str(any("0%" in m for m in llm.seen))}   # did the tool output reach the LLM prompt?

if __name__ == "__main__":
    import asyncio
    print(asyncio.run(tool.arun(hs_code="8471")))                  # 8471: 0%
    print(asyncio.run(tool.arun(hs_code="9999")))                  # ToolFailure(... not_found ...)
    try:
        tool.run(hs_code="84")                                     # fails pattern validation
    except Exception as e:
        print("validation:", type(e).__name__)
    from fastapi.testclient import TestClient
    print(TestClient(app).post("/duty", json={"hs_code": "8471"}).json())
```

Output we got: `8471: 0%`; `message='HS 9999 not found' reason=<ToolFailureReason.TOOL_REPORTED: 'tool_reported'> code='not_found' retryable=False details={}`; `validation: ValueError`; `{'answer': 'see tool result', 'tool_result_seen': 'True'}`.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Define a tool | LangChain `@tool` / `StructuredTool` | `@tool("name")` or `BaseTool` subclass | `@function_tool` | Plain function / `FunctionTool` |
| Input schema | From type hints / Pydantic | `args_schema` (Pydantic) or type hints | From type hints | From type hints |
| Async | `ainvoke` / async funcs | `_arun` / `arun` | `async def` tools | async funcs |
| Usage cap per tool | Your code | `max_usage_count` | Your code | Your code |
| Structured failure | Return/raise yourself | `ToolFailure` object | Error handler on tool | Your code |

_CrewAI column verified in crewai 1.15.41. The other columns are from general knowledge and were not re-verified here._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Vague description such as "does stuff".
✅ Correct: Say what it does, the input meaning and when to use it. The LLM picks tools from the description.

❌ Mistake 2: Returning `"Error"` text on failure so the framework thinks the call succeeded.
✅ Correct: Return `ToolFailure(message=..., code=..., retryable=...)` (or raise for real bugs).

❌ Mistake 3: No `args_schema` constraints (e.g. accepting any string as an HS code).
✅ Correct: Use `Field(pattern=...)`, ranges and enums; bad input is rejected before your code runs.

❌ Mistake 4: Blocking calls (`requests.get`) inside `_arun`.
✅ Correct: Use `httpx.AsyncClient` with a timeout; calling `asyncio.run` inside `_run` is only safe when no event loop is running in that thread (in our FastAPI sample it ran fine because crews execute tool code off the loop; test your own setup).

❌ Mistake 5: One shared tool object holding per-user state.
✅ Correct: Build tools per request, or keep state outside the tool. Note `current_usage_count` is per tool object.

---

## 🧠 Tricky Interview Question
Your custom tool sometimes hits a flaky API. The agent retries the same failing call five times and burns tokens. How do you fix it properly?

**Answer:** Classify failures. Business failures (404, "not found") should return `ToolFailure(retryable=False)` so the agent stops asking. Transport failures (timeout, 5xx) are `retryable=True`, but retries belong inside the tool with a small bounded backoff, not in the LLM loop (each LLM retry costs a whole prompt). Add `max_usage_count`, an agent `max_iter`, a `cache_function` that does not cache failures, and a timeout on the HTTP client. The framework also has a `REPEATED_CALL` failure reason (seen in the installed source) for the agent repeating the same call, and a `tool_failure_policy` field where you can choose `RAISE` to abort the task; check how your version applies the policy before relying on it.

---

## ⚫ Interview Questions + Answers

**Q1:** Two ways to create a CrewAI tool?

**A1:** The `@tool("Name")` decorator on a typed, documented function, or subclass `BaseTool` with `name`, `description`, `args_schema` and `_run`.

**Q2:** Where does the tool description go and why does it matter?

**A2:** Into the agent prompt. The LLM chooses tools by name/description, so poor wording causes wrong or missed calls.

**Q3:** What happens with invalid arguments?

**A3:** In our test `tool.run()` raised a `ValueError` saying argument validation failed; inside a crew the error text is fed back to the agent so it can correct the call.

**Q4:** `_run` vs `_arun`?

**A4:** `_run` is sync, `_arun` is async; `arun()` awaits `_arun`. Use `_arun` with async HTTP/DB clients so one slow tool does not block the event loop.

**Q5:** Design: a tool that writes to a database safely.

**A5:** Narrow schema (enum of allowed operations, bounded values), parameterised SQL only, a read-only DB role by default, `max_usage_count`, idempotency key in the args, `ToolFailure` for constraint errors, human approval for destructive actions, and an audit log row per call (tenant, args hash, result).

---

## 💰 Cost Impact
A custom tool costs tokens in three places: its description + schema (every LLM call), its arguments (output tokens), and its result (input tokens on every later call). Keep descriptions short, return compact results (IDs and summaries, not full tables), and push arithmetic and filtering into Python. Caps (`max_usage_count`, `max_iter`) bound the worst case. We did not measure real tokens; to estimate, count tokens of your schema + typical result and multiply by the number of LLM steps. Prices are approximate - verify with your provider.

---

## 🔷 When to Use
✅ Use when:
- You need your own API, DB or business rule
- You want deterministic code (math, validation) instead of LLM guessing
- You need a narrow, auditable action surface

❌ Avoid when:
- A built-in tool already does it safely (note #99)
- The "tool" is really a multi-step process; make it a Flow (notes #107-112) or a Task
- You would expose unrestricted shell / SQL to the model

---

## 📊 Visual Diagram
```
 LLM output:  Action: Tariff Rate API
              Action Input: {"hs_code": "8471"}
                    |
                    v
            +------------------+   invalid ----> error text -> LLM retries
            | args_schema      |
            | (Pydantic check) |
            +--------+---------+
                     | valid
                     v
            +------------------+   count > max_usage_count --> ToolFailure(USAGE_LIMIT)
            | usage + cache    |
            +--------+---------+
                     v
            +------------------+      +---------------------------+
            | _arun / _run     | ---> | HTTP API (timeout 5 s)    |
            +--------+---------+      +---------------------------+
                     |
          str result | ToolFailure(code, retryable)
                     v
              Observation -> LLM
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| @tool | Decorator that turns a function into a tool | function को tool बनाने वाला decorator |
| BaseTool | Class to subclass for full control | पूरे control के लिए base class |
| args_schema | Pydantic model validating inputs | inputs जाँचने वाला Pydantic model |
| ToolFailure | Object saying "tool ran but failed" | "tool चला पर सफल नहीं हुआ" का object |
| max_usage_count | Cap on calls per tool instance | tool के calls की सीमा |
| cache_function | Decides whether a result is cached | result cache करना है या नहीं |
| result_as_answer | Tool output becomes the final answer | tool का output ही अंतिम उत्तर |

---

## ⚡ 3-Line Summary
English: Make custom tools with `@tool` or `BaseTool` plus a Pydantic `args_schema`; input is validated before your code runs.
Return `ToolFailure` for failed calls, cap usage, use async I/O with timeouts.
Keep descriptions sharp and results small to save tokens.

Hindi: Custom tools `@tool` या `BaseTool` और Pydantic `args_schema` से बनते हैं; आपके code से पहले input validate होता है।
Failed call पर `ToolFailure` लौटाएँ, usage सीमित करें, timeout के साथ async I/O इस्तेमाल करें।
Description साफ़ और result छोटा रखें ताकि tokens बचें।

---

## ➡️ Next Topic
**#101 CrewAI Memory - Complete** - tools let agents act; memory lets them remember across tasks and runs. Important: memory changed a lot in crewai 1.15, so the next notes are checked against that version.

---
