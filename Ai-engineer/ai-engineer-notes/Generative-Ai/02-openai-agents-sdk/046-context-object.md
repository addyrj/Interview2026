---

# 46. Context Object
# हिंदी में: Context Object (run के साथ अपना डेटा भेजना)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (no API key). I confirmed the context argument is hidden from the tool's JSON schema (`properties` was empty) and that per-request contexts stayed isolated across two FastAPI calls.

---

## 🔵 Simple Definition (2-3 lines)
The context object is any Python object (dataclass, pydantic model, dict) that you pass to `Runner.run(..., context=obj)`. It is handed to your tools, guardrails, hooks and dynamic instructions, but it is local dependency injection: it is never sent to the LLM.

## 🔵 सरल परिभाषा (Hindi)
Context object कोई भी Python object (dataclass, pydantic model, dict) है जिसे आप `Runner.run(..., context=obj)` में देते हैं। यह आपके tools, guardrails, hooks और dynamic instructions तक पहुँचता है, पर यह सिर्फ़ local dependency injection है: LLM को यह कभी नहीं भेजा जाता।

---

## 🔴 Problem it Solves
Tools need things the model must not control or see: the current user id, a database pool, tenant settings, API clients, feature flags. Without a context you end up with globals (unsafe across concurrent requests), or you put the user id in the prompt (the model can change it, and it leaks into logs and traces). A typed per-run context gives each request its own dependencies safely.

## 🔴 यह क्यों बना? (Hindi)
Tools को कुछ ऐसी चीज़ें चाहिए जो model को न देखनी चाहिए न बदलनी चाहिए: current user id, database pool, tenant settings, API clients, feature flags। Context के बिना आप globals (concurrent requests में असुरक्षित) इस्तेमाल करेंगे, या user id को prompt में डालेंगे (model उसे बदल सकता है और वह logs/traces में leak होता है)। Typed per-run context हर request को अपनी dependencies सुरक्षित तरीके से देता है।

---

## 🟢 How it Works

```
Step 1 -> Define a context type: @dataclass AppCtx(user_id, db, ...)
Step 2 -> Type the agent: Agent[AppCtx](...)   (helps IDE + type checker)
Step 3 -> Tools take  ctx: RunContextWrapper[AppCtx]  as FIRST param
          (the SDK removes it from the JSON schema the LLM sees)
Step 4 -> Create ONE context object per request
Step 5 -> Runner.run(agent, input, context=ctx)
Step 6 -> Inside tools/hooks/guardrails: ctx.context.<your field>
Step 7 -> After the run: you still hold ctx (counters, audit list)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Context type बनाओ: @dataclass AppCtx(user_id, db, ...)
Step 2 -> Agent को type दो: Agent[AppCtx](...)  (IDE + type checker के लिए)
Step 3 -> Tools का FIRST param  ctx: RunContextWrapper[AppCtx]  रखो
          (SDK इसे LLM वाले JSON schema से हटा देता है)
Step 4 -> हर request के लिए एक नया context object बनाओ
Step 5 -> Runner.run(agent, input, context=ctx)
Step 6 -> tools/hooks/guardrails में: ctx.context.<आपका field>
Step 7 -> Run के बाद ctx आपके पास है (counters, audit list)
```

**Verified in 0.24.0:** `Runner.run(starting_agent, input, context=None, max_turns=10, hooks=None, run_config=None, ...)`; `RunContextWrapper` is exported from `agents`; `Agent[TContext]` is generic; `instructions` may be a function `(RunContextWrapper, Agent) -> str`.

**Key rule:** the context type must be the same across the agent, its tools and its guardrails in one run (the SDK does not check this at runtime; your type checker does). If you hand off between agents, they all share the same context object.

**Context is NOT conversation memory.** To give the LLM information, put it in the input, the instructions (dynamic instructions can read the context) or a tool result. The context is only for your code.

**Hindi नोट:** Interview में अक्सर पूछा जाता है "context और memory में फ़र्क?" Context = आपके Python code की dependencies (LLM नहीं देखता)। Memory/session = conversation history (LLM देखता है)। दोनों को मत मिलाओ।

---

## 🟡 Real World Example
**Tariff Agent.** Each API request carries a JWT. You build `RequestCtx(user_id, tenant, db_pool)` from it. The `get_duty` tool reads `ctx.context.db` to query that tenant's tariff table and appends to `ctx.context.audit`. The model only supplies `hs_code`; it can never choose which tenant's data is read.

**Customer Support Agent:** context holds the CRM client and ticket id, so `refund` tools act on the right ticket.

## 🟡 Real Example Hindi mein
**Tariff Agent.** हर API request में JWT आता है। उससे आप `RequestCtx(user_id, tenant, db_pool)` बनाते हैं। `get_duty` tool `ctx.context.db` से उस tenant की tariff table query करता है और `ctx.context.audit` में लिखता है। Model सिर्फ़ `hs_code` देता है; वह कभी तय नहीं कर सकता कि किस tenant का डेटा पढ़ा जाए।

**Customer Support Agent:** context में CRM client और ticket id रहता है, इसलिए `refund` tool सही ticket पर काम करता है।

---

## 💻 Code Example — Basic
Runs offline. The tool reads the user id from the context; we then print the tool's JSON-schema properties (empty = the model cannot see or set the context).

```python
# Basic: pass your own data (context) into a tool; the LLM never sees it (runs offline)
import asyncio                                           # run the async SDK
from dataclasses import dataclass                        # simple typed container for the context
from agents import Agent, Runner, RunContextWrapper, function_tool  # SDK pieces
from agents.testing import ScriptedModel, assistant_message, function_call  # offline fake LLM

@dataclass                                               # the context can be ANY Python object
class AppCtx:
    user_id: str                                         # who is calling (never sent to the model)
    plan: str                                            # e.g. "free" or "pro"

@function_tool                                           # turn the function into a tool
def my_plan(ctx: RunContextWrapper[AppCtx]) -> str:     # first param = context wrapper; it is hidden from the LLM schema
    """Return the plan of the current user."""           # docstring becomes the tool description
    return f"user={ctx.context.user_id} plan={ctx.context.plan}"  # read OUR data from ctx.context

async def main() -> None:
    model = ScriptedModel([                              # step 1: model asks for the tool; step 2: final text
        [function_call("my_plan", {}, call_id="c1")],    # tool call with no LLM-visible arguments
        [assistant_message("You are on the pro plan.")],
    ])
    agent = Agent[AppCtx](name="Tariff Agent", instructions="Help the user.",
                          model=model, tools=[my_plan])  # Agent[AppCtx] = typed context
    res = await Runner.run(agent, "What plan am I on?",  # run it
                           context=AppCtx(user_id="u-42", plan="pro"))  # context goes HERE, per run
    print("final:", res.final_output)                    # model's last message
    schema = model.calls[0].tools[0].params_json_schema  # what the LLM was shown for this tool
    print("tool schema properties:", schema["properties"])  # {} -> ctx is NOT in the schema
    print("context in model input?", "u-42" in str(model.calls[0].input))  # False before the tool ran

asyncio.run(main())                                      # entry point
```

## 💻 Code Example — Advanced
Per-request context in FastAPI: database handle, user, tenant, a counter and an audit list. Dynamic instructions are built from the context. Two requests from different tenants show the contexts do not leak. Offline, fake DB.

```python
# Advanced: per-request context in FastAPI (db handle + user + counters), dynamic instructions (offline)
import asyncio                                           # for the async DB stub
from dataclasses import dataclass, field                 # typed context with defaults
from fastapi import FastAPI, Header, HTTPException       # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # request schema
from agents import Agent, Runner, RunContextWrapper, function_tool, MaxTurnsExceeded  # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

class FakeDB:                                            # stand-in for an async DB pool
    rows = {"6109.10": 20, "6203.42": 12}                # HS code -> duty percent
    async def duty(self, code: str) -> int | None:       # async lookup
        await asyncio.sleep(0)                           # yield like real I/O
        return self.rows.get(code)

@dataclass
class RequestCtx:                                        # one instance PER REQUEST (never share between users)
    user_id: str
    tenant: str
    db: FakeDB                                           # handles are fine here; the model never sees them
    tool_calls: int = 0                                  # mutable counter the tools update
    audit: list[str] = field(default_factory=list)       # our own audit trail

@function_tool
async def get_duty(ctx: RunContextWrapper[RequestCtx], hs_code: str) -> str:  # hs_code is LLM-visible; ctx is not
    """Look up the import duty percent for an HS code."""
    ctx.context.tool_calls += 1                          # mutate shared run state
    pct = await ctx.context.db.duty(hs_code)             # use the db from context
    ctx.context.audit.append(f"{ctx.context.user_id}:{hs_code}")  # audit who asked what
    return "unknown code" if pct is None else f"{pct}%"  # tool result goes back to the LLM

def instructions(ctx: RunContextWrapper[RequestCtx], agent: Agent[RequestCtx]) -> str:  # dynamic system prompt
    return f"You are the Tariff Agent for tenant {ctx.context.tenant}. Be brief."  # built per run from context

def build_agent(model) -> Agent[RequestCtx]:             # factory keeps tests injectable
    return Agent[RequestCtx](name="Tariff Agent", instructions=instructions, model=model, tools=[get_duty])

app = FastAPI()                                          # the app

class Ask(BaseModel):
    question: str

@app.post("/ask")
async def ask(body: Ask, x_user: str = Header(...), x_tenant: str = Header("acme")) -> dict:
    model = ScriptedModel([[function_call("get_duty", {"hs_code": "6109.10"}, call_id="c1")],
                           [assistant_message("Duty is 20%.")]])  # production: a real model name instead
    ctx = RequestCtx(user_id=x_user, tenant=x_tenant, db=FakeDB())  # fresh context per request
    try:
        res = await Runner.run(build_agent(model), body.question, context=ctx, max_turns=4)  # pass context
    except MaxTurnsExceeded as exc:                      # agent looped too long
        raise HTTPException(status_code=504, detail="agent took too many turns") from exc
    except Exception as exc:                             # anything else becomes a clean 500
        raise HTTPException(status_code=500, detail=type(exc).__name__) from exc
    return {"answer": res.final_output, "tool_calls": ctx.tool_calls, "audit": ctx.audit,
            "system_prompt_seen": model.calls[0].system_instructions}  # proves dynamic instructions used ctx

if __name__ == "__main__":
    c = TestClient(app)                                  # no server needed
    print(c.post("/ask", json={"question": "Duty on 6109.10?"}, headers={"x-user": "u-1", "x-tenant": "acme"}).json())
    print(c.post("/ask", json={"question": "again"}, headers={"x-user": "u-2", "x-tenant": "globex"}).json())  # isolated ctx
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Run-scoped dependencies | State schema + `config['configurable']` (per-run config) | Task `context`/inputs dict; no typed DI | `context=` on `Runner.run`, typed `Agent[TContext]` | Tool closures / agent constructor args; no built-in run context |
| Visible to the LLM? | Only what you put in state/messages | Whatever is interpolated into prompts | Never (local only) | Only if you add it to messages |
| Typed? | TypedDict/pydantic state | Loosely typed | Generic `Agent[T]` + `RunContextWrapper[T]` | Python types per component |
| Reaches tools/guardrails/hooks | Via config/state in nodes | Via task context | Yes: tools, guardrails, hooks, dynamic instructions | Via closures |
| Shared across handoffs | Same graph state | Task outputs | Same context object | Per agent |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Storing the user id in a module-level global.
✅ Correct: Create a `RequestCtx` per request and pass `context=`; globals are shared across concurrent requests.

❌ Mistake 2: Putting secrets in the prompt so tools can use them.
✅ Correct: Keep secrets/handles in the context; the LLM never needs them.

❌ Mistake 3: Reusing one mutable context object for many requests.
✅ Correct: One context per run. Shared mutable state causes cross-user leaks and race conditions.

❌ Mistake 4: Expecting the LLM to read the context.
✅ Correct: It cannot. Pass facts via input, dynamic instructions or tool results.

❌ Mistake 5: Forgetting that the wrapper is the first parameter, not `ctx.user_id`.
✅ Correct: Use `ctx.context.user_id`: `ctx` is a `RunContextWrapper`, `ctx.context` is your object.

---

## 🧠 Tricky Interview Question
Your Tariff Agent serves many tenants from one process. A teammate stored `current_tenant` in a module-level variable that tools read. Occasionally one tenant sees another's duty data. Why, and how do you fix it using the SDK?

**Answer:** Async requests interleave on one event loop, so a global is overwritten by whichever request set it last; a tool call from request A can read the value written by request B. Fix: build a `RequestCtx(tenant=..., db=...)` per request and pass it via `Runner.run(..., context=ctx)`; tools read `ctx.context.tenant`. The context travels with the run (it is an argument, not ambient state), so interleaving cannot mix tenants. Also: construct per-tenant tools (for example `FileSearchTool` with that tenant's vector store) per request, never share a mutable context between requests, and add a test that fires two tenants concurrently with `asyncio.gather`.

---

## ⚫ Interview Questions + Answers

**Q1:** What is the context object in the OpenAI Agents SDK?

**A1:** Any Python object you pass as `context=` to `Runner.run`; it is injected into tools, guardrails, hooks and dynamic instructions. It is not sent to the LLM.

**Q2:** How does a tool receive it?

**A2:** Declare the first parameter as `ctx: RunContextWrapper[MyCtx]`. The SDK strips it from the tool's JSON schema (we verified `properties` is empty) and your object is at `ctx.context`.

**Q3:** Context vs session/memory?

**A3:** Context is local dependencies for your code. Session/memory is conversation history the LLM reads. Different purpose and lifetime.

**Q4:** How do you make the system prompt depend on the user?

**A4:** Pass a function as `instructions`: `(ctx: RunContextWrapper[T], agent) -> str`. It runs at each model call and can read `ctx.context`.

**Q5:** Design: multi-tenant agent API with per-tenant DB and audit.

**A5:** Build `RequestCtx` from the auth token (tenant, user, db pool handle, audit list). Pass it per run. Tools check authorization against `ctx.context`, never trust LLM-supplied ids for tenant or user. After the run, flush `ctx.audit` to a durable store. Cap `max_turns`, add timeouts, and test concurrent tenants for isolation.

---

## 💰 Cost Impact
The context itself adds zero tokens because it is never sent to the model. The cost lever is what your tools return: large tool results go back into the prompt. Formula: input_tokens per turn ~ system + history + tool_results. Keep tool results short and keep ids/handles in the context instead of repeating them in text. Token prices: approximate, from public pricing at time of writing, verify before budgeting.

---

## 🔷 When to Use
✅ Use when:
- Tools need DB pools, API clients, user/tenant identity
- Authorization must not depend on model-supplied ids
- You want typed, testable dependencies (inject fakes in tests)
- Collecting counters/audit data across a run

❌ Avoid when:
- Passing information the LLM needs to reason about (use input/instructions)
- Sharing one mutable context across concurrent requests
- Putting large conversation history here (use sessions)

---

## 📊 Visual Diagram
```
  HTTP request (JWT)
        |
        v
  RequestCtx(user, tenant, db, audit=[])      <- one per request
        |
        v
  Runner.run(agent, input, context=ctx)
        |
   +----+-----------------------+
   |    LLM loop                |
   |  prompt -> model -> tool call (hs_code only)
   |                |
   |                v
   |   tool(ctx: RunContextWrapper[RequestCtx], hs_code)
   |        uses ctx.context.db / .user   <- LLM never sees these
   +----------------------------+
        |
        v
  result + ctx.audit (you still hold ctx)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context object | Your own object passed to the run | आपका अपना object जो run को दिया जाता है |
| RunContextWrapper | SDK wrapper; your object is `.context` | SDK wrapper; आपका object `.context` में |
| Dependency injection | Supplying dependencies from outside | बाहर से dependencies देना |
| Dynamic instructions | Instructions built by a function each run | हर run में function से बने instructions |
| Tenant isolation | One customer cannot see another's data | एक customer दूसरे का डेटा नहीं देख सकता |

---

## ⚡ 3-Line Summary
English: The context is your own typed object passed with `context=` and delivered to tools, guardrails and hooks.
The LLM never sees it, so use it for identity, DB handles and counters.
Create one per request to keep tenants isolated.

Hindi: Context आपका अपना typed object है जो `context=` से जाता है और tools, guardrails, hooks तक पहुँचता है।
LLM इसे कभी नहीं देखता, इसलिए identity, DB handles और counters के लिए इस्तेमाल करें।
Tenants को अलग रखने के लिए हर request पर एक नया बनाएँ।

---

## ➡️ Next Topic
**#47 RunContext** - now a closer look at the `RunContextWrapper` itself: usage, turn input, `ToolContext` fields and how to read them in tools and hooks.

---
