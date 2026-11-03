---

# 536. Design: Tariff Classification System
# हिंदी में: Tariff Classification System का Design

---

## 🔵 Simple Definition (English)
A tariff classification system takes a product description ("wireless earbuds with charging case") and returns the correct Harmonized System (HS) code with a reason and confidence. It combines retrieval over the tariff schedule, LLM reasoning, rule validation, and human review for low-confidence cases.

## 🔵 सरल परिभाषा (Hindi)
Tariff classification system product description ("charging case वाले wireless earbuds") लेकर सही Harmonized System (HS) code, कारण और confidence लौटाता है। इसमें tariff schedule पर retrieval, LLM reasoning, rule validation और कम confidence पर human review शामिल है।

---

## 🔴 Problem it Solves
Manual classification needs experts, is slow, and varies between people. A wrong code means wrong duty, penalties, or shipment delays. An LLM alone may invent codes that do not exist, so we need grounding in the real schedule and validation.

## 🔴 यह क्यों बना? (Hindi)
Manual classification में experts चाहिए, यह धीमा है और लोगों में अलग-अलग होता है। गलत code का मतलब गलत duty, penalty या shipment में देरी। सिर्फ LLM ऐसे codes बना सकता है जो मौजूद ही नहीं, इसलिए असली schedule में grounding और validation ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input: description, optional material, use, country of import
Step 2 → Normalize text, extract attributes (material, function, power source) with LLM
Step 3 → Hybrid retrieve candidate headings (vector + BM25) from schedule, notes, rulings
Step 4 → LLM picks code from the candidates only, explains with chapter notes (JSON)
Step 5 → Validate: code exists in schedule, format ok (6/8/10 digits), rules not violated
Step 6 → Confidence = agreement of retrieval score, self-consistency, validator result
Step 7 → High confidence -> auto-answer; low -> human review queue
Step 8 → Store decision + evidence in audit log; reviewer corrections go to eval set
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input: description, material, use, import country
Step 2 → Text normalize करो, LLM से attributes निकालो (material, function, power)
Step 3 → Schedule, notes, rulings से hybrid retrieval (vector + BM25) से candidates लाओ
Step 4 → LLM सिर्फ candidates में से code चुनता है और chapter notes से कारण देता है
Step 5 → Validate: code schedule में है, format सही है, rules नहीं टूटे
Step 6 → Confidence = retrieval score, self-consistency और validator का मेल
Step 7 → ज़्यादा confidence पर auto-answer; कम पर human review queue
Step 8 → Decision और evidence audit log में; reviewer corrections eval set में
```

---

## 🟡 Real World Example
**Tariff Classification System** (the example itself): "Smartwatch with cellular calling" - candidates 8517.62 (apparatus for reception/transmission) and 9102 (wrist-watches). The chapter note says which heading prevails when a device has both functions. The system cites that note, validates 8517.62 exists, scores confidence 0.82, and auto-answers. A vague input "machine part" gets 0.3 and goes to a human.
**Amazon-style**: A seller listing is auto-classified for cross-border duty estimation.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: "Cellular calling वाली smartwatch" - candidates 8517.62 और 9102 (wrist-watches)। Chapter note बताता है कि दोनों functions होने पर कौन सा heading लागू होता है। System वह note cite करता है, 8517.62 के existence को validate करता है, confidence 0.82 देता है और auto-answer करता है। अस्पष्ट input "machine part" को 0.3 मिलता है और वह human के पास जाता है।
**Amazon-style**: Seller listing का cross-border duty estimate के लिए auto-classification।

---

## 💻 Code Example — Basic
```python
# Basic: rule + keyword classifier with validation (pure Python, runs offline)
SCHEDULE: dict[str, str] = {                           # tiny fake tariff schedule
    "8507.60": "lithium-ion accumulators batteries",
    "8518.30": "headphones earphones earbuds",
    "8517.62": "smartphones telephones wireless communication apparatus",
}


def classify(description: str) -> tuple[str | None, float]:
    """Return (code, confidence) by keyword overlap."""
    words = set(description.lower().split())           # words in the description
    best_code: str | None = None                       # best code so far
    best_score = 0.0                                   # best score so far
    for code, text in SCHEDULE.items():                # try each entry
        overlap = len(words & set(text.split()))       # shared words
        score = overlap / max(len(text.split()), 1)    # normalise by entry size
        if score > best_score:                         # better match
            best_code, best_score = code, score        # remember it
    return best_code, round(best_score, 2)             # result


def is_valid(code: str | None) -> bool:
    return code in SCHEDULE                            # code must exist in schedule


code, conf = classify("wireless earbuds with case")    # run
print(code, conf, "valid" if is_valid(code) else "invalid")   # show result
print("route:", "auto" if conf >= 0.4 else "human")    # threshold routing
```

## 💻 Code Example — Advanced
```python
# Production style: async pipeline with retrieval, LLM choice restricted to candidates,
# validation, confidence routing, and audit record
import asyncio                                         # async
import json                                            # parse model JSON
from dataclasses import dataclass, asdict              # result record
from typing import Protocol                            # interfaces


@dataclass
class Decision:
    code: str | None                                   # chosen HS code
    reason: str                                        # explanation with note refs
    confidence: float                                  # 0..1
    route: str                                         # "auto" or "human"


class Retriever(Protocol):
    async def candidates(self, text: str, k: int) -> list[dict]: ...   # [{code, title, score}]


class LLM(Protocol):
    async def complete(self, prompt: str) -> str: ...  # returns JSON string


VALID_CODES: set[str] = set()                          # load from the official schedule at startup


async def classify(desc: str, retr: Retriever, llm: LLM, threshold: float = 0.7) -> Decision:
    """Full classification flow."""
    cands = await retr.candidates(desc, k=8)           # step 3: candidate headings
    if not cands:                                      # nothing found
        return Decision(None, "no candidates", 0.0, "human")
    allowed = {c["code"] for c in cands}               # model may only choose from these
    prompt = (f"Product: {desc}\nCandidates: {json.dumps(cands)}\n"
              'Pick ONE code from candidates. JSON: {"code":..., "reason":...}')   # grounded prompt
    try:
        raw = await asyncio.wait_for(llm.complete(prompt), timeout=20)   # bounded call
        data = json.loads(raw)                         # parse
    except (asyncio.TimeoutError, json.JSONDecodeError, KeyError):   # failures go to a human
        return Decision(None, "llm_failed", 0.0, "human")
    code = data.get("code")                            # chosen code
    if code not in allowed or (VALID_CODES and code not in VALID_CODES):   # hallucination guard
        return Decision(None, "invalid code from model", 0.0, "human")
    top = max(c["score"] for c in cands)               # best retrieval score
    conf = round(min(1.0, top), 2)                     # simple confidence (add self-consistency in prod)
    return Decision(code, data.get("reason", ""), conf, "auto" if conf >= threshold else "human")


def audit(desc: str, d: Decision) -> str:
    return json.dumps({"input": desc, **asdict(d)})    # append to an audit log store
```

---

## 🟠 FastAPI Integration
Synchronous endpoint for single items; bulk endpoint for CSV uploads processed in the background. Always return evidence and a review flag.

```python
from fastapi import FastAPI, HTTPException             # FastAPI
from pydantic import BaseModel, Field                  # request model

app = FastAPI(title="Tariff Classifier")               # app


class ClassifyIn(BaseModel):
    description: str = Field(min_length=3, max_length=2000)   # input limits
    country: str = "IN"                                # destination country


@app.post("/classify")
async def classify_route(body: ClassifyIn) -> dict:
    try:
        # decision = await classify(body.description, retriever, llm)   # call pipeline
        decision = {"code": "8518.30", "confidence": 0.82, "route": "auto"}   # stub so file is runnable
    except Exception as exc:                           # unexpected failure
        raise HTTPException(502, f"classification failed: {exc}")
    return {"input": body.description, **decision}     # response with evidence
```

---

## 🔗 LangChain / LangGraph Connection
This is a natural LangGraph workflow: `extract_attributes` -> `retrieve` -> `decide` -> `validate` -> conditional edge: confident goes to `finish`, otherwise to `human_review` (using `interrupt` with a checkpointer to wait for the reviewer).

```python
# LangGraph skeleton (pip install langgraph)
from typing import TypedDict                           # state type
from langgraph.graph import StateGraph, END            # graph builder


class S(TypedDict, total=False):
    desc: str                                          # input
    code: str                                          # decision
    confidence: float                                  # score


def decide(s: S) -> S:
    return {"code": "8518.30", "confidence": 0.82}     # placeholder node


def route(s: S) -> str:
    return "done" if s.get("confidence", 0) >= 0.7 else "human"   # branch


g = StateGraph(S)                                      # create graph
g.add_node("decide", decide)                           # add node
g.add_node("human", lambda s: s)                       # human review placeholder
g.set_entry_point("decide")                            # start node
g.add_conditional_edges("decide", route, {"done": END, "human": "human"})   # branch
g.add_edge("human", END)                               # end after review
app_graph = g.compile()                                # runnable graph
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Letting the LLM answer from memory
✅ Correct: restrict choices to retrieved candidates and validate against the schedule.

```python
# Wrong: "What is the HS code for earbuds?" -> may return a plausible but non-existent code
# Right: pass candidates, require code in candidates, check VALID_CODES
```

❌ Mistake 2: Storing codes as integers
✅ Correct: use strings; "0101.21" and leading zeros matter.

❌ Mistake 3: Using one fixed schedule version forever
✅ Correct: version the schedule by year; classify against the version matching the shipment date.

---

## 🧠 Tricky Interview Question
**Q**: "Accuracy is 92% overall but customs penalties still occur. What do you check?"

**Answer**: Overall accuracy hides costly errors. Break down by chapter and by value at risk; the 8% may be concentrated in high-duty goods. Check confidence calibration (are 0.9-confidence answers really 90% right?), lower auto-approve thresholds for high-duty chapters, and review the unseen-product tail. Measure cost-weighted error, not just accuracy, and keep an appeals/audit trail.

---

## ⚫ Interview Questions + Answers

Q1: What is an HS code?
A1: An international product classification, 6 digits shared worldwide, extended to 8-10 digits by countries. It decides duty rates.

Q2: Why retrieval before the LLM?
A2: To ground the answer in real headings and notes, reduce hallucinated codes, and cut prompt size.

Q3: How do you decide when to involve a human?
A3: Low confidence, validator failure, high-duty goods, or ambiguity between candidates. Reviewer corrections feed the evaluation set.

Q4: How do you evaluate the system?
A4: A labelled set of past rulings; measure top-1 and top-k accuracy at 2, 4, 6 digits, calibration, and cost-weighted error, by chapter.

Q5: (Hard) How do you handle tariff schedule updates and legal audit?
A5: Version schedules and index per version; re-embed only changed entries; log input, retrieved evidence, prompt version, model version and output for every decision so a result can be reproduced and defended; run regression eval before switching models or prompts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- High volume of varied product descriptions
- Experts are a bottleneck, and an audit trail is available

❌ Avoid when:
- Legal binding rulings are needed without human sign-off
- Descriptions are too vague and cannot be improved by asking follow-ups

---

## 📊 Visual Diagram
```
 Description ─▶ attribute extraction ─▶ hybrid retrieval (schedule+notes+rulings)
                                              │ candidates
                                              ▼
                                   LLM chooses (candidates only)
                                              │
                                   validator (exists? format? rules?)
                                      │                 │
                              confidence ≥ τ        confidence < τ
                                      ▼                 ▼
                                 auto answer        human review ─▶ eval set
                                      └──── audit log ◀──┘
```

---

## 💰 Cost Impact
Per item: attribute extraction (small), retrieval (cheap), one decision call with about 8 candidates (roughly 1-2k input tokens, small output; illustrative). Self-consistency (3 samples) triples the decision cost.
Optimize: cache by normalised description, small model for extraction, larger model only for ambiguous cases, trim candidate text, batch bulk jobs (provider batch APIs offer discounts; check current terms).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HS Code | Harmonized System product code | उत्पाद वर्गीकरण code |
| Heading | 4-digit group in the schedule | Schedule का 4-अंकीय समूह |
| Chapter note | Legal rule guiding classification | वर्गीकरण का कानूनी नियम |
| Calibration | Confidence matches real accuracy | Confidence का असली accuracy से मेल |
| Audit log | Record of every decision | हर फैसले का रिकॉर्ड |
| Human-in-the-loop | Person reviews uncertain cases | अनिश्चित मामलों में इंसान की समीक्षा |

---

## ⚡ 3-Line Summary
English: Retrieve candidate headings, let the LLM choose only among them, then validate. Route low confidence to humans and log everything. Evaluate by chapter and cost-weighted error.
Hindi: Candidate headings retrieve करो, LLM को सिर्फ उन्हीं में से चुनने दो, फिर validate करो। कम confidence इंसान को भेजो और सब कुछ log करो। Chapter-wise और cost-weighted error से evaluate करो।

---

## ➡️ Next Topic
**537. Design: Customer Support AI**: intent routing, knowledge base answers and handoff to human agents.
