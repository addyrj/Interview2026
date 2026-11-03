
---

# 505. Fine Tuning Best Practices
# हिंदी में: Fine Tuning की Best Practices

---

## 🔵 Simple Definition (English)
Fine-tuning best practices are the rules that decide whether tuning works: try cheaper options first, use small clean data, keep a frozen eval set, compare against a baseline, version everything, and roll out safely. Most failed fine-tunes fail because of bad data or no evaluation, not because of the algorithm.

## 🔵 सरल परिभाषा (Hindi)
Fine-tuning best practices वे नियम हैं जो तय करते हैं कि tuning काम करेगी या नहीं: पहले सस्ते विकल्प आज़माओ, छोटा पर साफ़ data रखो, frozen eval set रखो, baseline से तुलना करो, सब कुछ version करो और सुरक्षित rollout करो। ज़्यादातर fine-tunes data की गड़बड़ी या eval न होने से fail होते हैं।

---

## 🔴 Problem it Solves
Teams fine-tune with noisy labels, no baseline and no regression checks. The result is a model that looks better in a demo but is worse in production, costs more, and cannot be rolled back. Best practices turn tuning from a gamble into a repeatable engineering process.

## 🔴 यह क्यों बना? (Hindi)
Teams noisy labels, बिना baseline और बिना regression check के fine-tune करती हैं। नतीजा: demo में अच्छा पर production में खराब, महँगा और rollback नामुमकिन model। Best practices tuning को जुआ से repeatable engineering बना देती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define success: metric + target (e.g. HS exact match >= 85%, JSON valid 99.5%)
Step 2 → Try prompt + RAG first; fine-tune only for the remaining gap
Step 3 → Data quality > quantity: dedupe, fix labels, double-review a sample
Step 4 → Freeze a golden test set before touching training data
Step 5 → Start small (a few hundred examples), measure, then scale the data
Step 6 → Use defaults for hyper-parameters; change one thing at a time
Step 7 → Watch validation loss; fewer epochs if it rises (over-fitting)
Step 8 → Evaluate vs baseline + regression set + safety/abstain checks
Step 9 → Version data, config and model; shadow, canary, then promote; keep rollback
Step 10 → Monitor drift and schedule re-training
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Success तय करो: metric + target (जैसे HS exact match >= 85%)
Step 2 → पहले prompt + RAG; बचा gap हो तभी fine-tune
Step 3 → Quality > quantity: duplicates हटाओ, labels सुधारो, sample double-review
Step 4 → Training data छूने से पहले golden test set freeze करो
Step 5 → कुछ सौ examples से शुरू करो, मापो, फिर बढ़ाओ
Step 6 → Hyper-parameters default रखो; एक बार में एक चीज़ बदलो
Step 7 → Validation loss बढ़े तो epochs कम करो (over-fitting)
Step 8 → Baseline + regression set + safety checks से evaluate
Step 9 → Data, config, model version करो; shadow, canary, फिर promote; rollback रखो
Step 10 → Drift monitor करो और periodic re-training रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: v1 used 600 clean examples and reached 79% exact match; the team doubled the data with 600 noisy auto-labelled rows and accuracy fell to 76% because the new labels disagreed on chapter 85 vs 90 items. They cleaned labels (inter-annotator agreement check), accuracy went to 84%. Every model is tagged `tariff-v3` with its data hash.

**Zomato AI**: A tuned reply-tone model was canaried on 5% of chats; complaint-escalation rate was watched before full rollout.

## 🟡 Real Example Hindi mein
**Tariff System**: v1 में 600 साफ़ examples से 79% exact match। टीम ने 600 noisy auto-label rows जोड़े तो accuracy 76% हो गई क्योंकि labels आपस में टकराते थे। Labels साफ़ करने (annotator agreement) के बाद 84%। हर model पर data hash के साथ `tariff-v3` जैसा tag है।

**Zomato AI**: Tone model को पहले 5% chats पर canary किया, escalation rate देखकर ही पूरा rollout।

---

## 💻 Code Example — Basic
```python
# Pure Python: data-quality checks you should run BEFORE every fine-tune
import json  # parse rows
from collections import Counter  # count duplicates / label conflicts

rows = [  # pretend training rows
    {"desc": "cotton t-shirt", "hs": "6109.10"},
    {"desc": "Cotton T-Shirt ", "hs": "6109.10"},   # duplicate after normalising
    {"desc": "bluetooth headphones", "hs": "8518.30"},
    {"desc": "bluetooth headphones", "hs": "8517.62"},  # conflicting label for same input
    {"desc": "", "hs": "0000.00"},  # empty input
]

def norm(s: str) -> str:
    """Normalise text for comparison."""
    return " ".join(s.lower().split())  # lowercase and collapse spaces

seen: Counter = Counter(norm(r["desc"]) for r in rows)  # how often each input appears
labels: dict[str, set[str]] = {}  # input -> set of labels
for r in rows:  # collect labels per input
    labels.setdefault(norm(r["desc"]), set()).add(r["hs"])

empty = [r for r in rows if not norm(r["desc"])]  # rows with no input
dups = [k for k, c in seen.items() if c > 1 and k]  # repeated inputs
conflicts = [k for k, v in labels.items() if len(v) > 1 and k]  # same input, different labels

print("empty rows   :", len(empty))      # 1
print("duplicates   :", dups)            # ['cotton t-shirt', 'bluetooth headphones']
print("label conflicts:", conflicts)     # ['bluetooth headphones']
```

## 💻 Code Example — Advanced
```python
# Production: gate a candidate model on golden-set metrics before promotion (async, typed, safe)
import asyncio  # concurrency
import json  # parse model output
import logging  # logs
from dataclasses import dataclass  # result container
from typing import Awaitable, Callable  # types

log = logging.getLogger("gate")  # logger
Predict = Callable[[str], Awaitable[str]]  # async predictor returning raw JSON text

@dataclass(frozen=True)
class Report:
    exact: float        # exact HS match rate
    valid_json: float   # share of parseable outputs
    abstain: float      # share flagged needs_review

async def evaluate(predict: Predict, golden: list[dict], conc: int = 8) -> Report:
    """Score a model on the frozen golden set."""
    sem = asyncio.Semaphore(conc)  # limit concurrency

    async def one(row: dict) -> tuple[bool, bool, bool]:
        async with sem:  # throttle
            try:
                raw = await predict(row["desc"])  # call model
                data = json.loads(raw)  # parse JSON
            except (json.JSONDecodeError, Exception) as exc:  # parse or API failure
                log.warning("bad output: %s", exc)  # log
                return (False, False, False)  # count as total miss
        return (data.get("hs_code") == row["hs"], True, bool(data.get("needs_review")))  # flags

    res = await asyncio.gather(*(one(r) for r in golden))  # run all
    n = max(len(res), 1)  # avoid divide by zero
    return Report(sum(r[0] for r in res) / n, sum(r[1] for r in res) / n, sum(r[2] for r in res) / n)

def should_promote(new: Report, old: Report) -> bool:
    """Promotion rules: better accuracy, near-perfect JSON, abstain not exploding."""
    return (
        new.exact >= old.exact + 0.01      # at least +1 point
        and new.valid_json >= 0.995        # format reliability
        and new.abstain <= old.abstain + 0.05  # not abstaining on everything
    )

async def _old(d: str) -> str: return json.dumps({"hs_code": "8518.30", "needs_review": False})  # stub
async def _new(d: str) -> str: return json.dumps({"hs_code": "8518.30", "needs_review": False})  # stub

if __name__ == "__main__":
    gold = [{"desc": "headphones", "hs": "8518.30"}] * 10  # tiny golden set
    old = asyncio.run(evaluate(_old, gold))  # baseline report
    new = asyncio.run(evaluate(_new, gold))  # candidate report
    print(old, new, "promote:", should_promote(new, old))  # equal scores -> False
```

---

## 🟠 FastAPI Integration
Serve versioned models and route a small share of traffic to the candidate (canary), returning the version so every answer is traceable.

```python
import random  # canary sampling
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema

app = FastAPI()  # app
STABLE, CANARY = "tariff-v3", "tariff-v4"  # model versions
CANARY_SHARE = 0.05  # 5% of traffic

class Req(BaseModel):
    description: str  # product text

async def call_model(version: str, text: str) -> str:
    return f"[{version}] answer for: {text}"  # stub; replace with a real call

@app.post("/classify")
async def classify(req: Req) -> dict:
    """Route by canary share and report the version used."""
    version = CANARY if random.random() < CANARY_SHARE else STABLE  # pick version
    answer = await call_model(version, req.description)  # run it
    return {"model_version": version, "answer": answer}  # traceable response
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith datasets hold your golden set, and LangSmith evaluators can run each candidate model against it with traces for debugging. In LangGraph, make the model name a config value so the same graph runs the stable and canary versions.

```python
from langchain_openai import ChatOpenAI  # chat model

def make_llm(version_model: str) -> ChatOpenAI:
    """Build the LLM from a configurable model id (stable or candidate)."""
    return ChatOpenAI(model=version_model, temperature=0)  # deterministic

stable = make_llm("gpt-4o-mini")  # baseline
# candidate = make_llm("ft:gpt-4o-mini-2024-07-18:acme:tariff-v4:xyz")  # illustrative id
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Training on the test set
✅ Correct: Freeze the golden set first.
```python
# Wrong: golden = random sample of all_rows; train = all_rows
# Right: golden, train = split_by_group(all_rows); never add golden to train
```

❌ Mistake 2: Changing many things at once
✅ Correct: One change per experiment, log results.
```python
# Wrong: new data + new base model + new epochs  -> cannot tell what helped
# Right: run A: data only; run B: epochs only; compare to the same golden set
```

❌ Mistake 3: Skipping the regression check
✅ Correct: Re-test general abilities (JSON, refusal, other languages) so tuning did not break them.

---

## 🧠 Tricky Interview Question

**Q**: "Your fine-tuned model reaches 99% training accuracy and 70% golden accuracy. A teammate says train longer. What do you say?"

**Answer**: That gap shows over-fitting (memorising), so more epochs makes it worse. Reduce epochs or learning-rate multiplier, add more diverse and cleaner data, remove near-duplicates, use a validation file for early stopping, and consider a smaller adapter (LoRA) or a simpler task. Also check label noise: a model that learns inconsistent labels will memorise them.

---

## ⚫ Interview Questions + Answers

Q1: Why start with prompting and RAG?
A1: They are cheap, fast to iterate and reversible. Fine-tuning is only needed for the gap they cannot close.

Q2: Why is a frozen golden set important?
A2: It gives a fair, repeatable score across all experiments and prevents fooling yourself with data leakage.

Q3: What signs show over-fitting?
A3: Training loss keeps falling while validation loss rises, and the golden score is far below training accuracy.

Q4: Data quality or quantity?
A4: Quality first. A few hundred consistent examples often beat thousands of noisy ones; scale after labels agree.

Q5: Describe a safe rollout and rollback plan.
A5: Version data/config/model, run offline gate metrics, shadow the candidate on live traffic, canary to 5%, monitor accuracy proxies, latency, cost and escalations, then promote gradually. Keep the previous model id deployable and make routing a config flag so rollback takes seconds.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Gap is behaviour/format/style/latency and you have clean labelled data
- You can measure success with an eval set

❌ Avoid when:
- Missing facts only (use RAG)
- No owner to maintain data and retraining
- Compliance forbids sending the data to a vendor and you cannot self-host

---

## 📊 Visual Diagram
```
 Goal+metric ─► Prompt/RAG baseline ─► gap left? ─no─► stop
                                         │yes
                                         ▼
 clean data ─► freeze golden ─► small tune ─► eval vs baseline
        ▲                                         │ pass
        └── fix data / change 1 thing ◄───────────┤ fail
                                                  ▼
                      shadow ─► canary 5% ─► promote ─► monitor ─► retrain
                                   │
                                   └──── rollback (flag)
```

---

## 💰 Cost Impact
Costs to track: training tokens (examples x tokens x epochs), higher per-token inference price for hosted tuned models (check current pricing; numbers vary), and evaluation calls. Every failed experiment costs tokens, so small pilots (200-500 examples) are the cheapest way to learn.
Optimise: dedupe data, cap epochs (2-4), shorten prompts after tuning (often saves hundreds of input tokens per call), use `max_tokens`, cache repeated inputs, run evals on a sampled golden set during iteration and the full set only before release, and delete unused fine-tuned model endpoints.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Over-fitting | Memorises training data | Training data रट लेना |
| Golden set | Frozen trusted test set | Freeze किया हुआ test set |
| Regression | Old skill gets worse | पुरानी skill खराब होना |
| Label noise | Wrong/inconsistent labels | गलत/असंगत labels |
| Early stopping | Stop when validation worsens | Validation बिगड़े तो रुकना |
| Canary | Small live traffic test | थोड़े live traffic पर test |
| Rollback | Return to previous version | पिछले version पर लौटना |

---

## ⚡ 3-Line Summary
English: Define a metric, try prompt and RAG first, and fine-tune with small, clean, deduplicated data. Freeze a golden set, change one thing at a time and gate on baseline and regression checks. Roll out with shadow and canary, and keep a rollback.
Hindi: Metric तय करो, पहले prompt और RAG आज़माओ, फिर छोटे, साफ़, deduplicated data से fine-tune करो। Golden set freeze करो, एक बार में एक चीज़ बदलो और baseline व regression checks से gate करो। Shadow और canary से rollout करो, rollback तैयार रखो।

---

## ➡️ Next Topic
**340. LangGraph Best Practices** — the same engineering discipline (state design, testing, safe rollout) applied to agent graphs.
