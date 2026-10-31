---

# 345. LangGraph for Tariff System
# हिंदी में: Tariff System के लिए LangGraph

---

## 🔵 Simple Definition (English)
This topic puts everything together: a complete **Tariff Classification workflow** as a LangGraph. Nodes: extract product facts, retrieve HS candidates, classify, validate, and either finish or send to human review. State flows through each node, and low-confidence results pause for a human.

## 🔵 सरल परिभाषा (Hindi)
यह topic सब कुछ जोड़ता है: LangGraph में एक पूरा **Tariff Classification workflow**। Nodes: product facts निकालना, HS candidates retrieve करना, classify करना, validate करना, और या तो खत्म करना या human review को भेजना। State हर node से गुज़रती है और low-confidence results human के लिए रुक जाते हैं।

---

## 🔴 Problem it Solves
A single big prompt ("classify this product") is hard to test, hard to debug and cannot pause for approval. Customs classification is high-stakes: a wrong HS code means wrong duty, fines or seized cargo. We need explicit steps, validation rules, an audit trail and a human gate.

## 🔴 यह क्यों बना? (Hindi)
एक बड़ा prompt ("इस product को classify करो") test करना, debug करना मुश्किल है और approval के लिए रुक भी नहीं सकता। Customs classification में जोखिम ज़्यादा है: गलत HS code यानी गलत duty, जुर्माना या माल ज़ब्त। हमें साफ़ steps, validation rules, audit trail और human gate चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input: raw product description from the importer
Step 2 → extract_facts: material, use, voltage, origin -> structured JSON
Step 3 → retrieve_candidates: vector search over HS headings -> top-5
Step 4 → classify: LLM picks one HS code + confidence + reasoning
Step 5 → validate: rule check (code exists, 8 digits, chapter matches facts)
Step 6 → route: valid and confidence >= 0.85 -> finalize
Step 7 → otherwise -> human_review (interrupt, checkpoint saved)
Step 8 → finalize: duty lookup, audit log, return result
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input: importer का raw product description
Step 2 → extract_facts: material, use, voltage, origin -> structured JSON
Step 3 → retrieve_candidates: HS headings पर vector search -> top-5
Step 4 → classify: LLM एक HS code + confidence + reasoning चुनता है
Step 5 → validate: rule check (code मौजूद है, 8 digits, chapter facts से मेल खाता है)
Step 6 → route: valid और confidence >= 0.85 -> finalize
Step 7 → वरना -> human_review (interrupt, checkpoint save)
Step 8 → finalize: duty lookup, audit log, result return
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importer submits "wireless noise-cancelling headphones, Bluetooth, 3.7V battery". The graph extracts facts, retrieves headings 8518 (headphones) and 8517 (telecom apparatus), the LLM picks 8518.30 with 0.92 confidence, the validator confirms the code exists in the tariff table, and the workflow finalizes with duty 20 percent. For "multi-function smart ring" confidence is 0.55, so the graph pauses and a customs officer decides.

**Zomato-style**: The same pattern fits menu-item categorisation: extract, retrieve candidate categories, classify, validate, send low-confidence items to a human moderator.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer "wireless noise-cancelling headphones, Bluetooth, 3.7V battery" देता है। Graph facts निकालता है, headings 8518 (headphones) और 8517 (telecom apparatus) लाता है, LLM 0.92 confidence के साथ 8518.30 चुनता है, validator tariff table में code की पुष्टि करता है और workflow 20 प्रतिशत duty के साथ पूरा होता है। "multi-function smart ring" में confidence 0.55 है, इसलिए graph रुकता है और customs officer फैसला करता है।

**Zomato-style**: यही pattern menu-item categorisation में चलता है: extract, candidate categories retrieve, classify, validate, कम confidence वाले items human moderator को।

---

## 💻 Code Example — Basic
```python
# Pure Python version of the tariff workflow (mock LLM, runs offline)
from typing import TypedDict  # typed state

class TariffState(TypedDict):
    description: str       # raw product text
    facts: dict[str, str]  # extracted facts
    candidates: list[str]  # HS candidates
    hs_code: str           # chosen code
    confidence: float      # model confidence 0..1
    status: str            # done / needs_review

HS_TABLE: dict[str, str] = {"8518.30": "Headphones", "8517.13": "Smartphones", "9503.00": "Toys"}  # known codes

def extract_facts(s: TariffState) -> TariffState:
    d = s["description"].lower()  # normalise text
    s["facts"] = {"is_audio": "yes" if "headphone" in d else "no"}  # simple fact extraction
    return s

def retrieve_candidates(s: TariffState) -> TariffState:
    s["candidates"] = list(HS_TABLE)  # a real system does vector search here
    return s

def classify(s: TariffState) -> TariffState:
    if s["facts"]["is_audio"] == "yes":  # mock LLM decision
        s["hs_code"], s["confidence"] = "8518.30", 0.92
    else:
        s["hs_code"], s["confidence"] = "9503.00", 0.50
    return s

def validate(s: TariffState) -> TariffState:
    ok = s["hs_code"] in HS_TABLE  # code must exist
    s["status"] = "done" if ok and s["confidence"] >= 0.85 else "needs_review"  # gate
    return s

def run(desc: str) -> TariffState:
    s: TariffState = {"description": desc, "facts": {}, "candidates": [], "hs_code": "", "confidence": 0.0, "status": ""}
    for step in (extract_facts, retrieve_candidates, classify, validate):  # fixed pipeline
        s = step(s)  # each node updates state
    return s

if __name__ == "__main__":
    print(run("Bluetooth headphones"))      # high confidence -> done
    print(run("multi function smart ring")) # low confidence -> needs_review
```

## 💻 Code Example — Advanced
```python
# Async tariff pipeline with typed models, retries and token accounting
import asyncio  # async runtime
import random  # for fake flaky failures
from dataclasses import dataclass, field  # typed state container

@dataclass
class Result:
    hs_code: str = ""                     # chosen code
    confidence: float = 0.0               # model confidence
    status: str = "pending"               # pending / done / needs_review / error
    tokens: int = 0                       # token estimate across nodes
    trail: list[str] = field(default_factory=list)  # audit trail of steps

async def call_llm(prompt: str, attempts: int = 3) -> dict[str, float | str]:
    for i in range(attempts):  # simple retry loop with backoff
        try:
            await asyncio.sleep(0)  # simulate network
            if random.random() < 0.2:  # 20 percent fake failure
                raise TimeoutError("llm timeout")
            return {"code": "8518.30", "conf": 0.9}  # fake answer
        except TimeoutError:
            await asyncio.sleep(0.01 * 2 ** i)  # exponential backoff
    raise RuntimeError("llm failed after retries")  # give up cleanly

async def classify_product(desc: str) -> Result:
    r = Result()  # fresh result
    try:
        r.trail.append("extract")  # audit step
        r.tokens += 200  # extraction tokens
        r.trail.append("retrieve")
        r.trail.append("classify")
        out = await call_llm(f"Classify: {desc}")  # LLM call with retries
        r.hs_code, r.confidence = str(out["code"]), float(out["conf"])  # parse output
        r.tokens += 600  # prompt with candidates + completion
        r.status = "done" if r.confidence >= 0.85 else "needs_review"  # gate
    except Exception as exc:  # any failure becomes a safe state
        r.status = "error"
        r.trail.append(f"error:{exc}")
    return r

async def main() -> None:
    batch = ["headphones", "ring", "phone case"]  # several items
    results = await asyncio.gather(*(classify_product(d) for d in batch))  # run concurrently
    for d, r in zip(batch, results):
        print(d, r.status, r.hs_code, r.tokens)  # show outcome

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Two endpoints: one to start a classification (runs until finished or paused), one for the officer to resume with a decision. A `thread_id` identifies the checkpointed run.

```python
import uuid  # thread ids
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models
from langgraph.types import Command  # resume a paused graph

app = FastAPI()  # app

class ClassifyIn(BaseModel):
    description: str  # product text

class ReviewIn(BaseModel):
    thread_id: str    # run to resume
    hs_code: str      # officer decision

@app.post("/tariff/classify")
async def classify(body: ClassifyIn) -> dict:
    thread_id = str(uuid.uuid4())  # new run id
    cfg = {"configurable": {"thread_id": thread_id}}  # checkpoint key
    try:
        out = await tariff_graph.ainvoke({"description": body.description}, cfg)  # run graph
    except Exception as exc:
        raise HTTPException(502, str(exc))
    paused = "__interrupt__" in out  # waiting for human?
    return {"thread_id": thread_id, "paused": paused, "state": {k: v for k, v in out.items() if k != "__interrupt__"}}

@app.post("/tariff/review")
async def review(body: ReviewIn) -> dict:
    cfg = {"configurable": {"thread_id": body.thread_id}}  # same run
    out = await tariff_graph.ainvoke(Command(resume=body.hs_code), cfg)  # continue after human input
    return {"state": out}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from typing import TypedDict  # state
from langgraph.graph import StateGraph, START, END  # graph
from langgraph.checkpoint.memory import MemorySaver  # use SqliteSaver / Postgres in production
from langgraph.types import interrupt  # pause for a human
from langchain_openai import ChatOpenAI  # LLM
from pydantic import BaseModel, Field  # structured output (pydantic v2)

class Classification(BaseModel):
    hs_code: str = Field(description="8 digit HS code")
    confidence: float = Field(ge=0, le=1)
    reasoning: str

class TState(TypedDict, total=False):
    description: str
    candidates: list[str]
    hs_code: str
    confidence: float
    final_code: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Classification)

def classify_node(s: TState) -> dict:
    res = llm.invoke(f"Product: {s['description']}\nCandidates: {s['candidates']}")  # structured result
    return {"hs_code": res.hs_code, "confidence": res.confidence}

def human_node(s: TState) -> dict:
    decision = interrupt({"suggested": s["hs_code"], "confidence": s["confidence"]})  # pauses here
    return {"final_code": decision}  # value passed by Command(resume=...)

def accept_node(s: TState) -> dict:
    return {"final_code": s["hs_code"]}

def route(s: TState) -> str:
    return "accept" if s["confidence"] >= 0.85 else "human"

g = StateGraph(TState)
g.add_node("classify", classify_node)
g.add_node("accept", accept_node)
g.add_node("human", human_node)
g.add_edge(START, "classify")
g.add_conditional_edges("classify", route, {"accept": "accept", "human": "human"})
g.add_edge("accept", END)
g.add_edge("human", END)
tariff_graph = g.compile(checkpointer=MemorySaver())  # checkpointer is required for interrupt
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting the LLM's HS code without validation
✅ Correct: check the code against the official tariff table.

```python
# Wrong: return whatever the model says
return {"final_code": res.hs_code}
# Right: validate first
if res.hs_code not in HS_TABLE:
    return {"status": "needs_review"}
```

❌ Mistake 2: Using `interrupt` without a checkpointer or thread_id
✅ Correct: compile with a checkpointer and pass `configurable.thread_id`.

```python
# Wrong
app = g.compile()
# Right
app = g.compile(checkpointer=MemorySaver())
```

---

## 🧠 Tricky Interview Question
**Q**: "The model says confidence 0.97 but the code is wrong 8 percent of the time. How do you fix the gate?"

**Answer**: LLM self-reported confidence is poorly calibrated. Build a labelled set, measure accuracy per confidence bucket, and set the threshold from data. Add independent signals: retrieval similarity of the chosen code, agreement across two prompts or models (self-consistency), and rule validators (chapter notes). Combine them into a score, and always send high-duty or high-value shipments to a human regardless of confidence.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why split classification into several nodes?
A1: Each step becomes testable, debuggable and replaceable, and we get an audit trail per node.

Q2: [Easy] What does the checkpointer do?
A2: It saves state after every node, so the graph can pause, resume, survive a crash and support time-travel debugging.

Q3: [Medium] How does human-in-the-loop work in LangGraph?
A3: A node calls `interrupt(payload)`. The run stops and returns the payload. Later you call the graph with `Command(resume=value)` and the same `thread_id`; `interrupt` returns that value.

Q4: [Medium] Where would you put the validator and why?
A4: After classify and before finalize, as deterministic code, not LLM. It enforces hard rules (code exists, chapter matches) that the model must never override.

Q5: [Hard] How do you handle 50,000 classifications per day with a human bottleneck?
A5: Route by risk. Auto-approve high-confidence, low-duty items; queue the rest by priority; cache decisions for identical descriptions; use batch API for non-urgent work; feed human corrections back into a few-shot set and evaluation set; monitor the review rate and drift weekly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Decisions are high-stakes and need audit and approval
- The task has distinct stages with different tools
- You need pause, resume and retries

❌ Avoid when:
- One prompt solves the task reliably
- No human review and no branching, a plain chain is simpler

---

## 📊 Visual Diagram
```
START -> [extract_facts] -> [retrieve_candidates] -> [classify]
                                                        |
                                                   [validate]
                                                        |
                                      conf >= 0.85 and valid?
                                         |yes              |no
                                     [accept]         [human_review]
                                         |             (interrupt)
                                         +-----> [finalize + audit] -> END
```

---

## 💰 Cost Impact
- Extraction (about 200 tokens) + classification (about 800 tokens with 5 candidates) is roughly 1,000 tokens, about $0.0003 on gpt-4o-mini.
- Human review costs far more than tokens, so tuning the threshold matters most.
- Optimise: cheap model for extraction, send only top-5 candidates, cache by normalised description, structured output to avoid long free text, batch non-urgent jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HS code | Global product classification code | Product का वैश्विक classification code |
| Checkpointer | Saves graph state per step | हर step पर state सुरक्षित रखने वाला |
| interrupt | Pause for human input | Human input के लिए रुकना |
| thread_id | Id of one checkpointed run | एक run की पहचान |
| Audit trail | Record of every step | हर step का रिकॉर्ड |
| Confidence gate | Threshold that triggers review | Review शुरू करने वाली सीमा |

---

## ⚡ 3-Line Summary
English: The tariff workflow is a graph of extract, retrieve, classify, validate and finalize. Low confidence or invalid codes pause at a human node using a checkpointer. Validate with deterministic rules and calibrate the threshold with data.
Hindi: Tariff workflow extract, retrieve, classify, validate और finalize का graph है। कम confidence या invalid code पर checkpointer के साथ human node पर रुकते हैं। Deterministic rules से validate करो और threshold data से तय करो।

---

## ➡️ Next Topic
**346. Multi-Agent — What + Why** — when one graph is not enough and several specialised agents should cooperate.
