---

# 92. Crew memory
# हिंदी में: Crew memory (agents को पिछली बातें याद रखना)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (venv, offline). I created a `Memory` object with a fake LLM, a fake embedding function and local storage, called `remember`/`recall`, and passed it into a `Crew`. Real extraction quality with a real LLM and real embeddings: not run - needs an API key and an embedding provider.

## 🔵 Simple Definition (2-3 lines)
Crew memory lets a crew store facts from its runs and recall them later. In 1.15.41 it is a single `Memory` class (`from crewai import Memory`) with `remember()` and `recall()`, scopes like `/tariff`, categories and importance.
You enable it with `Crew(memory=True)` or pass your own `Memory(...)`.

## 🔵 सरल परिभाषा (Hindi)
Crew memory से crew अपने runs की बातें store करता है और बाद में recall करता है। 1.15.41 में यह एक ही `Memory` class है (`from crewai import Memory`) जिसमें `remember()` और `recall()`, scopes जैसे `/tariff`, categories और importance होते हैं।
इसे `Crew(memory=True)` से या अपना `Memory(...)` देकर चालू करते हैं।

---

## 🔴 Problem it Solves
By default every `kickoff()` starts from zero. The agent forgets that this customer ships flat-rolled steel, or that last week's HS code was corrected. Putting all history in the prompt wastes tokens. Memory stores facts once and recalls only the relevant ones.

## 🔴 यह क्यों बना? (Hindi)
Default में हर `kickoff()` शून्य से शुरू होता है। Agent भूल जाता है कि यह customer flat-rolled steel भेजता है या पिछले हफ्ते का HS code सुधारा गया था। पूरा history prompt में डालना tokens बर्बाद करता है। Memory तथ्य एक बार रखती है और सिर्फ प्रासंगिक वाले वापस लाती है।

---

## 🟢 How it Works

```
Step 1 -> Before a task: crew recalls relevant memories (semantic search)
Step 2 -> Prompt gets a block "# Memories from past conversations ..."
Step 3 -> Agent answers the task
Step 4 -> After the run: new facts are extracted (needs an LLM) and saved
Step 5 -> Saved in a storage backend (default LanceDB) with embeddings
Step 6 -> Next run recalls them by similarity + recency + importance
```

`Memory` fields I read from the installed class: `llm` (for analysis), `storage` (backend or path), `embedder` (callable, config dict, or None = default OpenAI), `recency_weight` 0.3, `semantic_weight` 0.5, `importance_weight` 0.2, `recency_half_life_days` 30, `consolidation_threshold` 0.85, `read_only`, `root_scope`.
Methods: `remember`, `remember_many`, `recall(query, scope, categories, limit, depth='shallow'|'deep')`, `forget`, `update`, `list_scopes`, `list_records`, `scope(path)`, `slice`, `reset`, `drain_writes`.

What I ran:
- `Memory(llm=fake, storage="memdb/store", embedder=embed_fn)` where `embed_fn(list[str]) -> list[list[float]]`. `remember("Steel HS 7208 ...", scope="/tariff", categories=["duty"], importance=0.8)` returned a `MemoryRecord`; `recall("steel duty", scope="/tariff", depth="shallow")` returned it with a score; `list_scopes()` returned `['/tariff']`.
- `Crew(memory=mem)` ran; the task prompt the LLM received contained a "# Memories from past conversations" block with my stored fact.
- My fake LLM returned the wrong JSON schema for save-time analysis, and CrewAI logged "Memory save analysis failed, using defaults" and carried on. So a bad analysis LLM degrades memory quietly instead of crashing - monitor this log line.
- `Crew(memory=True)` with no key would try default OpenAI embeddings, so I did not run it.

## 🟢 कैसे काम करता है? (Hindi)
1. Task से पहले crew प्रासंगिक memories ढूँढता है (semantic search)।
2. Prompt में "# Memories from past conversations" वाला हिस्सा जुड़ता है (मैंने prompt में देखा)।
3. Agent जवाब देता है।
4. Run के बाद नए तथ्य निकालकर (LLM से) save होते हैं।
5. Storage backend (default LanceDB) में embeddings के साथ रखे जाते हैं।
6. अगले run में similarity, recency और importance के score से वापस आते हैं।
7. Analysis वाला LLM गलत format दे तो CrewAI चुपचाप defaults लेकर आगे बढ़ता है - इस log line पर नज़र रखें।

---

## 🟡 Real World Example
Tariff Agent for a trading company: memory scope `/customer/acme` holds "Acme imports flat-rolled steel (HS 7208) from Germany" and "Acme was told in May that licence X is required". Tomorrow's question "what is the duty for our usual product?" recalls these facts without re-sending history.

## 🟡 Real Example Hindi mein
किसी trading company के लिए Tariff Agent: scope `/customer/acme` में "Acme जर्मनी से flat-rolled steel (HS 7208) मँगवाता है" और "Acme को मई में बताया गया था कि licence X चाहिए" रखा है। कल "हमारे usual product की duty क्या है?" पूछने पर ये तथ्य बिना पूरा history भेजे वापस आ जाते हैं।

---

## 💻 Code Example — Basic
```python
# basic_crew_memory.py  (verified offline with a fake LLM + fake embedder, crewai 1.15.41)
import hashlib  # to build a deterministic fake embedding
from crewai import Agent, Task, Crew, Memory  # core classes

LLM_NAME = "gpt-4o-mini"  # model string; real run needs OPENAI_API_KEY


def embed(texts: list[str]) -> list[list[float]]:  # embedding callable: texts -> vectors
    # FAKE embedder for offline tests ONLY; use a real embedding model in production
    return [[b / 255 for b in hashlib.sha256(t.lower().encode()).digest()[:16]] for t in texts]


memory = Memory(  # unified memory object
    llm=LLM_NAME,  # LLM used to analyse/extract memories on save
    storage="memdb/store",  # local path for the default LanceDB-style backend
    embedder=embed,  # callable or provider config dict; None means default OpenAI
)

memory.remember(  # store one fact manually
    "Acme imports flat-rolled steel (HS 7208) from Germany",  # the fact
    scope="/customer/acme",  # hierarchical namespace
    categories=["profile"],  # labels
    importance=0.9,  # 0..1, higher survives recall ranking
)

hits = memory.recall("what does Acme import", scope="/customer/acme", limit=3, depth="shallow")  # search
for h in hits:  # MemoryMatch objects
    print(round(h.score, 3), h.record.content)  # score and text

agent = Agent(role="Tariff Analyst", goal="Answer duty questions", backstory="Broker.",  # agent
              llm=LLM_NAME, allow_delegation=False)  # no delegation
task = Task(description="Duty for Acme's usual product?", expected_output="Rate.", agent=agent)  # task
crew = Crew(agents=[agent], tasks=[task], memory=memory)  # crew uses this memory

if __name__ == "__main__":  # script entry
    print(crew.kickoff().raw)  # recalled facts are injected into the prompt
```

## 💻 Code Example — Advanced
```python
# advanced_crew_memory.py  (FastAPI + async + per-tenant scope + error handling)
from __future__ import annotations  # modern annotations

import hashlib  # fake embedder for offline use
import re  # sanitise tenant id

from fastapi import FastAPI, HTTPException  # web layer
from pydantic import BaseModel, Field  # schemas
from crewai import Agent, Task, Crew, Memory  # CrewAI

LLM_NAME = "gpt-4o-mini"  # replace with your model
app = FastAPI(title="Tariff API with memory")  # ASGI app


def embed(texts: list[str]) -> list[list[float]]:  # OFFLINE fake; swap for a real embedder
    return [[b / 255 for b in hashlib.sha256(t.lower().encode()).digest()[:16]] for t in texts]


SHARED_MEMORY = Memory(llm=LLM_NAME, storage="memdb/api", embedder=embed)  # one store for the app


class Ask(BaseModel):  # request
    tenant: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{2,32}$")  # tenant id, validated
    question: str = Field(..., min_length=3, max_length=400)  # question


class Fact(BaseModel):  # fact to store
    tenant: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{2,32}$")  # tenant id
    text: str = Field(..., min_length=3, max_length=400)  # the fact


class Answer(BaseModel):  # response
    answer: str  # final text
    recalled: list[str]  # memories we found for this tenant
    total_tokens: int  # usage


def scope_for(tenant: str) -> str:  # tenant isolation via scope path
    return "/tenant/" + re.sub(r"[^a-zA-Z0-9_-]", "", tenant)  # safe scope string


@app.post("/facts")  # store a fact
async def add_fact(f: Fact) -> dict[str, str]:  # async route
    try:
        rec = SHARED_MEMORY.remember(f.text, scope=scope_for(f.tenant), importance=0.7)  # write
    except Exception as exc:  # storage or embedding failure
        raise HTTPException(503, f"memory unavailable: {exc}") from exc  # service unavailable
    return {"id": rec.id if rec else "skipped"}  # return record id


@app.post("/ask", response_model=Answer)  # ask with memory
async def ask(q: Ask) -> Answer:  # async route
    scope = scope_for(q.tenant)  # tenant scope
    try:
        hits = SHARED_MEMORY.recall(q.question, scope=scope, limit=3, depth="shallow")  # tenant-only recall
        agent = Agent(role="Tariff Analyst", goal="Answer using known facts", backstory="Broker.",  # agent
                      llm=LLM_NAME, allow_delegation=False, max_iter=4)  # capped
        task = Task(description="{question}", expected_output="Short answer.", agent=agent)  # task
        crew = Crew(agents=[agent], tasks=[task], memory=SHARED_MEMORY.scope(scope))  # scoped memory view
        out = await crew.akickoff(inputs={"question": q.question})  # async run
    except Exception as exc:  # any failure
        raise HTTPException(502, f"crew failed: {exc}") from exc  # bad gateway
    return Answer(answer=out.raw, recalled=[h.record.content for h in hits],  # reply
                  total_tokens=out.token_usage.total_tokens)  # usage
```
Not run with a real model or real embeddings. Offline note: I verified `Memory`, `remember`, `recall`, `list_scopes` and `Crew(memory=Memory)` directly; the advanced code (including the `Memory.scope(path)` view passed into `Crew(memory=...)`) also ran through FastAPI `TestClient` with fakes and returned 200 (the `recalled` list was empty because nothing had been stored first).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Short-term (one run) | State / messages | Task context | Conversation items / session | Chat history |
| Long-term store | `Store` / checkpointer | `Memory` (LanceDB default) | Sessions; or your own store | Memory interface (`autogen_core.memory`) |
| Semantic recall | Store with embeddings | Built in (semantic + recency + importance) | Roll your own / vector tool | Memory implementations |
| Scoping | Namespaces | Scopes (`/tenant/x`) | Your design | Your design |

---

## ⚠️ Common Mistakes
❌ Mistake 1: `Crew(memory=True)` in production without deciding storage and embedder; it silently needs the default OpenAI embeddings.
✅ Correct: Create `Memory(llm=..., storage=..., embedder=...)` explicitly.

❌ Mistake 2: One global scope for all customers; recalled facts leak between tenants.
✅ Correct: Scope per tenant (`/tenant/<id>`) and also validate the id.

❌ Mistake 3: Never watching the "Memory save analysis failed" log, so nothing useful is saved.
✅ Correct: Alert on it and test your analysis LLM output.

---

## 🧠 Tricky Interview Question
After enabling memory the agent started giving an old, wrong HS code. How do you debug and fix it?

Answer: Memory recalled a stale fact. Inspect with `recall(...)` and `list_records(scope)`, find the wrong record, then `update()` or `forget()` it. Lower reliance on old items via recency weight/half-life, mark corrections with higher importance, store the source and date in metadata, and make the task's `expected_output` require the agent to check the current tariff tool and prefer it over memory. Memory is a hint, not ground truth.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you turn memory on?
A1: `Crew(memory=True)` or pass a `Memory(...)` instance.

Q2: [Medium] What does recall score depend on?
A2: Semantic similarity, recency and importance, with weights 0.5/0.3/0.2 by default.

Q3: [Hard] What LLM calls does memory make?
A3: Analysis/extraction on save (scope, categories, importance) and optional deep-recall exploration, so memory adds tokens beyond the tasks.

Q4: [Hard] How do you isolate tenants?
A4: Scopes (`/tenant/<id>`), plus `root_scope`, `private` records and `read_only` where needed; validate ids.

Q5: [System Design] Memory for 10,000 customers.
A5: Shared vector store (not local disk) with per-tenant scope, async writes (`drain_writes` on shutdown), TTL/cleanup, PII redaction before saving, evaluation set to catch stale facts, cost dashboard for extraction tokens.

---

## 💰 Cost Impact
Memory adds: (1) embedding calls on save and recall, (2) an LLM call to analyse each save, (3) extra prompt tokens from the recalled block. Token and price numbers depend on provider and text size - measure with `result.token_usage` before and after enabling memory; I do not state a fixed number. Tips: `depth="shallow"` where possible, limit recalled items, save only meaningful facts, use a cheap model for analysis, set importance thresholds. Prices change - verify on the provider page.

## 🔷 When to Use
✅ Use when:
- Repeat users/customers and long-lived context.
- Corrections must carry over.

❌ Avoid when:
- Every request is independent and stateless.
- Sensitive data without redaction/retention policy.

---

## 📊 Visual Diagram
```
 question --> recall(scope=/tenant/acme) --> [facts]
                                              |
                                              v  injected into prompt
 Task prompt: "... # Memories from past conversations ... <facts> ..."
                                              |
                                              v
                                          Agent + LLM --> answer
                                              |
                                              v  after run
                              analyse (LLM) -> embed -> store (LanceDB)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memory | Store + recall of facts | तथ्यों का store और recall |
| scope | Namespace path for memories | memories का namespace path |
| embedding | Vector of meaning | अर्थ का vector |
| recency half-life | Time for recency score to halve | recency score आधा होने का समय |
| consolidation | Merging similar memories | मिलती-जुलती memories को जोड़ना |
| importance | Weight of a memory | memory का वज़न |

---

## ⚡ 3-Line Summary
English: `Memory` stores facts with scopes and recalls them by similarity, recency and importance.
Pass your own `Memory(llm, storage, embedder)` and scope per tenant.
It adds embedding and analysis tokens, and recalled facts can be stale.

Hindi: `Memory` तथ्यों को scopes के साथ रखती है और similarity, recency व importance से वापस लाती है।
अपना `Memory(llm, storage, embedder)` दें और हर tenant का अलग scope रखें।
इसमें embedding व analysis के tokens लगते हैं, और याद किए तथ्य पुराने हो सकते हैं।

---

## ➡️ Next Topic
**#93 Crew tools** - memory remembers; tools let the crew act and fetch fresh facts, and you can share tools across agents.

---
