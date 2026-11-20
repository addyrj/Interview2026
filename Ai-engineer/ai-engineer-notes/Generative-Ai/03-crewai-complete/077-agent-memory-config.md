---

# 77. Agent memory config
# हिंदी में: Agent का memory config
# Framework: CrewAI
# Already Known: No

> Verified against: `crewai` 1.15.41, `fastapi` 0.163.1, `pydantic` 2.12.5, Python 3.13 (installed in a scratch venv). Crews ran offline with a scripted fake LLM (`BaseLLM` subclass) and FastAPI `TestClient`. Real model calls: not run - needs an OpenAI-style API key, so real answers, token counts and latency are not shown.

---

## 🔵 Simple Definition (2-3 lines)
`memory` on an Agent (and on a Crew) turns on CrewAI's memory so agents can store and recall facts across tasks and runs. In 1.15.41 the field accepts `True` or a `Memory` object (unified memory with an embedder and scoring weights).

## 🔵 सरल परिभाषा (Hindi)
Agent (और Crew) पर `memory` चालू करने से CrewAI की memory सक्रिय होती है, जिससे agents tasks और runs के बीच facts store और recall कर सकते हैं। 1.15.41 में यह field `True` या `Memory` object (embedder और scoring weights वाली unified memory) लेता है।

---

## 🔴 Problem it Solves
LLMs are stateless: each run forgets earlier results, so users repeat context and agents re-do work. Memory stores useful facts (preferences, past lookups) and retrieves relevant ones into the prompt.

## 🔴 यह क्यों बना? (Hindi)
LLM stateless होते हैं: हर run पिछला भूल जाता है, इसलिए user को संदर्भ दोहराना पड़ता है और agent वही काम दोबारा करता है। Memory उपयोगी facts (preferences, पुराने lookups) store करती है और प्रासंगिक facts prompt में लाती है।

---

## 🟢 How it Works

```
Step 1 -> memory=True (or a Memory object) on Agent/Crew
Step 2 -> After tasks, facts are extracted and embedded into a store
Step 3 -> On later tasks, a query is embedded and similar memories are retrieved
Step 4 -> Retrieval blends similarity, recency and importance (Memory has recency_weight, semantic_weight, importance_weight fields)
Step 5 -> Retrieved snippets are injected into the prompt
Step 6 -> Extra LLM/embedding calls cost tokens
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Agent/Crew पर memory=True (या Memory object)
Step 2 -> Tasks के बाद facts निकालकर embed करके store में रखे जाते हैं
Step 3 -> बाद के tasks में query embed होती है और मिलती-जुलती memories आती हैं
Step 4 -> Retrieval similarity, recency और importance मिलाता है (Memory में recency_weight, semantic_weight, importance_weight fields हैं)
Step 5 -> मिले snippets prompt में जोड़े जाते हैं
Step 6 -> अतिरिक्त LLM/embedding calls के tokens लगते हैं
```

---

## 🟡 Real World Example
**Tariff Agent**: after answering 'duty for 8517 into India', memory stores it; next week a user asks a related question and the agent recalls the earlier finding instead of re-deriving it. Danger: stale rates - always store a date and re-verify volatile facts.

## 🟡 Real Example Hindi mein
**Tariff Agent**: 'India में 8517 की duty' का जवाब देने के बाद memory उसे store करती है; अगले हफ़्ते related सवाल आने पर agent पुराना finding याद कर लेता है, दोबारा नहीं निकालता। ख़तरा: पुराने rates - तारीख़ store करें और बदलने वाले facts दोबारा verify करें।

---

## 💻 Code Example — Basic
```python
# memory_basic.py - turning memory on (needs embeddings => needs an embedder/API key at real run time)
from crewai import Agent, Task, Crew, LLM            # core

llm = LLM(model="gpt-4o-mini")                       # chat model
agent = Agent(role="Analyst", goal="Remember past lookups", backstory="Organised.",
              llm=llm, memory=True)                  # agent-level memory (True = default Memory())
task = Task(description="Duty for HS {hs}?", expected_output="One line.", agent=agent)
crew = Crew(agents=[agent], tasks=[task], memory=True)   # crew-level memory shared by agents
crew.kickoff(inputs={"hs": "8517"})                  # run 1 stores facts
crew.kickoff(inputs={"hs": "8517"})                  # run 2 can recall run 1
```
Syntax-checked only (`ast.parse`) - NOT run: memory needs an embedder (for example an OpenAI embedding key) and a storage backend. We did confirm `Memory` is importable from `crewai.memory.unified_memory` and lists fields such as `embedder`, `recency_weight`, `semantic_weight`, `importance_weight`, `storage` in 1.15.41. Memory APIs are changing quickly - check the current docs.

## 💻 Code Example — Advanced
```python
# memory_api.py - explicit Memory object (custom embedder) shared by agent and crew
from crewai import Agent, Task, Crew, LLM            # core
from crewai.memory.unified_memory import Memory      # unified memory class (check fields in your version)
from fastapi import FastAPI, HTTPException           # web
from pydantic import BaseModel                       # schema

app = FastAPI()                                      # app
mem = Memory(embedder={"provider": "openai", "config": {"model_name": "text-embedding-3-small"}})   # one store per process

class Q(BaseModel):                                  # body
    hs: str                                          # HS code

@app.post("/lookup")                                 # endpoint
async def lookup(q: Q) -> dict[str, str]:            # typed
    agent = Agent(role="Analyst", goal="Reuse past answers", backstory="Organised.",
                  llm=LLM(model="gpt-4o-mini"), memory=mem)      # agent uses shared store
    task = Task(description="Duty for HS {hs}?", expected_output="One line.", agent=agent)
    try:
        out = await Crew(agents=[agent], tasks=[task], memory=mem).kickoff_async(inputs={"hs": q.hs})
    except Exception as exc:                         # embedder/LLM/storage failure
        raise HTTPException(502, type(exc).__name__) from exc
    return {"answer": out.raw}
```
Syntax-checked only - NOT run (needs embeddings credentials). The `embedder` dict shape (`provider` + `config.model_name`) is an assumption from CrewAI docs for earlier versions; verify it for your installed version before use. Design point: one shared `Memory` per process, but scope or namespace per tenant so users never recall each other's data.

Async: the advanced example uses `kickoff_async`, so the FastAPI event loop is never blocked. Error handling: every route wraps the crew in try/except and maps failures to an HTTP error. Token usage: `CrewOutput.token_usage` carries prompt/completion tokens (real numbers appear only with a real LLM; with the offline fake they are 0).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Short-term state | Graph state / checkpointer | Task context within a run | Session / run context | Message history |
| Long-term memory | Store (e.g. `BaseStore`) you wire up | `memory=` (embedder-backed) | Sessions + your own store | Memory interface / extensions |
| Needs embeddings | Only if you build semantic recall | Yes for semantic memory | Only if you add retrieval | Only if you add retrieval |
| Tenant isolation | You design namespaces | Scopes (`MemoryScope`) exist, verify usage | You design it | You design it |
| Maturity | Stable primitives | Evolving API | Evolving | Evolving |

LangGraph, OpenAI Agents SDK and AutoGen cells are summarised from general knowledge of those frameworks, not run in this note - verify against their current docs.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Turning memory on everywhere 'just in case'.
✅ Correct: Enable only where recall pays off; it adds embedding and LLM calls.

❌ Mistake 2: Sharing one memory across tenants.
✅ Correct: Scope memory per tenant/user and test isolation.

❌ Mistake 3: Trusting recalled facts blindly.
✅ Correct: Store timestamps and sources; re-verify volatile data and avoid storing secrets/PII.

---

## 🧠 Tricky Interview Question
Users complain the agent 'remembers' wrong or outdated duty rates. What is happening and how do you fix it?

Answer: Semantic memory returns similar items, not necessarily current ones; an old rate can outrank new data if it matches the query better. Fixes: store effective dates and sources, weight recency (the Memory object exposes `recency_weight`/`recency_half_life_days`), prefer tool lookups for volatile facts, expire or overwrite superseded entries, and add a guardrail that requires a fresh tool call for rates.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `memory=True` do?
A1: Enables CrewAI memory so the agent/crew can store and recall information across tasks and runs.

Q2: [Medium] What extra resources does memory need?
A2: An embedding model (and API key or local embedder) plus a storage backend; also extra LLM calls for extracting/consolidating facts.

Q3: [Hard] Memory vs context between tasks?
A3: Context passes specific task outputs within one run; memory persists and retrieves semantically across runs.

Q4: [Hard] How do you stop PII leaking via memory?
A4: Don't store PII, redact before storing, scope per tenant, set retention, encrypt storage, and test cross-tenant recall.

Q5: [System Design] Memory for a multi-tenant agent product?
A5: Per-tenant namespaces/scopes, central embedder service, TTL and deletion API (GDPR), store provenance, background consolidation, and evals measuring recall precision.

---

## 💰 Cost Impact
Formula: extra cost per run = embedding calls + memory-extraction LLM calls + injected memory tokens in each prompt. Injected snippets are resent every iteration, so 500 recalled tokens x 8 iterations = 4,000 input tokens (approximate example). Tips: limit retrieved items, enable only for agents that need it, use a cheap embedding model.
Numbers here are formulas and ranges only (approximate, from public pricing at time of writing - verify with your provider); no measured token counts are claimed.

---

## 🔷 When to Use
✅ Use when:
- Repeat users and long-running assistants
- Reusing verified findings across runs

❌ Avoid when:
- One-shot stateless jobs
- Regulated data without retention/deletion controls

---

## 📊 Visual Diagram
```
  task output --> extract facts --> embed --> [ MEMORY STORE ]
                                                    ^      |
   new task --> embed query --> similarity+recency --+      |
                                   |                        |
                                   v                        |
                     top-k memories injected into prompt <--+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memory | Persistent store of facts | स्मृति |
| Embedding | Vector representation of text | एम्बेडिंग |
| Recall | Retrieve relevant memories | याद करना |
| Scope | Namespace limiting visibility | दायरा |
| Recency | How recent a memory is | ताज़गी |
| TTL | Time before data expires | समाप्ति-समय |

---

## ⚡ 3-Line Summary
English: Memory lets agents recall facts across runs but needs an embedder and adds cost. Scope per tenant, store dates, and verify volatile facts with tools. Not run here - APIs need credentials and are evolving.
Hindi: Memory से agents runs के बीच facts याद रखते हैं, पर embedder चाहिए और cost बढ़ती है। Tenant के अनुसार scope करें, तारीख़ें रखें और बदलने वाले facts tools से verify करें। यहाँ run नहीं किया - credentials चाहिए और APIs बदल रही हैं।

---

## ➡️ Next Topic
**078. Agent max_iter** - the loop cap that protects your token budget.

---
