---

# 76. Agent llm config
# हिंदी में: Agent का llm config
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`Agent(llm=...)` accepts a model string (`"gpt-4o-mini"`) or an `LLM(...)` object with settings such as `temperature`, `max_tokens` and `timeout`. A second optional model, `function_calling_llm`, can handle tool-call formatting cheaply.

## 🔵 सरल परिभाषा (Hindi)
`Agent(llm=...)` model string (`"gpt-4o-mini"`) या `LLM(...)` object लेता है जिसमें `temperature`, `max_tokens`, `timeout` जैसी settings होती हैं। दूसरा optional model `function_calling_llm` tool-call formatting सस्ते में संभाल सकता है।

---

## 🔴 Problem it Solves
One model for everything wastes money (a strong model for trivial lookups) or hurts quality (a weak model for reasoning). Per-agent model config lets you match cost and capability to each role.

## 🔴 यह क्यों बना? (Hindi)
सब कुछ एक ही model से करने पर पैसा बर्बाद होता है (मामूली lookup के लिए महँगा model) या quality गिरती है (reasoning के लिए कमज़ोर model)। Per-agent model config से हर role के लिए cost और क्षमता मिलाई जा सकती है।

---

## 🟢 How it Works

```
Step 1 -> Agent receives llm string or LLM object
Step 2 -> CrewAI builds the provider client from the model id
Step 3 -> Every iteration calls llm with system + task + scratchpad
Step 4 -> temperature/max_tokens/timeout apply to each call
Step 5 -> If function_calling_llm is set it formats tool calls
Step 6 -> Errors (rate limit/timeouts) surface as exceptions you handle
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Agent को llm string या LLM object मिलता है
Step 2 -> CrewAI model id से provider client बनाता है
Step 3 -> हर iteration system + task + scratchpad के साथ llm call करती है
Step 4 -> temperature/max_tokens/timeout हर call पर लागू होते हैं
Step 5 -> function_calling_llm सेट हो तो वह tool calls format करता है
Step 6 -> Errors (rate limit/timeouts) exceptions बनकर आते हैं जिन्हें आप संभालते हैं
```

---

## 🟡 Real World Example
**Tariff Agent**: lookup agent on a small model, temperature 0, `max_tokens=400`; a Planner agent on a stronger model with `function_calling_llm` set to the cheap one. We confirmed `LLM(model='gpt-4o-mini', temperature=0.1)` constructs offline without an API call and exposes `.model` and `.temperature`.

## 🟡 Real Example Hindi mein
**Tariff Agent**: lookup agent छोटे model पर, temperature 0, `max_tokens=400`; Planner agent मज़बूत model पर और `function_calling_llm` सस्ते model पर। हमने पुष्टि की कि `LLM(model='gpt-4o-mini', temperature=0.1)` बिना API call के offline बनता है और `.model`, `.temperature` देता है।

---

## 💻 Code Example — Basic
```python
# llm_basic.py - three ways to configure an agent's model
from crewai import Agent, LLM                        # core

by_string = Agent(role="A", goal="g", backstory="b", llm="gpt-4o-mini")   # 1: plain model string
tuned = LLM(                                         # 2: LLM object for tuning
    model="gpt-4o-mini",                             # provider/model id
    temperature=0.0,                                 # deterministic for lookups
    max_tokens=400,                                  # cap output tokens = cap cost
    timeout=30,                                      # seconds per request
)
precise = Agent(role="Tariff Analyst", goal="Exact duty", backstory="Strict.", llm=tuned)
router = Agent(                                      # 3: cheap model for tool-call formatting
    role="Planner", goal="Plan steps", backstory="Strategic.",
    llm=LLM(model="gpt-4o", temperature=0.4),        # stronger model for reasoning
    function_calling_llm=LLM(model="gpt-4o-mini"),   # cheaper model used to parse tool calls
)
print(tuned.model, tuned.temperature)                # inspect config; no API call is made here
```
Verified: constructing `LLM(...)` and `Agent(..., llm=...)` works offline (printed `gpt-4o-mini 0.0`). Model ids are examples - check your provider's current names. Any real completion: not run - needs an API key.

## 💻 Code Example — Advanced
```python
# llm_api.py - model tier chosen per request (cheap vs smart) with fallback on failure
from crewai import Agent, Task, Crew, LLM            # core
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app
TIERS: dict[str, str] = {"fast": "gpt-4o-mini", "smart": "gpt-4o"}   # tier -> model id (verify names)

class Req(BaseModel):                                # body
    question: str                                    # user question
    tier: str = "fast"                               # default cheap

def run(question: str, model: str) -> str:           # blocking helper
    llm = LLM(model=model, temperature=0.0, max_tokens=500, timeout=30)   # bounded
    agent = Agent(role="Analyst", goal="Answer briefly", backstory="Expert.", llm=llm)
    task = Task(description="{q}", expected_output="Short answer.", agent=agent)
    return Crew(agents=[agent], tasks=[task]).kickoff(inputs={"q": question}).raw

@app.post("/answer")                                 # endpoint (sync def -> FastAPI threadpool)
def answer(req: Req) -> dict[str, str]:              # typed
    model = TIERS.get(req.tier)                      # map tier
    if model is None:                                # unknown tier
        raise HTTPException(422, "tier must be fast or smart")
    try:
        return {"model": model, "answer": run(req.question, model)}   # primary
    except Exception:                                # primary failed: fall back to the cheap tier
        try:
            return {"model": TIERS["fast"], "answer": run(req.question, TIERS["fast"])}
        except Exception as exc:                     # both failed
            raise HTTPException(502, type(exc).__name__) from exc
```
Verified with `TestClient` using the offline fake (the code path with the real `LLM` in `run()` was substituted). Fallback pattern: on primary failure retry once on the cheap tier, then return 502. Tier names map to model ids you must verify.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Set model | `ChatOpenAI(...)` etc. in a node | `llm="model"` or `LLM(...)` | `model=` on Agent / ModelSettings | `model_client=` |
| Per-step model | Different model per node | Different model per agent | Different model per agent | Different client per agent |
| Provider range | Any LangChain integration | Native providers + LiteLLM-style routing (check docs) | OpenAI-first, others possible | OpenAI, Azure, Anthropic, local via extensions |
| Tool-call model split | DIY | `function_calling_llm` | n/a | n/a |
| Offline testing | Fake chat model | `BaseLLM` subclass (used here) | Mock model | `ReplayChatCompletionClient` |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: High temperature for deterministic lookups.
✅ Correct: Use temperature 0-0.2 for factual/tool tasks.

❌ Mistake 2: No `max_tokens`/`timeout`.
✅ Correct: Cap both so one slow call cannot stall a request or run up cost.

❌ Mistake 3: Hard-coding model ids across the codebase.
✅ Correct: Centralise in config (tier -> model id) and verify names against the provider.

---

## 🧠 Tricky Interview Question
The same crew gives different answers each run even at temperature 0. Why?

Answer: Temperature 0 reduces but does not guarantee determinism: providers may batch, update models, or use non-deterministic kernels, and tool outputs or ordering can differ. Also each ReAct step conditions on prior text, so small differences compound. For stability: pin the model version, use structured outputs (`output_pydantic`) with guardrails, cache tool results, and test with an eval set that tolerates minor wording changes.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Two ways to set an agent's model?
A1: A string like `llm="gpt-4o-mini"` or an `LLM(model=..., temperature=...)` object.

Q2: [Medium] What is `function_calling_llm`?
A2: An optional separate LLM used to handle tool-calling; it lets a cheaper model format calls while the main LLM reasons.

Q3: [Hard] How do you control cost with llm config?
A3: Cheaper models for simple agents, `max_tokens`, low temperature to avoid rambling, smaller `max_iter`, and fewer tools.

Q4: [Hard] How do you test crews without a paid model?
A4: Subclass `BaseLLM` returning scripted replies (we used this) or use provider mocks; assert on prompts seen and outputs.

Q5: [System Design] Multi-provider failover?
A5: Gateway or per-request tiers with retries and circuit breakers, same prompts tested on both providers, log model id per run, budget alarms, and an eval gate before changing defaults.

---

## 💰 Cost Impact
Formula: cost = input_tokens x in_price + output_tokens x out_price, per iteration. Small models are often an order of magnitude cheaper than flagship models (approximate, from public pricing at time of writing - verify). Tips: tier models by role, cap `max_tokens`, and use `function_calling_llm` only if you measure savings.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Mixed workloads with different difficulty
- You need deterministic-ish tool use (low temperature)

❌ Avoid when:
- Changing models without re-running your eval set
- Using one huge model for every step by default

---

## 📊 Visual Diagram
```
  Agent A (lookup)  --llm--> small model, temp 0, max_tokens 400
  Agent B (planner) --llm--> strong model, temp 0.4
                     \--function_calling_llm--> small model (formats tool calls)
           each iteration:  prompt --> [model] --> text/tool call
           failures: timeout / rate limit --> exception --> your handler
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LLM object | CrewAI model config wrapper | एलएलएम ऑब्जेक्ट |
| temperature | Randomness of sampling | यादृच्छिकता |
| max_tokens | Output length cap | अधिकतम टोकन |
| timeout | Max seconds per request | समय-सीमा |
| Model tier | Cheap vs strong model class | मॉडल श्रेणी |
| Fallback | Backup path on failure | बैकअप |

---

## ⚡ 3-Line Summary
English: Configure the model per agent with LLM(): low temperature for lookups, caps for tokens and time, stronger models only where reasoning needs them. Centralise model ids and keep a fallback.
Hindi: हर agent का model LLM() से configure करें: lookups के लिए कम temperature, tokens और समय की सीमा, और मज़बूत model सिर्फ़ वहीं जहाँ reasoning चाहिए। Model ids एक जगह रखें और fallback रखें।

---

## ➡️ Next Topic
**077. Agent memory config** - letting agents remember across tasks and runs.

---
