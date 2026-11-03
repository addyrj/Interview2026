---

# 483. Responsible AI Principles
# हिंदी में: Responsible AI के सिद्धांत

---

## 🔵 Simple Definition (English)
Responsible AI is a set of rules for building AI that is fair, safe, private, transparent and accountable. It turns "do the right thing" into checks you can test in code. Common pillars: fairness, reliability/safety, privacy/security, transparency, accountability, human oversight.

## 🔵 सरल परिभाषा (Hindi)
Responsible AI वो नियम हैं जिनसे AI fair, safe, private, transparent और accountable बनता है। "सही काम करो" को code में test होने वाले checks में बदला जाता है। मुख्य pillars: fairness, safety, privacy, transparency, accountability, human oversight।

---

## 🔴 Problem it Solves
Without principles, teams ship models that leak PII, discriminate, hallucinate confidently or cannot be explained to an auditor. Regulators (for example the EU AI Act) and enterprise customers now ask for proof. Principles give a shared checklist before launch.

## 🔴 यह क्यों बना? (Hindi)
Principles के बिना model PII leak करता है, भेदभाव करता है, confidently गलत बोलता है और auditor को explain नहीं हो पाता। Regulators और enterprise customers अब proof माँगते हैं। Principles launch से पहले एक common checklist देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick principles for your product (fairness, privacy, safety, transparency, accountability)
Step 2 → Turn each principle into a measurable check (e.g. PII leak rate = 0)
Step 3 → Put checks in the pipeline (input guard, output guard, audit log)
Step 4 → Add human review for high-risk decisions
Step 5 → Log every decision with model version + reason
Step 6 → Monitor metrics in production, review regularly
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → अपने product के लिए principles चुनो
Step 2 → हर principle को measurable check बनाओ
Step 3 → Pipeline में checks लगाओ (input guard, output guard, audit log)
Step 4 → High-risk decision में human review जोड़ो
Step 5 → हर decision log करो (model version + reason)
Step 6 → Production में metrics monitor करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The LLM suggests an HS code for a shipment. A wrong code means a wrong customs duty, which is a legal and money risk. Responsible design: show the cited tariff rule (transparency), send low-confidence cases to a customs officer (human oversight), mask importer PII in logs (privacy), store model version and prompt for each decision (accountability), and check that accuracy is similar across product categories and countries (fairness).
**Zomato-style example**: A delivery-time AI must not give systematically worse ETAs or fewer orders to some areas.

## 🟡 Real Example Hindi mein
**Tariff System**: LLM HS code suggest करता है। गलत code = गलत duty = legal और पैसे का risk। इसलिए: cited rule दिखाओ (transparency), low-confidence case customs officer को भेजो (human oversight), logs में importer PII mask करो (privacy), हर decision में model version store करो (accountability), और अलग-अलग categories/countries में accuracy बराबर check करो (fairness)।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny responsible-AI checklist evaluator (pure Python, runs offline)
from dataclasses import dataclass  # dataclass gives a clean record type


@dataclass
class Check:  # one principle -> one testable check
    principle: str  # name of the principle
    passed: bool  # did the system satisfy it?
    note: str  # short reason


def evaluate(system: dict[str, bool]) -> list[Check]:  # system flags in, checks out
    rules = {  # map each principle to the flag that proves it
        "transparency": "shows_sources",  # answer cites sources
        "privacy": "masks_pii",  # PII is masked in logs
        "accountability": "logs_decisions",  # every decision is logged
        "human_oversight": "human_review_low_conf",  # low confidence goes to a human
        "fairness": "fairness_tested",  # parity metrics were measured
    }
    results: list[Check] = []  # collect results here
    for principle, flag in rules.items():  # loop over each principle
        ok = bool(system.get(flag, False))  # missing flag counts as failed
        results.append(Check(principle, ok, f"{flag}={ok}"))  # store the result
    return results  # return all checks


if __name__ == "__main__":  # run directly
    tariff_system = {"shows_sources": True, "masks_pii": True, "logs_decisions": True,
                     "human_review_low_conf": True, "fairness_tested": False}  # sample system
    for c in evaluate(tariff_system):  # print each check
        print(("PASS" if c.passed else "FAIL"), c.principle, "-", c.note)  # PASS/FAIL line
    print("Launch allowed:", all(c.passed for c in evaluate(tariff_system)))  # gate on all passing
```

## 💻 Code Example — Advanced
```python
# Advanced: async responsible-AI gate with audit log, human escalation, error handling
import asyncio  # async runtime
import json  # audit records as JSON
import re  # simple PII regex
import time  # timestamps
from dataclasses import dataclass, asdict  # records

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")  # naive email pattern (illustrative)


@dataclass
class Decision:  # audit record for each AI decision
    request_id: str  # unique id
    hs_code: str  # model suggestion
    confidence: float  # model confidence 0..1
    needs_human: bool  # escalated or not
    model_version: str  # which model produced it
    ts: float  # unix time


def mask_pii(text: str) -> str:  # privacy principle
    return EMAIL.sub("[EMAIL]", text)  # replace emails with a placeholder


async def mock_llm(description: str) -> tuple[str, float]:  # stand-in for a real LLM call
    await asyncio.sleep(0.01)  # simulate network latency
    if "phone" in description.lower():  # toy rule
        return "8517.13", 0.93  # confident answer
    return "9999.99", 0.40  # unsure answer


async def classify(request_id: str, description: str, threshold: float = 0.75) -> Decision:
    safe_text = mask_pii(description)  # never log raw PII
    try:  # guard the model call
        code, conf = await asyncio.wait_for(mock_llm(safe_text), timeout=5)  # timeout = reliability
    except asyncio.TimeoutError:  # model too slow
        code, conf = "UNKNOWN", 0.0  # fail safe, not fail silent
    d = Decision(request_id, code, conf, conf < threshold, "mock-v1", time.time())  # build record
    print(json.dumps(asdict(d)))  # audit log line (use a real log sink in prod)
    return d  # return the decision


if __name__ == "__main__":
    print(asyncio.run(classify("r1", "smart phone from a@b.com")))  # confident path
    print(asyncio.run(classify("r2", "strange item")))  # escalated path
```

---

## 🟠 FastAPI Integration
Put responsible-AI checks as dependencies/middleware so every route gets them. Return the confidence and a `needs_human_review` flag so the client can show a review banner.

```python
from fastapi import FastAPI, HTTPException  # FastAPI app + errors
from pydantic import BaseModel, Field  # request validation

app = FastAPI()  # app instance


class Req(BaseModel):  # request body
    description: str = Field(min_length=3, max_length=2000)  # limit input size


class Resp(BaseModel):  # response body
    hs_code: str  # suggestion
    confidence: float  # transparency
    needs_human_review: bool  # oversight flag
    sources: list[str]  # citations


@app.post("/classify", response_model=Resp)  # route
async def classify_route(req: Req) -> Resp:  # async handler
    try:  # error handling
        code, conf = "8517.13", 0.9  # replace with real LLM/RAG call
    except Exception as exc:  # never leak internals
        raise HTTPException(status_code=502, detail="model_error") from exc  # clean error
    return Resp(hs_code=code, confidence=conf, needs_human_review=conf < 0.75,
                sources=["HS Chapter 85 note 3"])  # return with transparency fields
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph fits human oversight well: add a conditional edge that routes low-confidence results to a human node and use `interrupt` with a checkpointer to pause for approval. LangSmith traces give the audit trail (accountability).

```python
# LangGraph sketch (API names are real; wiring is simplified)
from langgraph.graph import StateGraph, END  # graph builder
from typing import TypedDict  # state type


class S(TypedDict):  # graph state
    confidence: float  # model confidence
    decision: str  # final decision


def route(state: S) -> str:  # conditional edge function
    return "human" if state["confidence"] < 0.75 else "auto"  # oversight rule


g = StateGraph(S)  # create graph
g.add_node("auto", lambda s: {"decision": "approved"})  # auto path
g.add_node("human", lambda s: {"decision": "pending_review"})  # human path
g.set_conditional_entry_point(route, {"auto": "auto", "human": "human"})  # branch at start
g.add_edge("auto", END)  # finish
g.add_edge("human", END)  # finish
app = g.compile()  # runnable graph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating ethics as a document, not code
✅ Correct: make each principle a test that blocks release.
```python
# Wrong
# "We care about fairness" in a slide deck, no test.
# Right
assert fairness_gap <= 0.05, "release blocked: fairness gap too large"  # enforced in CI
```

❌ Mistake 2: Logging raw user data for "accountability"
✅ Correct: log ids, model version and masked text only.
```python
# Wrong
logger.info(f"user said: {raw_text}")  # leaks PII
# Right
logger.info("req=%s text=%s", req_id, mask_pii(raw_text))  # masked
```

---

## 🧠 Tricky Interview Question
**Q**: "Your model is 95% accurate overall. Is it responsible to ship?"

**Answer**: Not automatically. Overall accuracy can hide a bad subgroup (for example 99% on electronics but 70% on textiles from one country). Also check calibration, PII handling, explainability, failure behaviour and whether high-impact cases have human review. Responsible means measured per group, with logging and fallback, not one headline number.

---

## ⚫ Interview Questions + Answers

Q1: Name the main Responsible AI principles. (Easy)
A1: Fairness, reliability and safety, privacy and security, transparency, accountability, inclusiveness, and human oversight. Different companies word them slightly differently.

Q2: What is human-in-the-loop? (Easy)
A2: A design where a person reviews or approves AI output, usually for low-confidence or high-impact cases, so the AI does not act alone.

Q3: How do you make "transparency" concrete in an LLM app? (Medium)
A3: Return citations to retrieved sources, show confidence, tell users when content is AI generated, and keep a decision log with model and prompt versions.

Q4: How do you balance privacy and accountability? (Medium)
A4: Log what you need to reproduce a decision, but mask or hash PII, set retention limits, restrict access, and store raw data only where law and purpose allow.

Q5: Design a governance process for a customs-classification AI. (Hard)
A5: Risk-classify the use case (high impact), define metrics per principle, run pre-release evals including per-group accuracy and red-team tests, add input/output guardrails, route low-confidence to officers, keep immutable audit logs, monitor drift, provide appeal path for users, and review on a schedule with an owner named for each metric.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Decisions affect money, legal status, jobs, health or access
- Selling to enterprises or regulated markets
- Handling personal data

❌ Avoid heavy process when:
- Throwaway prototypes with no real users or data (still keep basic safety)

---

## 📊 Visual Diagram
```
 User request
     │
     ▼
┌──────────────┐   PII masked
│ Input guard  │──────────────┐
└──────┬───────┘              │
       ▼                      ▼
┌──────────────┐        ┌───────────┐
│   LLM / RAG  │───────▶│ Audit log │
└──────┬───────┘        └───────────┘
       ▼
┌──────────────┐  low conf   ┌─────────────┐
│ Output guard │────────────▶│ Human review│
└──────┬───────┘             └─────────────┘
       ▼
   Answer + sources + confidence
```

---

## 💰 Cost Impact
Guardrails add tokens and latency: an LLM-as-judge safety check can add roughly the same input tokens again (illustrative: 1,000 extra input tokens per request). Audit logs add storage cost. Human review costs staff time.
Optimise: use regex/rules first (free), small classifiers for safety instead of big LLM judges, sample-based evaluation (check 5% of traffic), and escalate to humans only below a threshold. Count tokens before and after adding checks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fairness | Similar quality across groups | सबके लिए बराबर quality |
| Transparency | Explain and cite how answer was made | पारदर्शिता |
| Accountability | Someone owns the outcome and logs exist | जवाबदेही |
| Human-in-the-loop | Human approves risky outputs | इंसान की निगरानी |
| Audit log | Record of decisions | decisions का record |
| PII | Personal identifiable information | निजी जानकारी |

---

## ⚡ 3-Line Summary
English: Responsible AI turns values into tests: fairness, privacy, transparency, accountability, oversight.
Put checks in the pipeline, log decisions, and send risky cases to humans.
Measure per group, not just overall accuracy.
Hindi: Responsible AI values को tests में बदलता है: fairness, privacy, transparency, accountability, oversight।
Pipeline में checks लगाओ, decisions log करो, risky cases इंसान को भेजो।
सिर्फ overall accuracy नहीं, group-wise measure करो।

---

## ➡️ Next Topic
**484. Bias Detection** — how to actually measure unfairness in model outputs.
