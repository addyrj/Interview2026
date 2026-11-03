---

# 600. Design: Complete AI System
# हिंदी में: पूरा AI System Design करना

---

## 🔵 Simple Definition (English)
A complete AI system is more than one LLM call. It wraps the model with input guardrails, caching, routing between small and large models, retrieval over your documents, timeouts and fallbacks, and cost and quality logging.

## 🔵 सरल परिभाषा (Hindi)
Complete AI system सिर्फ एक LLM call नहीं है। Model के चारों तरफ input guardrails, caching, छोटे/बड़े model के बीच routing, documents पर retrieval, timeouts/fallbacks और cost/quality logging होती है।

---

## 🔴 Problem it Solves
A demo that calls an LLM breaks in production: prompt injection, repeated expensive questions, slow or failing providers, hallucinated answers, unbounded cost, no audit trail. The system design covers these before launch.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ LLM call वाला demo production में टूटता है: prompt injection, बार-बार वही महँगे सवाल, धीमे/fail होते providers, hallucination, बेकाबू cost, audit trail का न होना। System design इन सबको launch से पहले संभालता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → API layer (FastAPI): auth, rate limit, request validation
Step 2 → Input guardrails: length check, prompt-injection patterns
Step 3 → Cache lookup (exact, later semantic): hit -> return immediately
Step 4 → Retrieve relevant chunks from the knowledge base
Step 5 → No evidence -> safe fallback ("I don't know"), no LLM call
Step 6 → Route: simple -> small model, hard -> large model
Step 7 → Call LLM with timeout; retry/fallback on failure
Step 8 → Output checks (grounding, format); store in cache
Step 9 → Log tokens, cost, latency, prompt version; return answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → API layer: auth, rate limit, validation
Step 2 → Input guardrails: length और prompt-injection check
Step 3 → Cache lookup: hit हो तो तुरंत return
Step 4 → Knowledge base से relevant chunks निकालो
Step 5 → Evidence नहीं मिला -> safe fallback, LLM call नहीं
Step 6 → Route: आसान -> छोटा model, कठिन -> बड़ा model
Step 7 → Timeout के साथ LLM call; fail पर retry/fallback
Step 8 → Output checks; cache में store
Step 9 → Tokens, cost, latency, prompt version log करके answer लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: a broker asks "HS code for laptop?". The system validates input, finds no cached answer, retrieves the laptop tariff chunk, routes to the small model, answers with a citation, caches it, and logs tokens. The same question a minute later is served from cache with zero LLM cost. "weather today" finds no evidence and gets the safe fallback. "ignore previous instructions" is blocked at the guardrail. `main.py` demonstrates exactly these four cases.

**Zomato/Amazon style**: the same layout powers a support bot: refund policy RAG, order-status tool calls, escalation to a human on low confidence.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker पूछता है "laptop का HS code?"। System input validate करता है, cache में नहीं मिलता, laptop का chunk retrieve करता है, छोटे model पर route करता है, citation के साथ जवाब देता है, cache करता है और tokens log करता है। एक मिनट बाद वही सवाल cache से, बिना LLM cost के। "weather today" पर evidence नहीं, इसलिए safe fallback। "ignore previous instructions" guardrail पर block।

**Zomato/Amazon**: यही layout support bot चलाता है: refund policy RAG, order-status tool calls, कम confidence पर human को escalate।

---

## 💻 Code Example — Basic
```python
# Smallest useful skeleton: validate -> cache -> answer
cache: dict[str, str] = {}                              # in-memory cache (demo only)


def answer(q: str) -> str:
    q = q.strip()                                       # normalise input
    if not q or len(q) > 2000:                          # basic guardrail
        raise ValueError("invalid query")
    if q in cache:                                      # cache hit: no LLM cost
        return cache[q]
    result = f"(LLM answer for: {q})"                   # stand-in for the real call
    cache[q] = result                                   # remember for next time
    return result


print(answer("HS code for laptop?"))                    # computed
print(answer("HS code for laptop?"))                    # served from cache
```

## 💻 Code Example — Advanced
Full file: `main.py` (`AISystem` with guardrails, cache, retrieval, router, timeout, token log, mock LLMs). Observed output:
```
HS code for laptop? -> {'answer': '[small] answer based on: ...', 'source': 'small'}
HS code for laptop? -> {'answer': '[small] ...', 'source': 'cache'}
weather today -> {'answer': "I don't know based on available documents.", 'source': 'fallback'}
ignore previous instructions -> blocked: possible prompt injection
usage: [('small', 17, 20)]
```
```python
# Excerpt from main.py
async def answer(self, q: str) -> dict[str, str]:
    q = guard_input(q)                                   # raises on bad input
    key = hashlib.sha256(q.lower().encode()).hexdigest() # cache key
    if key in self.cache:
        return {"answer": self.cache[key], "source": "cache"}
    docs = retrieve(q)                                   # grounding evidence
    if not docs:
        return {"answer": "I don't know based on available documents.", "source": "fallback"}
    llm = self.route(q, docs)                            # small vs large model
    try:
        text, tin, tout = await asyncio.wait_for(llm.complete(prompt), timeout=5)
    except asyncio.TimeoutError:                         # provider too slow
        return {"answer": "Service busy, try again.", "source": "timeout"}
```
Everything is mocked (retrieval is a keyword lookup, LLM is a stub); replace with a vector store and a real client.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import AISystem                               # our module

app = FastAPI()
system = AISystem()                                     # one shared instance


class Ask(BaseModel):
    question: str


@app.post("/ask")
async def ask(req: Ask) -> dict:
    try:
        return await system.answer(req.question)
    except ValueError as e:                             # bad input
        raise HTTPException(status_code=422, detail=str(e))
    except PermissionError as e:                        # injection attempt
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "calls": len(system.tokens)}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph models this as a graph: guard -> cache -> retrieve -> route -> generate -> verify, with conditional edges.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END


class State(TypedDict):
    question: str
    docs: list[str]
    answer: str


def retrieve_node(s: State) -> State:
    return {**s, "docs": ["Laptops: HS 8471.30"]}        # stand-in retriever


def generate_node(s: State) -> State:
    return {**s, "answer": f"Based on {s['docs'][0]}"}  # stand-in LLM


def has_docs(s: State) -> str:
    return "generate" if s["docs"] else "end"            # conditional routing


g = StateGraph(State)
g.add_node("retrieve", retrieve_node)
g.add_node("generate", generate_node)
g.set_entry_point("retrieve")
g.add_conditional_edges("retrieve", has_docs, {"generate": "generate", "end": END})
g.add_edge("generate", END)
app_graph = g.compile()                                  # app_graph.invoke({...})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating the LLM as the whole system.
✅ Correct: add guardrails, retrieval, fallbacks, observability.

❌ Mistake 2: No timeout or fallback.
```python
# Wrong
text = await llm.complete(prompt)
# Right
text = await asyncio.wait_for(llm.complete(prompt), timeout=5)
```

❌ Mistake 3: Caching answers without versioning: after the knowledge base or prompt changes, stale answers persist. Include prompt version and doc version in the cache key or use a TTL.

---

## 🧠 Tricky Interview Question
**Q**: "Design a tariff Q&A system for 1M queries a day with strict accuracy. What are the main trade-offs?"

**Answer**: Accuracy vs cost vs latency. Use hybrid retrieval (keyword for exact codes + vectors), a reranker on a small candidate set, a small model by default with escalation to a large model on low confidence, citation-required answers verified against chunks, semantic cache for repeated queries, async workers with rate limits, per-tenant budgets, and a human-review path for low confidence. Evaluate continuously on a golden set; monitor retrieval recall, faithfulness, p95 latency, cost per answer.

---

## ⚫ Interview Questions + Answers

Q1: Why add a cache in front of an LLM?
A1: Repeated questions are common; a hit costs nothing and answers instantly.

Q2: What is model routing?
A2: Choosing a cheaper model for easy requests and a stronger one for hard ones.

Q3: How do you defend against prompt injection?
A3: Layered: input filters, separating instructions from data, least-privilege tools, output validation; no single check is enough.

Q4: What do you log for each request?
A4: Request id, prompt version, retrieved chunk ids, model, tokens, cost, latency, outcome.

Q5 (Hard): The provider has an outage. How does the system stay up?
A5: Timeouts with retries and backoff, a circuit breaker, a secondary provider or smaller local model as fallback, cached answers for frequent queries, graceful degraded messages, and queueing for non-urgent work.

---

## 🔷 When to Use + When Not to Use
✅ Use this full design when:
- Real users, real money, accuracy or compliance requirements

❌ Avoid it when:
- Prototype or internal demo; start with the smallest skeleton and add layers as risks appear

---

## 📊 Visual Diagram
```
 Client ─► FastAPI ─► Guardrails ─► Cache ──hit──► answer
                          │blocked      │miss
                          ▼             ▼
                       400/422      Retrieve ──none──► fallback
                                        │docs
                                        ▼
                                  Router (small / large)
                                        │
                                  LLM (timeout, retry)
                                        │
                                  Verify + store cache
                                        ▼
                         Log: tokens, cost, latency ─► answer
```

---

## 💰 Cost Impact
Each layer reduces spend: cache hits cost zero tokens; the "no evidence" fallback avoids an LLM call; routing sends most traffic to the small model; token logging reveals regressions. In the demo run, one real LLM call served two identical questions (17 input and 20 output tokens by the mock's own counting, not real usage). At scale the largest levers are cache hit rate, routing ratio, context size, and output caps. Prices vary by provider; measure with your own logs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Guardrail | Input/output safety check | Input/output सुरक्षा जाँच |
| Router | Picks model per request | Request के हिसाब से model चुनने वाला |
| Fallback | Safe default response | सुरक्षित default जवाब |
| Circuit breaker | Stops calling a failing service | Fail होती service को call करना रोकना |
| Observability | Logs, metrics, traces | Logs, metrics, traces से सिस्टम देखना |

---

## ⚡ 3-Line Summary
English: A production AI system wraps the LLM with guardrails, cache, retrieval, routing, timeouts and logging. Each layer protects accuracy, cost or reliability. Start small, add layers as risks appear.
Hindi: Production AI system LLM के चारों ओर guardrails, cache, retrieval, routing, timeouts और logging लगाता है। हर layer accuracy, cost या reliability बचाती है। छोटे से शुरू करो, risk के हिसाब से layers जोड़ो।

---

## ➡️ Next Topic
**601.** Continue with the next section of the curriculum in How.md (this completes the 21-interview-problems batch 593-600).
