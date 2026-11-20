---

# 72. CrewAI vs LangGraph vs SDK
# हिंदी में: CrewAI बनाम LangGraph बनाम OpenAI SDK
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
Three popular ways to build agents: CrewAI (declare role-based agents and tasks), LangGraph (draw an explicit stateful graph) and the OpenAI Agents SDK (small agent loop with tools and handoffs). They solve overlapping problems at different levels of control.

## 🔵 सरल परिभाषा (Hindi)
Agents बनाने के तीन लोकप्रिय तरीक़े: CrewAI (role-based agents और tasks declare करो), LangGraph (साफ़ stateful graph बनाओ) और OpenAI Agents SDK (छोटा agent loop जिसमें tools और handoffs हों)। ये मिलती-जुलती समस्याएँ अलग-अलग स्तर के control पर हल करते हैं।

---

## 🔴 Problem it Solves
Picking the wrong framework costs weeks: too much control means boilerplate for a simple pipeline; too little means hacks when you need loops, human approval or resumable state.

## 🔴 यह क्यों बना? (Hindi)
ग़लत framework चुनने से हफ़्तों बर्बाद होते हैं: ज़्यादा control का मतलब साधारण pipeline के लिए boilerplate; कम control का मतलब loops, human approval या resumable state चाहिए तो hacks।

---

## 🟢 How it Works

```
Step 1 -> Write the workflow as a sentence (who does what in what order)
Step 2 -> Does it need cycles, branches, checkpoints, human-in-the-loop? -> LangGraph
Step 3 -> Is it a linear/role-based pipeline of 2-5 agents? -> CrewAI
Step 4 -> Is it one agent with tools and handoffs, all on OpenAI? -> OpenAI Agents SDK
Step 5 -> Prototype the smallest slice in the front-runner
Step 6 -> Measure cost, latency, debuggability, then commit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Workflow को एक वाक्य में लिखें (कौन क्या करता है किस क्रम में)
Step 2 -> Cycles, branches, checkpoints, human-in-the-loop चाहिए? -> LangGraph
Step 3 -> 2-5 agents की linear/role-based pipeline? -> CrewAI
Step 4 -> एक agent, tools और handoffs, सब OpenAI पर? -> OpenAI Agents SDK
Step 5 -> सबसे छोटा हिस्सा front-runner में prototype करें
Step 6 -> Cost, latency, debuggability नापें, फिर तय करें
```

---

## 🟡 Real World Example
**Tariff Agent**: 'find duty, verify, write brief' is a straight pipeline -> CrewAI is quick. 'Classify HS code, if confidence < 0.8 ask a human, retry, resume next day' needs checkpoints and a loop -> LangGraph. 'Chat assistant that hands off to a Billing agent' -> Agents SDK.

## 🟡 Real Example Hindi mein
**Tariff Agent**: 'duty निकालो, verify करो, brief लिखो' सीधी pipeline है -> CrewAI तेज़ है। 'HS code classify करो, confidence < 0.8 हो तो human से पूछो, retry, अगले दिन resume' के लिए checkpoints और loop चाहिए -> LangGraph। 'Chat assistant जो Billing agent को handoff करे' -> Agents SDK।

---

## 💻 Code Example — Basic
```python
# compare_basic.py - the same job in CrewAI: declare WHO + WHAT, framework decides HOW
from crewai import Agent, Task, Crew, LLM            # CrewAI core

llm = LLM(model="gpt-4o-mini")                       # real run needs OPENAI_API_KEY
checker = Agent(role="Duty Checker", goal="Verify a duty rate",
                backstory="Strict auditor.", llm=llm)   # persona-driven agent
lookup = Task(description="Look up duty for HS {hs}.", expected_output="Rate in percent.", agent=checker)
verify = Task(description="Double-check the rate found above.", expected_output="OK or corrected rate.",
              agent=checker, context=[lookup])       # explicit data flow between tasks
crew = Crew(agents=[checker], tasks=[lookup, verify])   # 2 tasks, default sequential
print(crew.kickoff(inputs={"hs": "6403"}).raw)       # LangGraph equivalent = 2 nodes + 1 edge + state schema
```
Verified: ran offline with a scripted fake LLM. The two-task crew with `context=[lookup]` is the CrewAI shape of what LangGraph would express as two nodes, one edge and a state schema (that LangGraph comparison is conceptual, not run here).

## 💻 Code Example — Advanced
```python
# compare_api.py - one endpoint, timing + token metadata so you can benchmark frameworks fairly
import time                                          # wall-clock timing
from crewai import Agent, Task, Crew, LLM            # CrewAI core
from fastapi import FastAPI, HTTPException           # web layer
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app
llm = LLM(model="gpt-4o-mini")                       # shared model

class Q(BaseModel):                                  # request
    hs: str                                          # HS code

@app.post("/bench")                                  # benchmark endpoint
async def bench(q: Q) -> dict[str, object]:          # typed
    agent = Agent(role="Analyst", goal="Answer duty questions", backstory="Expert.", llm=llm)
    task = Task(description="Duty for {hs}?", expected_output="One line.", agent=agent)
    crew = Crew(agents=[agent], tasks=[task])        # smallest crew
    start = time.perf_counter()                      # start timer
    try:
        out = await crew.kickoff_async(inputs={"hs": q.hs})   # async run
    except Exception as exc:                         # map failures to 502
        raise HTTPException(502, f"{type(exc).__name__}") from exc
    ms = round((time.perf_counter() - start) * 1000) # latency in ms (measure yourself, do not assume)
    return {"answer": out.raw, "latency_ms": ms, "prompt_tokens": out.token_usage.prompt_tokens,
            "completion_tokens": out.token_usage.completion_tokens}
```
Verified with FastAPI `TestClient` and the offline fake LLM. The endpoint returns latency and token fields so you can benchmark frameworks on the same prompt; the latency printed in our run (about 15 ms) came from the fake model and says nothing about real performance.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Mental model | Graph: nodes, edges, state | Team: roles, tasks, process | Agent loop + handoffs + guardrails | Conversation between agents |
| Cycles / branching | First-class | Limited (Flows add routing) | Via code / handoffs | Via team patterns |
| Persistence / resume | Checkpointers built in | Memory + checkpoint features (check docs) | Sessions / tracing | State save APIs |
| Human-in-the-loop | Interrupts built in | `human_input` on Task | Approvals via guardrails/hooks (check docs) | UserProxy agent |
| Model lock-in | Any LangChain model | Any (LiteLLM-style / native providers) | Optimised for OpenAI, others possible | Any |
| Setup effort for a 2-step pipeline | Medium | Low | Low | Medium |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Choosing by hype or GitHub stars.
✅ Correct: Choose by workflow shape: pipeline vs graph vs single agent with handoffs.

❌ Mistake 2: Rewriting a working CrewAI pipeline in LangGraph 'for scale'.
✅ Correct: Scale comes from stateless workers, queues and rate limits; switch only when you need cycles/checkpoints.

❌ Mistake 3: Comparing frameworks with different prompts and models.
✅ Correct: Fix model, prompt, tools and inputs, then compare cost, latency and failure rate yourself.

---

## 🧠 Tricky Interview Question
The CTO asks: 'Why not just use one framework for everything?'

Answer: You can, but fit matters. A single framework avoids a mixed stack, yet CrewAI's declarative style hides control flow you may later need (cycles, resumable state), while LangGraph's explicitness is boilerplate for a 2-step pipeline. A pragmatic answer: standardise on tools via MCP/OpenAPI so they are framework-neutral, pick LangGraph for stateful core flows, allow CrewAI for quick role-based pipelines, and review quarterly because all three change fast.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] One-line difference between CrewAI and LangGraph?
A1: CrewAI: declare agents/tasks and let the process run them. LangGraph: you draw the graph and own the state and control flow.

Q2: [Medium] When would you pick the OpenAI Agents SDK?
A2: One or a few agents with function tools, handoffs, guardrails and tracing, mostly on OpenAI models, with minimal framework overhead.

Q3: [Hard] How do you add human approval in CrewAI vs LangGraph?
A3: CrewAI: `human_input=True` on a Task prompts a human for feedback on that task. LangGraph: interrupt before/after a node with a checkpointer, resume later with the stored state. LangGraph is stronger for async approvals.

Q4: [Hard] Which is cheapest in tokens?
A4: None inherently. Cost depends on prompts, number of LLM calls and model. CrewAI hierarchical adds manager calls; LangGraph lets you skip LLM calls on deterministic nodes. Measure.

Q5: [System Design] Design a platform supporting all three frameworks.
A5: Shared tool layer (MCP/HTTP), common LLM gateway with rate limits and logging, a thin `run(workflow, input)` API, uniform tracing/IDs, per-framework adapters, and a benchmark harness using fixed prompts.

---

## 💰 Cost Impact
Formula: cost = LLM calls x (input tokens x input price + output tokens x output price). Frameworks change the number of calls (manager agents, retries, reflection loops), not the price per token. Prefer designs where deterministic steps are plain code, not LLM calls.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- You are choosing a framework for a new agent project
- You must justify the choice to a team or interviewer

❌ Avoid when:
- Framework is already fixed by the codebase and works
- You compare without running your own benchmark

---

## 📊 Visual Diagram
```
            Need cycles / checkpoints / resume?
                     /            \
                  yes              no
                   |                |
               LangGraph     Role-based pipeline of agents?
                                /            \
                             yes              no
                              |                |
                           CrewAI      One agent + tools + handoffs?
                                                 |
                                         OpenAI Agents SDK
                         (multi-agent chat -> AutoGen)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Graph | Nodes and edges describing control flow | ग्राफ़ |
| Handoff | One agent passes the conversation to another | हस्तांतरण |
| Checkpoint | Saved state to resume later | चेकपॉइंट |
| Process | CrewAI execution order | प्रक्रिया |
| Boilerplate | Repetitive setup code | बार-बार का कोड |
| Benchmark | Measured comparison on same inputs | तुलनात्मक माप |

---

## ⚡ 3-Line Summary
English: Pick by workflow shape: graph with state -> LangGraph, role pipeline -> CrewAI, single agent with handoffs -> OpenAI SDK. Costs depend on LLM call count, not the logo. Benchmark with your own prompts.
Hindi: Workflow के आकार से चुनें: state वाला graph -> LangGraph, role pipeline -> CrewAI, handoffs वाला single agent -> OpenAI SDK। Cost LLM calls की गिनती पर निर्भर है, logo पर नहीं। अपने prompts से benchmark करें।

---

## ➡️ Next Topic
**073. Agent - Complete Guide** - now that CrewAI is chosen, learn every important Agent parameter.

---
