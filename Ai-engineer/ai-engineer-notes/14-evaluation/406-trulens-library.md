---

# 406. TruLens Library
# हिंदी में: TruLens Library

---

## 🔵 Simple Definition (English)
TruLens is an open-source library for evaluating and tracking LLM apps. It records every call of your app (a trace), then runs **feedback functions** on the record, most famously the **RAG Triad**: context relevance, groundedness, and answer relevance. Results go to a local database and a dashboard.

## 🔵 सरल परिभाषा (Hindi)
TruLens LLM apps को evaluate और track करने की open-source library है। यह आपके app की हर call (trace) record करती है, फिर record पर **feedback functions** चलाती है, खासकर **RAG Triad**: context relevance, groundedness और answer relevance। Results local database और dashboard में जाते हैं।

---

## 🔴 Problem it Solves
Offline test sets show quality at one moment. In development you want to compare app versions side by side, and in production you want to see which individual calls were poor. TruLens combines tracing + evaluation + comparison dashboard, so you see which version (prompt, chunk size, retriever) is better and why.

## 🔴 यह क्यों बना? (Hindi)
Offline test sets एक समय की quality दिखाते हैं। Development में app versions की side-by-side तुलना और production में खराब calls देखना ज़रूरी है। TruLens tracing + evaluation + comparison dashboard साथ देता है, ताकि पता चले कि कौन सा version (prompt, chunk size, retriever) बेहतर है और क्यों।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Instrument app methods (retrieve, generate) so calls are recorded
Step 2 → Define feedback functions backed by a provider LLM (e.g. OpenAI)
Step 3 → Wrap app in a recorder (TruCustomApp / TruChain / TruGraph) with feedbacks
Step 4 → Run queries inside `with recorder as recording:`
Step 5 → TruLens stores records + runs feedbacks (usually in background)
Step 6 → Open dashboard / query leaderboard: compare app versions by triad scores
Step 7 → Fix the weakest leg of the triad
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → App methods (retrieve, generate) instrument करो ताकि calls record हों
Step 2 → Provider LLM (जैसे OpenAI) पर आधारित feedback functions बनाओ
Step 3 → App को feedbacks के साथ recorder (TruCustomApp / TruChain / TruGraph) में wrap करो
Step 4 → `with recorder as recording:` के अंदर queries चलाओ
Step 5 → TruLens records store करता है और feedbacks चलाता है (आमतौर पर background में)
Step 6 → Dashboard / leaderboard देखो: triad scores से versions की तुलना
Step 7 → Triad की सबसे कमज़ोर कड़ी ठीक करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three app versions (chunk 200, 500, 1000 tokens). The leaderboard shows: chunk 200 has high groundedness but low context relevance (too fragmented), chunk 1000 has low answer relevance (noisy context). Chunk 500 wins on all three. In production, 5% of traffic is recorded and any call with groundedness < 0.5 is flagged for review.

**Zomato-style**: Triad on a restaurant-FAQ bot shows context relevance is low for Hinglish queries, pointing to an embedding problem, not a generation problem.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन app versions (chunk 200, 500, 1000 tokens)। Leaderboard: chunk 200 में groundedness ऊँची पर context relevance कम (बहुत टुकड़े), chunk 1000 में answer relevance कम (noisy context)। Chunk 500 तीनों में जीता। Production में 5% traffic record होता है और groundedness < 0.5 वाली call review के लिए flag होती है।

**Zomato-style**: Restaurant-FAQ bot पर triad दिखाता है कि Hinglish queries में context relevance कम है, यानी समस्या embedding की है, generation की नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny "RAG triad" tracker in pure Python (offline, toy lexical scoring)
from dataclasses import dataclass  # record type


@dataclass
class Record:  # one traced call
    question: str  # input
    contexts: list[str]  # retrieved chunks
    answer: str  # output


def overlap(a: str, b: str) -> float:  # toy similarity: shared-word ratio
    wa, wb = set(a.lower().split()), set(b.lower().split())  # word sets
    return len(wa & wb) / len(wa) if wa else 0.0  # share of a found in b


def triad(r: Record) -> dict[str, float]:  # three scores
    ctx = " ".join(r.contexts)  # join contexts
    return {
        "context_relevance": round(overlap(r.question, ctx), 2),  # question vs context
        "groundedness": round(overlap(r.answer, ctx), 2),  # answer vs context
        "answer_relevance": round(overlap(r.question, r.answer), 2),  # question vs answer
    }


rec = Record("hs code lithium battery", ["hs 8507.60 covers lithium battery accumulators"], "hs code 8507.60 lithium battery")
print(triad(rec))  # printed scores between 0 and 1 (toy numbers, not real TruLens output)
```

## 💻 Code Example — Advanced
```python
# Advanced: TruLens 1.x recorder with the RAG triad (OpenAI provider)
# pip install trulens trulens-providers-openai   (API names follow trulens 1.x; check your version)
import logging  # logs
import numpy as np  # aggregate over chunks

from trulens.apps.custom import TruCustomApp, instrument  # tracing helpers
from trulens.core import Feedback, Select, TruSession  # core objects
from trulens.providers.openai import OpenAI as TruOpenAI  # LLM provider for feedbacks

log = logging.getLogger("trulens_demo")  # logger
session = TruSession()  # local SQLite store
session.reset_database()  # clean start for the demo only
provider = TruOpenAI(model_engine="gpt-4o-mini")  # judge model


class TariffRAG:  # our app
    def __init__(self, retriever, llm) -> None:
        self.retriever = retriever  # any callable: str -> list[str]
        self.llm = llm  # any callable: str -> str

    @instrument  # record this call + its return value
    def retrieve(self, query: str) -> list[str]:
        return self.retriever(query)  # list of chunks

    @instrument  # record generation
    def query(self, query: str) -> str:
        try:
            ctx = self.retrieve(query)  # retrieval step
            return self.llm(f"Context: {ctx}\nQuestion: {query}")  # answer
        except Exception as exc:  # keep failures visible in traces
            log.exception("query failed: %s", exc)  # log
            raise  # re-raise to caller


f_ctx = (Feedback(provider.context_relevance_with_cot_reasons, name="Context Relevance")
         .on_input().on(Select.RecordCalls.retrieve.rets[:]).aggregate(np.mean))  # per-chunk mean
f_ground = (Feedback(provider.groundedness_measure_with_cot_reasons, name="Groundedness")
            .on(Select.RecordCalls.retrieve.rets.collect()).on_output())  # context -> answer
f_ans = Feedback(provider.relevance_with_cot_reasons, name="Answer Relevance").on_input_output()  # Q -> A


def run(app: TariffRAG, questions: list[str], version: str) -> None:
    recorder = TruCustomApp(app, app_name="TariffRAG", app_version=version,
                            feedbacks=[f_ctx, f_ground, f_ans])  # wrap with feedbacks
    with recorder:  # everything inside is recorded
        for q in questions:  # each query
            app.query(q)  # traced call
    print(session.get_leaderboard())  # compare versions by average feedback scores
```

---

## 🟠 FastAPI Integration
Record production traffic by wrapping the app once and calling it inside the recorder context in each request.

```python
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # validation

api = FastAPI()  # app
rag = TariffRAG(retriever=lambda q: ["8507.60 covers lithium-ion accumulators."],
                llm=lambda p: "8507.60")  # demo stubs
recorder = TruCustomApp(rag, app_name="TariffRAG", app_version="prod",
                        feedbacks=[f_ctx, f_ground, f_ans])  # shared recorder


class Q(BaseModel):  # request
    question: str  # user question


@api.post("/ask")  # endpoint
async def ask(q: Q) -> dict:
    try:
        with recorder:  # record this request
            answer = rag.query(q.question)  # traced call (sync app)
    except Exception as exc:  # app failure
        raise HTTPException(500, str(exc))  # error
    return {"answer": answer}  # response
```

---

## 🔗 LangChain / LangGraph Connection
TruLens provides `TruChain` for LangChain LCEL chains and a LangGraph recorder (`TruGraph`) in recent versions. You wrap the compiled chain/graph, and the instrumentation finds retriever and LLM calls automatically.

```python
from trulens.apps.langchain import TruChain  # LangChain recorder
# chain = prompt | llm | parser          # your LCEL chain
# tru_chain = TruChain(chain, app_name="TariffChain", feedbacks=[f_ans])
# with tru_chain:
#     chain.invoke({"question": "HS code for iPhone?"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating only the final answer
✅ Correct: score all three legs of the triad

```python
# Wrong - only answer relevance; cannot tell retrieval vs generation failures
feedbacks = [f_ans]
# Right
feedbacks = [f_ctx, f_ground, f_ans]
```

❌ Mistake 2: `reset_database()` in production code (deletes history)
✅ Correct: use it only in demos/tests.

❌ Mistake 3: Running feedbacks on 100% of production traffic with an expensive judge
✅ Correct: sample (5-10%) or use a cheap judge.

---

## 🧠 Tricky Interview Question
**Q**: "Triad scores: context relevance 0.9, groundedness 0.4, answer relevance 0.85. What is wrong and what do you change?"

**Answer**: Retrieval is fine (context relevant) and the answer addresses the question, but the answer contains claims not supported by the context: hallucination or the model using parametric knowledge. Fix generation: tighter prompt ("answer only from context, say 'not found' otherwise"), lower temperature, citations, or a groundedness-check/regenerate loop. Do not touch the retriever.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is the RAG Triad?
A1: Context relevance, groundedness, and answer relevance.

Q2: [Easy] What is a feedback function?
A2: A function (often LLM-based) that scores a record on some quality, returning 0-1 and optionally a reason.

Q3: [Medium] What does groundedness catch that answer relevance does not?
A3: Answers that sound on-topic but contain unsupported claims (hallucinations).

Q4: [Medium] How does TruLens differ from Ragas?
A4: TruLens is trace-centric with a dashboard, app versioning and online monitoring; Ragas is dataset-centric batch evaluation with RAG-specific metrics. They are often used together.

Q5: [Hard] How would you use TruLens for production monitoring cheaply?
A5: Record all traces, run feedbacks on a sample with a cheap judge, alert on rolling-mean drops, store low-scoring records, and send them to a human review queue and into the regression dataset.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You compare app versions and want a dashboard
- You want tracing and evaluation in one tool

❌ Avoid when:
- You only need a CI pass/fail test (DeepEval is simpler)
- You cannot add instrumentation to the app

---

## 📊 Visual Diagram
```
            query
              │
     ┌────────▼────────┐
     │  retrieve()     │──► contexts ──► Context Relevance (Q vs each chunk)
     └────────┬────────┘                     │
     ┌────────▼────────┐                     │
     │  generate()     │──► answer ──► Groundedness (contexts vs answer)
     └────────┬────────┘                     │
              ▼                              ▼
   Answer Relevance (Q vs answer) ──► Dashboard / Leaderboard
```

---

## 💰 Cost Impact
Each triad feedback calls the judge once per record (context relevance once per chunk, so 3-5 calls for top-k). Roughly 5-8 judge calls per query, ~3-6K tokens. On gpt-4o-mini that is about $0.001 per query; at 100K queries/month with 100% evaluation it is ~$100.
Optimise: sample 5%, cheap judge, aggregate over fewer chunks, run feedbacks deferred in background.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG Triad | 3 core RAG metrics | RAG के 3 मुख्य metrics |
| Feedback function | Scorer on a record | Record पर scorer |
| Record / Trace | Saved app call | सेव की हुई app call |
| Groundedness | Answer supported by context | Answer context से समर्थित |
| Leaderboard | Version comparison table | Versions की तुलना table |

---

## ⚡ 3-Line Summary
English: TruLens traces your app and scores each record with feedback functions, centred on the RAG Triad. Compare versions in the dashboard and fix the weakest triad leg. Sample production traffic to control cost.
Hindi: TruLens आपके app को trace करता है और हर record को feedback functions से score करता है, RAG Triad पर केंद्रित। Dashboard में versions compare करो और सबसे कमज़ोर triad कड़ी ठीक करो। Cost के लिए production traffic sample करो।

---

## ➡️ Next Topic
**407. Evaluation Dataset Creation** - how to build the test data every tool above depends on.
