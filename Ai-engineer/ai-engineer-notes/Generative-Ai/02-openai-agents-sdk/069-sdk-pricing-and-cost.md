---

# 69. SDK Pricing + Cost
# हिंदी में: SDK की Pricing और Cost
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57). IMPORTANT: every token count printed here (10 in / 5 out per call) comes from the fake model, and every price in the code (`1.00` and `4.00` USD per 1M tokens) is a PLACEHOLDER, not a real price list. No real model call was made (needs OPENAI_API_KEY). Look up current prices on the provider pricing page before computing anything real.

---

## 🔵 Simple Definition (2-3 lines)
The SDK itself is free open-source software; you pay the model provider per token (and for any hosted tools you use). Each run reports a `Usage` object with requests, input tokens and output tokens summed over all LLM calls, so cost = `input_tokens x input_price + output_tokens x output_price`.

## 🔵 सरल परिभाषा (Hindi)
SDK खुद मुफ़्त open-source है; आप model provider को प्रति token (और इस्तेमाल किए गए hosted tools के लिए) भुगतान करते हैं। हर run एक `Usage` object देता है जिसमें सभी LLM calls का requests, input tokens और output tokens जुड़ा होता है, इसलिए cost = `input_tokens x input_price + output_tokens x output_price`।

---

## 🔴 Problem it Solves
Agents are loops: each tool call is another LLM turn that re-sends the whole history, so cost grows faster than people expect and varies per request. Without measurement and a budget, one runaway conversation or one abusive user can burn a day's budget, and finance cannot attribute spend to a team or tenant.

## 🔴 यह क्यों बना? (Hindi)
Agents loops होते हैं: हर tool call एक और LLM turn है जो पूरा history दोबारा भेजता है, इसलिए cost उम्मीद से तेज़ बढ़ती है और हर request में अलग होती है। मापन और budget के बिना, एक बेकाबू बातचीत या एक दुरुपयोग करने वाला user दिन भर का budget जला सकता है और finance खर्च को किसी team या tenant से जोड़ नहीं पाता।

---

## 🟢 How it Works

```
Step 1 -> Runner.run(...) makes N LLM calls (N = 1 + number of tool/handoff turns)
Step 2 -> after each call the SDK adds that call's usage to a running Usage
Step 3 -> result.context_wrapper.usage = Usage(requests, input_tokens,
                                              output_tokens, total_tokens,
                                              request_usage_entries=[per call])
Step 4 -> you convert tokens -> money with YOUR price table (one function)
Step 5 -> enforce: a hook compares spend with a per-request budget -> raise -> HTTP 402

Cost of one run (formula):
  sum over calls i of  ( in_i x P_in + out_i x P_out )
  in_i grows each turn because history (system + messages + tool results) is re-sent
  cached input tokens (if the provider supports it) are billed at a lower rate - check docs
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Runner.run(...) N LLM calls करता है (N = 1 + tool/handoff turns)
Step 2 -> हर call के बाद SDK उसकी usage चल रहे Usage में जोड़ता है
Step 3 -> result.context_wrapper.usage = Usage(requests, input_tokens,
                                              output_tokens, total_tokens,
                                              request_usage_entries=[हर call का])
Step 4 -> tokens को पैसे में आप अपनी price table से बदलते हैं (एक function)
Step 5 -> लागू करें: hook खर्च की तुलना per-request budget से करता है -> raise -> HTTP 402

एक run की cost (सूत्र):
  सभी calls i का योग ( in_i x P_in + out_i x P_out )
  in_i हर turn बढ़ता है क्योंकि history (system + messages + tool results) दोबारा भेजा जाता है
  cached input tokens (अगर provider सपोर्ट करे) सस्ते दर पर बिल होते हैं - docs देखें
```

**Verified output (basic sample, fake model):**
```
requests: 2 in: 20 out: 10 total: 30
  call 1: in=10 out=5
  call 2: in=10 out=5
estimated cost (placeholder prices): $0.00006000
```
Real runs differ: `in` increases on the second call because it contains the first call's tool result. Here the fake reports a constant 10, so do not infer growth from this output.

Advanced sample output: `{'answer': '20%', 'tokens': 30, 'est_usd': 6e-05}` for the normal request and `402 {'detail': 'budget exceeded: spent 0.00003000 > 1e-07'}` for a tiny budget (the run was aborted after the first LLM call because the hook raised in `on_llm_end`).

**Hindi नोट:** Hook `on_llm_end` में budget जाँचने का मतलब है कि run पहली ही call के बाद रुक सकता है; पर जो call हो चुकी, उसका पैसा लग चुका। इसलिए budget के साथ `max_turns`, input length limit और सस्ता model भी रखें। Prices को code में hard-code न करें; config/DB से पढ़ें क्योंकि वे बदलती रहती हैं।

---

## 🟡 Real World Example
**Tariff Agent.** A request costs one LLM call to decide on `get_tariff_rate`, then a second to write the answer. The API returns `tokens` and `est_usd` per request, logs them with tenant id, and rejects with HTTP 402 when a request exceeds its budget. Finance gets a daily report of cost per tenant and per agent.

**Customer Support Agent:** long chats get expensive because each turn re-sends the history; a summary of older turns replaces raw history after 10 messages.

## 🟡 Real Example Hindi mein
**Tariff Agent.** एक request में `get_tariff_rate` चुनने के लिए एक LLM call और जवाब लिखने के लिए दूसरी call लगती है। API हर request पर `tokens` और `est_usd` लौटाती है, tenant id के साथ log करती है, और budget से ऊपर जाने पर HTTP 402 से reject करती है। Finance को हर दिन tenant और agent के हिसाब से cost report मिलती है।

**Customer Support Agent:** लंबी chats महँगी हो जाती हैं क्योंकि हर turn history दोबारा भेजता है; 10 संदेशों के बाद पुराने turns का सारांश raw history की जगह ले लेता है।

---

## 💻 Code Example — Basic
Read usage and estimate cost (placeholder prices).

```python
# Basic: read token usage from a run and turn it into a cost estimate (offline; prices are PLACEHOLDERS).
# verified against openai-agents 0.24.0
import asyncio                                                    # run the async Runner
from agents import Agent, Runner, function_tool, set_tracing_disabled   # SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline scripted model (see note 57)

set_tracing_disabled(True)                                        # no trace upload offline

PRICE_IN_PER_M = 1.00                                             # USD per 1M input tokens - PLACEHOLDER, read your real price list
PRICE_OUT_PER_M = 4.00                                            # USD per 1M output tokens - PLACEHOLDER

@function_tool
def get_tariff_rate(hs_code: str) -> str:                         # one tool => the run needs 2 LLM calls
    """Duty percent for an HS code."""
    return "20%"

async def main() -> None:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text("Duty is 20%")]])
    agent = Agent(name="Tariff", instructions="x", tools=[get_tariff_rate], model=m)
    res = await Runner.run(agent, "rate?")
    u = res.context_wrapper.usage                                 # Usage summed over ALL llm calls of this run
    print("requests:", u.requests, "in:", u.input_tokens, "out:", u.output_tokens, "total:", u.total_tokens)
    for i, e in enumerate(u.request_usage_entries, 1):            # per-call breakdown (input grows each turn in real runs)
        print(f"  call {i}: in={e.input_tokens} out={e.output_tokens}")
    cost = u.input_tokens / 1e6 * PRICE_IN_PER_M + u.output_tokens / 1e6 * PRICE_OUT_PER_M
    print(f"estimated cost (placeholder prices): ${cost:.8f}")    # formula only; the token counts here are the fake model's

asyncio.run(main())
```

## 💻 Code Example — Advanced
FastAPI cost meter and budget guard using `RunHooks`.

```python
# Advanced: per-request cost meter + budget guard behind FastAPI, using RunHooks and Usage.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
from dataclasses import dataclass                                 # request context
from typing import Any                                            # type hints
from fastapi import FastAPI, HTTPException                        # web layer
from pydantic import BaseModel                                    # schemas
from agents import (Agent, RunContextWrapper, RunHooks, Runner, Usage, function_tool,
                    set_tracing_disabled)                         # SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline model

set_tracing_disabled(True)

PRICES = {"small-model": (1.00, 4.00)}                            # (in, out) USD per 1M tokens - PLACEHOLDERS, load from config in prod

def cost_usd(u: Usage, model: str) -> float:                      # one place that turns tokens into money
    p_in, p_out = PRICES[model]
    return u.input_tokens / 1e6 * p_in + u.output_tokens / 1e6 * p_out

class BudgetExceeded(Exception):                                  # our own signal, not an SDK error
    pass

@dataclass
class Ctx:
    model: str
    max_usd: float                                                # per-request budget

class BudgetHooks(RunHooks[Ctx]):
    async def on_llm_end(self, context: RunContextWrapper[Ctx], agent: Agent[Ctx], response: Any) -> None:
        spent = cost_usd(context.usage, context.context.model)    # usage so far in THIS run
        if spent > context.context.max_usd:                       # raising inside a hook aborts the run
            raise BudgetExceeded(f"spent {spent:.8f} > {context.context.max_usd}")

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    return "20%"

class Q(BaseModel):
    question: str
    max_usd: float = 0.01

app = FastAPI()

@app.post("/ask")
async def ask(q: Q) -> dict[str, Any]:
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"1"}')], [text("20%")]])   # offline script
    agent = Agent[Ctx](name="Tariff", instructions="x", tools=[get_tariff_rate], model=m)
    ctx = Ctx(model="small-model", max_usd=q.max_usd)
    try:
        res = await Runner.run(agent, q.question, context=ctx, hooks=BudgetHooks(), max_turns=5)
    except BudgetExceeded as e:
        raise HTTPException(402, f"budget exceeded: {e}")         # map to a clear client error
    u = res.context_wrapper.usage
    return {"answer": res.final_output, "tokens": u.total_tokens, "est_usd": round(cost_usd(u, ctx.model), 8)}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    c = TestClient(app)
    print(c.post("/ask", json={"question": "rate?"}).json())
    r = c.post("/ask", json={"question": "rate?", "max_usd": 0.0000001}); print(r.status_code, r.json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Framework price | Free (OSS); LangSmith/Platform optional paid | Free (OSS); enterprise paid | Free (OSS) | Free (OSS) |
| Token usage in result | Via callbacks / message metadata | `crew.usage_metrics` | `result.context_wrapper.usage` (+ per-call entries) | Model client usage |
| Budget enforcement | Your callback / node | Your code | Hook raising (this note) | Termination conditions + your code |
| Model choice | Any LangChain model | Any via LiteLLM-style config | Default OpenAI; others via adapters | Any model client |

_OpenAI SDK column verified in openai-agents 0.24.0; other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: Estimating cost as `questions x one call`.
✅ Correct: Count turns (tool calls and handoffs each add an LLM call) and growing history.

❌ Mistake 2: Hard-coding prices in business logic.
✅ Correct: One config table keyed by model name; update when pricing changes; log the model used.

❌ Mistake 3: Only a budget guard, no `max_turns` or input size limit.
✅ Correct: Layer limits: input `max_length`, `max_turns`, per-request budget, per-tenant daily budget.

❌ Mistake 4: Ignoring non-token costs.
✅ Correct: Hosted tools (search, code execution), storage, trace/eval platforms and egress can be billed separately - read each price page.

---

## 🧠 Tricky Interview Question
Cost per conversation doubled after you added "just one more tool" and did not change traffic. Why?

**Answer:** Three compounding effects: (1) the tool's schema is added to every request's input (more tools = bigger prompt on each call), (2) each use of the tool adds an LLM turn, and (3) its result is appended to history and re-sent on all later turns, so a large result is paid for many times. Diagnose with `request_usage_entries` and hook logs: compare input tokens per call before and after. Fixes: truncate or summarise tool output, narrow the tool's description and parameters, enable the tool only when needed (`is_enabled`), use prompt caching where available for the stable prefix, and route the tool decision to a cheaper model.

---

## ⚫ Interview Questions + Answers

**Q1:** Is the OpenAI Agents SDK paid?

**A1:** The library is open source and free; you pay for model tokens and any hosted tools you use.

**Q2:** Where do you read token usage?

**A2:** `result.context_wrapper.usage` (totals) and `usage.request_usage_entries` (per LLM call); inside hooks, `context.usage`.

**Q3:** Why does cost grow superlinearly with turns?

**A3:** Each turn re-sends the entire history, so input tokens sum roughly quadratically with the number of turns when results are large.

**Q4:** How do you cap spend per request?

**A4:** `max_turns`, input length limits, and a hook that raises when estimated spend passes a budget.

**Q5:** System design: per-tenant metering and billing.

**A5:** Put tenant id in context; hooks emit `{tenant, model, in, out}` events to a queue; a consumer prices them from a versioned price table and aggregates per day; enforce soft limits (alert) and hard limits (HTTP 402/429) via Redis counters; reconcile with the provider invoice monthly.

---

## 💰 Cost Impact
Formula only (no measured numbers): `run_cost = sum(in_i x P_in + out_i x P_out)`. A tool-using run needs at least 2 LLM calls; each extra tool turn re-sends history. Typical levers, in order of impact: smaller/cheaper model for routing and simple steps, fewer turns (better tool descriptions, parallel tool calls), shorter tool outputs, trimmed or summarised history, prompt caching of the stable prefix, strict output formats (shorter outputs), and batch/offline endpoints for non-interactive jobs where available. Prices change; approximate, from public pricing at time of writing - verify.

---

## 🔷 When to Use
✅ Use when:
- Any production agent (meter every run)
- Multi-tenant products that bill or limit usage
- Cost regressions after prompt/tool changes need detection

❌ Avoid when:
- Treating the estimate as the invoice (reconcile with the provider)
- Relying on a budget hook as the only protection
- Using placeholder prices in real dashboards

---

## 📊 Visual Diagram
```
 Runner.run
   |
   +-- LLM call 1: in=sys+user          out=tool_call      \
   +-- tool runs                                            |  usage += each call
   +-- LLM call 2: in=sys+user+call+result  out=answer      /
   v
 result.context_wrapper.usage = {requests, input, output, total, entries[]}
   |
   +--> cost_usd(usage, model) = in*P_in + out*P_out
   +--> BudgetHooks.on_llm_end: spent > max_usd ? raise -> HTTP 402
   +--> log {tenant, model, tokens, est_usd} -> billing queue
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Usage | Token and request counters of a run | run के token और request counters |
| Input / output tokens | Billed separately | अलग-अलग बिल होते हैं |
| Budget guard | Stops a run over a spend limit | खर्च सीमा पर run रोकता है |
| Prompt caching | Cheaper repeated prefix | दोहराए prefix का सस्ता दर |
| Metering | Measuring usage per tenant | tenant के हिसाब से उपयोग मापना |
| max_turns | Cap on LLM turns | LLM turns की सीमा |

---

## ⚡ 3-Line Summary
English: The SDK is free; tokens cost money and each tool turn re-sends history.
Read result.context_wrapper.usage, convert with a configurable price table and enforce budgets in hooks.
Combine budget, max_turns and input limits instead of relying on one guard.

Hindi: SDK मुफ़्त है; tokens पर पैसा लगता है और हर tool turn history दोबारा भेजता है।
result.context_wrapper.usage पढ़ें, configurable price table से बदलें और hooks में budgets लागू करें।
एक guard पर निर्भर रहने की बजाय budget, max_turns और input limits साथ रखें।

---

## ➡️ Next Topic
**#70 SDK Best Practices** - a checklist that ties tools, guardrails, limits, logging and tests into one production-ready service.

---
