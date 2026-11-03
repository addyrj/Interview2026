---

# 506. AI System Design — Framework
# हिंदी में: AI System Design — Framework

---

## 🔵 Simple Definition (English)
An AI system design framework is a fixed order of steps to answer any "design an AI system" question: clarify requirements, estimate scale, choose architecture, pick components, handle quality, cost, safety and operations. It keeps you from jumping straight to "use GPT + vector DB".

## 🔵 सरल परिभाषा (Hindi)
AI system design framework steps का fixed क्रम है जिससे हर "AI system design करो" सवाल हल होता है: requirements समझो, scale estimate करो, architecture चुनो, components चुनो, फिर quality, cost, safety और operations देखो। सीधे "GPT + vector DB" पर कूदने से बचाता है।

---

## 🔴 Problem it Solves
Candidates and teams often pick tools first and discover later that latency, cost or accuracy requirements were never defined. A framework forces trade-offs to be explicit and gives a calm structure in interviews.

## 🔴 यह क्यों बना? (Hindi)
लोग पहले tools चुन लेते हैं और बाद में पता चलता है कि latency, cost, accuracy की requirements तय ही नहीं थीं। Framework trade-offs साफ़ करता है और interview में structure देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Clarify: users, task, inputs, outputs, success metric, constraints
Step 2 → Estimate: QPS, tokens per request, data size, latency budget, cost budget
Step 3 → Baseline: simplest solution (prompt only? RAG? fine-tune? rules?)
Step 4 → High-level design: ingestion, retrieval, generation, serving, storage
Step 5 → Deep dive: pick models, embeddings, vector DB, chunking, caching
Step 6 → Quality: evals, guardrails, hallucination control, human review
Step 7 → Operations: monitoring, scaling, fallbacks, security, rollout
Step 8 → Trade-offs: say what you gave up and what you would do next
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Clarify: users, task, input/output, success metric, constraints
Step 2 → Estimate: QPS, tokens/request, data size, latency, cost budget
Step 3 → Baseline: सबसे सरल solution (prompt? RAG? fine-tune? rules?)
Step 4 → High-level design: ingestion, retrieval, generation, serving
Step 5 → Deep dive: models, embeddings, vector DB, chunking, caching
Step 6 → Quality: evals, guardrails, hallucination control
Step 7 → Operations: monitoring, scaling, fallbacks, security
Step 8 → Trade-offs बताओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Clarify: officers need an HS code with a cited rule in under 5 seconds, 95% top-1 accuracy, 50 requests per second at peak. Estimate: 1,500 input tokens and 150 output tokens per request. Baseline: LLM with the tariff schedule in RAG. Add reranking only if retrieval recall is low. Human review below 0.75 confidence.
**Zomato-style example**: "Design a restaurant Q&A bot": reviews and menus as RAG, tight latency, cache popular questions.

## 🟡 Real Example Hindi mein
**Tariff System**: Clarify: officer को 5 सेकंड में cited rule के साथ HS code चाहिए, 95% accuracy, peak पर 50 requests/sec। Estimate: 1,500 input और 150 output tokens। Baseline: tariff schedule पर RAG। Retrieval recall कम हो तभी reranking जोड़ो। 0.75 से कम confidence पर human review।

---

## 💻 Code Example — Basic
```python
# Basic: capacity estimator for step 2 of the framework (pure Python, offline)
def estimate(qps: float, in_tokens: int, out_tokens: int,
             in_price_per_m: float, out_price_per_m: float) -> dict[str, float]:  # prices are illustrative
    per_req = in_tokens * in_price_per_m / 1e6 + out_tokens * out_price_per_m / 1e6  # cost of one call
    per_day = per_req * qps * 86_400  # seconds per day times qps
    return {"cost_per_request": per_req, "cost_per_day": per_day,  # results
            "tokens_per_sec": qps * (in_tokens + out_tokens)}  # throughput needed


r = estimate(qps=50, in_tokens=1500, out_tokens=150, in_price_per_m=0.5, out_price_per_m=1.5)  # sample numbers
for k, v in r.items():  # print each
    print(k, round(v, 4))  # rounded values
```

## 💻 Code Example — Advanced
```python
# Advanced: a design-checklist object that refuses to proceed with missing answers
import asyncio  # async demo
from dataclasses import dataclass, field  # records


@dataclass
class Design:  # holds decisions made at each step
    requirements: dict[str, str] = field(default_factory=dict)  # step 1
    estimates: dict[str, float] = field(default_factory=dict)  # step 2
    components: dict[str, str] = field(default_factory=dict)  # steps 4-5
    risks: list[str] = field(default_factory=list)  # step 7-8

    def validate(self) -> list[str]:  # find missing pieces
        missing: list[str] = []  # collect problems
        for key in ("users", "success_metric", "latency_ms"):  # must-have requirements
            if key not in self.requirements:  # missing?
                missing.append(f"requirement:{key}")  # note it
        for key in ("llm", "retriever", "cache"):  # must-have components
            if key not in self.components:  # missing?
                missing.append(f"component:{key}")  # note it
        return missing  # list of gaps


async def review(d: Design) -> None:  # async to mimic calling a reviewer LLM
    await asyncio.sleep(0)  # yield control
    gaps = d.validate()  # check
    if gaps:  # incomplete
        raise ValueError(f"design incomplete: {gaps}")  # fail loudly
    print("design ok")  # all good


if __name__ == "__main__":
    d = Design({"users": "officers", "success_metric": "top1>=0.95", "latency_ms": "5000"},
               {}, {"llm": "mid-tier", "retriever": "hybrid", "cache": "semantic"})  # filled design
    asyncio.run(review(d))  # run
```

---

## 🟠 FastAPI Integration
In the design, FastAPI is the serving layer: validate input, call the orchestration (RAG chain), stream results, expose health and metrics routes.

```python
from fastapi import FastAPI  # app
from pydantic import BaseModel  # schema

app = FastAPI(title="Tariff AI")  # app


class Q(BaseModel):  # request
    text: str  # product description


@app.get("/healthz")  # liveness for load balancer
async def healthz() -> dict[str, str]:
    return {"status": "ok"}  # simple ok


@app.post("/classify")  # main route
async def classify(q: Q) -> dict[str, str | float]:
    return {"hs_code": "8517.13", "confidence": 0.9}  # replace with RAG pipeline
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph represents the design directly: nodes are components (retrieve, rerank, generate, verify), edges are control flow, and checkpointing gives resumability. LangSmith gives tracing for step 7.

```python
from langgraph.graph import StateGraph, END  # graph builder
from typing import TypedDict  # state typing


class S(TypedDict):  # graph state
    q: str  # question
    docs: list[str]  # retrieved
    answer: str  # output


g = StateGraph(S)  # new graph
g.add_node("retrieve", lambda s: {"docs": ["rule A"]})  # retrieval stub
g.add_node("generate", lambda s: {"answer": "8517.13"})  # generation stub
g.set_entry_point("retrieve")  # start
g.add_edge("retrieve", "generate")  # flow
g.add_edge("generate", END)  # end
print(g.compile().invoke({"q": "phone", "docs": [], "answer": ""}))  # run
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Starting with the tools
✅ Correct: start with requirements and metrics.
```python
# Wrong
design = ["GPT-4", "Pinecone", "LangChain"]  # no requirements
# Right
design = {"latency_ms": 5000, "top1": 0.95, "qps": 50}  # then choose tools
```

❌ Mistake 2: Skipping evaluation and cost
✅ Correct: include evals, monitoring and a cost estimate in every design.

---

## 🧠 Tricky Interview Question
**Q**: "Interviewer says: design a chatbot for company docs. You have 45 minutes. What do you do first?"

**Answer**: Ask clarifying questions: how many docs and users, doc types, freshness, access control per user, accuracy and latency targets, languages, budget. Many wrong designs come from missing access control or freshness needs. Then give a simple baseline (RAG with permissions filter) before adding complexity.

---

## ⚫ Interview Questions + Answers

Q1: Why start with a baseline? (Easy)
A1: It is cheap, fast and gives a measured point to compare. Complexity must earn its place with evals.

Q2: What numbers do you estimate first? (Easy)
A2: Requests per second, tokens per request, data volume, latency budget and monthly cost.

Q3: RAG, fine-tuning or prompt engineering: how to choose? (Medium)
A3: Prompting first. RAG when knowledge is large or changing and you need citations. Fine-tuning for style, format or latency/cost with stable behaviour. They can be combined.

Q4: How do you make an LLM system reliable? (Medium)
A4: Timeouts, retries with backoff, fallback models, validation of structured output, guardrails, caching and graceful degradation.

Q5: How would you evolve the system from 100 to 100,000 users? (Hard)
A5: Stateless API replicas behind a load balancer, queue for heavy jobs, caching layers, sharded or managed vector DB, model routing for cost, rate limits per tenant, observability, batch pipelines for ingestion, and capacity tests before each step.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Interviews and design reviews
- Starting any new AI product

❌ Avoid when:
- You treat it as a rigid script; adapt to the problem

---

## 📊 Visual Diagram
```
Requirements → Estimates → Baseline → Architecture
                                         │
        ┌────────────────────────────────┘
        ▼
  Components (LLM, embeddings, vector DB, cache)
        ▼
  Quality (evals, guardrails) → Ops (monitor, scale) → Trade-offs
```

---

## 💰 Cost Impact
Cost is a design input, not an afterthought. Tokens per request x requests per day x price drives the bill. Example (illustrative prices): 1,500 in + 150 out tokens at 50 QPS gives a very large daily number, which is why caching, routing and prompt trimming appear in the design.
Optimise: shorter prompts, fewer retrieved chunks, smaller models for easy cases, semantic cache, batch for offline jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Baseline | Simplest working solution | शुरुआती सरल solution |
| QPS | Queries per second | प्रति सेकंड queries |
| Latency budget | Max allowed response time | समय सीमा |
| Trade-off | Choice with a cost | समझौता |
| SLO | Target reliability/latency | सेवा लक्ष्य |
| Fallback | Backup path on failure | बैकअप रास्ता |

---

## ⚡ 3-Line Summary
English: Follow a fixed order: requirements, estimates, baseline, design, quality, operations, trade-offs.
Always tie choices to numbers like latency, accuracy and cost.
Start simple and add complexity only when evals justify it.
Hindi: क्रम रखो: requirements, estimates, baseline, design, quality, operations, trade-offs।
हर choice को latency, accuracy, cost जैसे numbers से जोड़ो।
सरल से शुरू करो, evals कहें तभी complexity जोड़ो।

---

## ➡️ Next Topic
**507. Designing RAG at Scale** — applying the framework to the most common AI system.
