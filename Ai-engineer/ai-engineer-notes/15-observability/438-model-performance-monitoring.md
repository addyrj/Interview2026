---

# 438. Model Performance Monitoring
# हिंदी में: Model Performance Monitoring

---

## 🔵 Simple Definition (English)
Model performance monitoring is tracking **how good the answers are** over time in production: accuracy against labels, groundedness (is the answer supported by retrieved text), format validity, user feedback, and regressions after prompt, model or data changes. It answers "is the AI still right?", not just "is the service up?".

## 🔵 सरल परिभाषा (Hindi)
Model performance monitoring का मतलब है production में समय के साथ **जवाब कितने अच्छे हैं** यह track करना: labels से accuracy, groundedness (जवाब retrieved text से समर्थित है या नहीं), format validity, user feedback, और prompt, model या data बदलने के बाद regressions। यह पूछता है "क्या AI अब भी सही है?", सिर्फ "क्या service चल रही है?" नहीं।

---

## 🔴 Problem it Solves
- Provider silently updates a model alias; behaviour shifts without any code change.
- Quality degrades slowly (new product types, new HS code revisions) and no alert fires.
- Offline benchmarks do not match live inputs.

## 🔴 यह क्यों बना? (Hindi)
- Provider चुपचाप model alias अपडेट कर देता है; code बदले बिना behaviour बदल जाता है।
- Quality धीरे-धीरे गिरती है (नए product types, HS code revisions) और कोई alert नहीं आता।
- Offline benchmark live inputs से मेल नहीं खाता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define quality metrics per task (exact match, heading match, groundedness, format ok)
Step 2 → Online signals: schema validity, confidence, validator agreement, user corrections, thumbs
Step 3 → Sample N% of traffic (more for low-confidence) into a review queue
Step 4 → Label by humans or LLM judge (calibrated against humans)
Step 5 → Compute rolling metrics per segment (language, chapter, customer) with confidence intervals
Step 6 → Run a fixed golden set on a schedule (canary) to detect provider-side model changes
Step 7 → Alert on significant drops; roll back prompt/model; add failures to the golden set
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर task के लिए quality metrics तय करो (exact match, heading match, groundedness, format ok)
Step 2 → Online signals: schema validity, confidence, validator सहमति, user corrections, thumbs
Step 3 → Traffic का N% sample review queue में डालो (low-confidence ज़्यादा)
Step 4 → इंसान या LLM judge (इंसानों से calibrated) label करे
Step 5 → Segment (भाषा, chapter, customer) के हिसाब से confidence interval के साथ rolling metrics
Step 6 → Fixed golden set को schedule पर चलाओ (canary) ताकि provider-side बदलाव पकड़ें
Step 7 → बड़ी गिरावट पर alert; prompt/model rollback; failures को golden set में जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Daily canary runs 100 golden products with `temperature=0`. On a Tuesday exact-match drops from 88% to 79% with no deploy; the provider updated the model alias. The team pins a dated snapshot, re-runs evals, and adjusts the prompt before upgrading deliberately. Another finding: Hindi-described products have 71% accuracy vs 90% for English, which is invisible in the overall average.

**Amazon-style**: review-summary feature monitors groundedness: every claim in the summary must appear in the source reviews.

## 🟡 Real Example Hindi mein
**Tariff System**: रोज़ canary 100 golden products `temperature=0` पर चलाता है। मंगलवार को deploy के बिना exact-match 88% से 79% हो गया; provider ने model alias अपडेट किया था। Team dated snapshot pin करती है, evals दोबारा चलाती है और सोच-समझकर upgrade करती है। दूसरा नतीजा: हिंदी में लिखे products की accuracy 71% है जबकि अंग्रेज़ी में 90%, जो overall average में छुप जाता है।

---

## 💻 Code Example — Basic
Rolling accuracy with segment breakdown and a simple drop alert (pure Python, run directly).

```python
# Rolling accuracy per segment + alert if it drops below a threshold
from collections import defaultdict, deque            # containers

WINDOW = 50                                           # last 50 labelled samples per segment
results: dict[str, deque[int]] = defaultdict(lambda: deque(maxlen=WINDOW))


def record(segment: str, correct: bool) -> None:
    results[segment].append(1 if correct else 0)      # 1 = correct, 0 = wrong


def accuracy(segment: str) -> float:
    d = results[segment]
    return sum(d) / len(d) if d else float("nan")     # nan when no data


def alerts(threshold: float = 0.85, min_n: int = 20) -> list[str]:
    out = []
    for seg, d in results.items():
        if len(d) >= min_n and accuracy(seg) < threshold:   # need enough samples
            out.append(f"{seg}: {accuracy(seg):.0%} (n={len(d)})")
    return out


for i in range(40):                                   # English: ~92% correct
    record("english", i % 12 != 0)
for i in range(40):                                   # Hindi: ~70% correct
    record("hindi", i % 10 not in (0, 3, 7))

print({s: round(accuracy(s), 2) for s in results})
print("ALERTS:", alerts())
```

## 💻 Code Example — Advanced
Scheduled canary runner with a golden set, tolerance and model-snapshot logging (async, typed, error handling).

```python
# Daily canary: run golden set, compare with last accepted score, flag regressions
import asyncio                                                # concurrency
import json                                                   # store results
import logging                                                # logs
from dataclasses import dataclass, asdict                     # records
from pathlib import Path                                      # file store
from typing import Optional

from openai import AsyncOpenAI                                # client

log = logging.getLogger("canary")
client = AsyncOpenAI()
STATE = Path("canary_state.json")                             # persists last accepted score
MODEL = "gpt-4o-mini-2024-07-18"                              # pinned snapshot (check current names)


@dataclass
class Golden:                                                 # golden example
    product: str
    hs_code: str


@dataclass
class CanaryResult:                                           # outcome
    model: str
    accuracy: float
    n: int
    regressed: bool


async def predict(product: str, sem: asyncio.Semaphore) -> Optional[str]:
    async with sem:                                           # limit concurrency (rate limits)
        try:
            r = await client.chat.completions.create(
                model=MODEL, temperature=0, max_tokens=20,
                messages=[{"role": "user", "content": f"HS code (NNNN.NN only) for: {product}"}],
            )
            return (r.choices[0].message.content or "").strip()
        except Exception as exc:                              # one failure must not kill the run
            log.warning("canary call failed: %s", exc)
            return None


async def run_canary(golden: list[Golden], tolerance: float = 0.03) -> CanaryResult:
    sem = asyncio.Semaphore(5)                                # 5 parallel calls
    preds = await asyncio.gather(*(predict(g.product, sem) for g in golden))
    correct = sum(p == g.hs_code for p, g in zip(preds, golden))
    acc = correct / len(golden)
    last = json.loads(STATE.read_text())["accuracy"] if STATE.exists() else None
    regressed = last is not None and acc < last - tolerance   # drop beyond tolerance
    if not regressed:
        STATE.write_text(json.dumps({"accuracy": acc, "model": MODEL}))  # accept new baseline
    res = CanaryResult(MODEL, acc, len(golden), regressed)
    log.info("canary %s", json.dumps(asdict(res)))
    return res
```

---

## 🟠 FastAPI Integration
Sampling hook: store a sample of requests for review (more when confidence is low), plus an endpoint to submit labels.

```python
# FastAPI: sample production answers into a review queue and accept labels
import random
import uuid
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
REVIEW_QUEUE: list[dict] = []                                  # use a DB table in production
LABELS: list[dict] = []


class Req(BaseModel):
    product: str


def should_sample(confidence: float) -> bool:
    rate = 0.30 if confidence < 0.6 else 0.05                  # review more when unsure
    return random.random() < rate


@app.post("/classify")
async def classify(req: Req) -> dict:
    code, conf = "8518.22", 0.55                               # replace with real pipeline
    rid = uuid.uuid4().hex
    if should_sample(conf):
        REVIEW_QUEUE.append({"id": rid, "product": req.product, "pred": code, "conf": conf})
    return {"hs_code": code, "confidence": conf, "request_id": rid}


class Label(BaseModel):
    request_id: str
    correct: bool


@app.post("/admin/label")
async def label(l: Label) -> dict:
    LABELS.append(l.model_dump())                               # feeds rolling accuracy job
    return {"ok": True}
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith, Langfuse and Phoenix attach evaluators to traces. In LangGraph add a "verify" node that scores groundedness, writes the score into state, and routes low scores to human review.

```python
# LangGraph: verify node routes low-confidence answers to human review
from typing import TypedDict
from langgraph.graph import StateGraph, END


class S(TypedDict):
    product: str
    code: str
    grounded: float


def classify(s: S) -> dict: return {"code": "8518.22"}
def verify(s: S) -> dict: return {"grounded": 0.9}             # replace with judge / validator
def route(s: S) -> str: return "ok" if s["grounded"] >= 0.8 else "review"


g = StateGraph(S)
g.add_node("classify", classify)
g.add_node("verify", verify)
g.add_node("review", lambda s: {})                             # human-in-the-loop placeholder
g.set_entry_point("classify")
g.add_edge("classify", "verify")
g.add_conditional_edges("verify", route, {"ok": END, "review": "review"})
g.add_edge("review", END)
app = g.compile()
print(app.invoke({"product": "speaker", "code": "", "grounded": 0.0}))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a floating alias like `gpt-4o-mini` in production without canaries
✅ Correct: pin a dated snapshot where available and run daily canaries.

```python
# Wrong: behaviour can change silently
model = "gpt-4o-mini"
# Right: pin, and upgrade on purpose after eval
model = "gpt-4o-mini-2024-07-18"
```

❌ Mistake 2: Reporting only the overall average
✅ Correct: break down by segment.

```python
# Wrong: overall 85% hides Hindi at 70%
# Right
for seg in ("english", "hindi", "chapter_85"):
    print(seg, accuracy(seg))
```

---

## 🧠 Tricky Interview Question
**Q**: "You have no ground-truth labels in production. How do you monitor accuracy?"

**Answer**: Use proxy signals plus sampling. Proxies: schema validity, validator/rule agreement (code exists in the tariff table), self-consistency (multiple samples agree), confidence calibration, retrieval score, user corrections and escalations. Then label a small stratified sample (humans or a calibrated LLM judge) to estimate true accuracy with confidence intervals, and use the proxies to decide which cases to sample. Track the correlation between proxies and true labels so you know when a proxy stops being reliable.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What is a golden set?
A1: A fixed, human-verified set of inputs and expected outputs used to measure quality repeatedly.

Q2 (Easy): What is a regression?
A2: A drop in quality after a change (prompt, model, data, provider update).

Q3 (Medium): What is groundedness?
A3: Whether each claim in the answer is supported by the retrieved context. Low groundedness signals hallucination.

Q4 (Medium): Why pin model versions?
A4: Aliases can point to new snapshots; pinning makes behaviour reproducible, and you upgrade only after running evals.

Q5 (Hard): How would you detect a quality drop quickly when labels arrive slowly?
A5: Use leading indicators (validator disagreement, low-confidence rate, refusal rate, correction rate, judge scores on a small sample) with statistical process control such as CUSUM or a two-proportion test versus baseline. Lagging labels then confirm. Keep the golden canary running as a cheap, fast detector of provider changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers have real consequences (customs, finance, health)
- Provider models change or your data changes often

❌ Avoid when:
- A prototype with no users; do manual spot checks instead
- Do not build an elaborate labelling pipeline for tasks with no definable "correct"

---

## 📊 Visual Diagram
```
 Production traffic ──> answer ──> proxies (schema, validator, confidence)
        │                                   │ low confidence -> higher sampling
        └──── 5% sample ──> review queue ──> labels (human / calibrated judge)
                                              │
 Golden canary (daily) ──────────────────────>│
                                              ▼
                       rolling accuracy by segment + CI
                                              │ drop > 3 pts
                                              ▼
                       alert -> rollback / pin model / add cases to golden set
```

---

## 💰 Cost Impact
- A canary of 100 items x about 150 tokens on gpt-4o-mini is roughly 15k tokens, about $0.003 per day. Very cheap.
- LLM-judge sampling at 5% of 1M requests = 50k judged requests; at about 500 tokens each that is 25M tokens, about $4 on a mini-tier judge. Human labelling is the larger cost: budget it.
- Optimise: sample smartly (low confidence), cache judge results, use small judges after calibration.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Verified test cases | Verified test cases का set |
| Canary | Small scheduled test in prod | Production में छोटा scheduled test |
| Regression | Quality drop after change | बदलाव के बाद गिरावट |
| Groundedness | Answer supported by sources | जवाब source से समर्थित |
| Segment | Slice of traffic | Traffic का हिस्सा |
| Snapshot pinning | Fixing an exact model version | Exact model version तय करना |
| Calibration | Confidence matches reality | Confidence का असलियत से मेल |

---

## ⚡ 3-Line Summary
English: Monitor answer quality, not just uptime: sample and label production traffic, run a daily golden canary, and slice metrics by segment. Pin model snapshots and alert on drops with enough samples. Feed failures back into the golden set.
Hindi: सिर्फ uptime नहीं, जवाबों की quality monitor करो: production traffic sample और label करो, रोज़ golden canary चलाओ और segment के हिसाब से metrics देखो। Model snapshot pin करो और पर्याप्त samples के साथ गिरावट पर alert लगाओ। Failures को golden set में वापस जोड़ो।

---

## ➡️ Next Topic
**439. Drift Detection** — spotting changes in input data, retrieval and model behaviour before accuracy visibly drops.
