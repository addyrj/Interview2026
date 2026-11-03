---

# 509. LLM Selection for Production
# हिंदी में: Production के लिए LLM का चुनाव

---

## 🔵 Simple Definition (English)
LLM selection means choosing which model (or models) to use based on measured quality on your task, latency, cost, context length, privacy rules and reliability. The best leaderboard model is not always the best production choice.

## 🔵 सरल परिभाषा (Hindi)
LLM selection का मतलब है अपने task पर measured quality, latency, cost, context length, privacy rules और reliability के आधार पर model चुनना। Leaderboard का सबसे अच्छा model production के लिए हमेशा सबसे अच्छा नहीं होता।

---

## 🔴 Problem it Solves
Picking a model by hype leads to huge bills, slow responses, vendor lock-in or data-privacy problems. Models also change and get retired, so a selection process must be repeatable.

## 🔴 यह क्यों बना? (Hindi)
Hype देखकर model चुनने से बड़े bills, धीमे responses, vendor lock-in या privacy problems आते हैं। Models बदलते और बंद होते रहते हैं, इसलिए चुनाव की process दोहराने लायक होनी चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the task and hard constraints (data residency, max latency, budget)
Step 2 → Shortlist 3-5 candidates (small, mid, large; hosted and open-weight)
Step 3 → Build a golden eval set from real tasks (50-500 examples)
Step 4 → Run all candidates, measure quality, p50/p95 latency, cost per request
Step 5 → Choose the cheapest model that meets the quality bar
Step 6 → Add routing (small model first, escalate) and a fallback provider
Step 7 → Pin model versions, monitor, re-evaluate when new models arrive
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Task और hard constraints तय करो (data residency, latency, budget)
Step 2 → 3-5 candidates shortlist करो (small, mid, large; hosted और open-weight)
Step 3 → Real tasks से golden eval set बनाओ
Step 4 → सब चलाओ, quality, p50/p95 latency, cost per request मापो
Step 5 → Quality bar पार करने वाला सबसे सस्ता model चुनो
Step 6 → Routing और fallback provider जोड़ो
Step 7 → Version pin करो, monitor करो, नया model आने पर दोबारा evaluate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Extracting product attributes from invoices is easy: a small fast model hits 97% on the golden set. Final HS-code reasoning with conflicting notes needs a stronger model: 94% vs 88% for the small one. Design: small model for extraction and easy codes, strong model only when confidence is low or notes conflict, second provider as fallback for outages.
**Zomato-style example**: Review summarisation uses a small model; complaint-resolution reasoning uses a larger one.

## 🟡 Real Example Hindi mein
**Tariff System**: Invoice से attributes निकालना आसान है: छोटा तेज़ model golden set पर 97% देता है। Conflicting notes वाला final HS reasoning मज़बूत model माँगता है: 94% vs 88%। Design: extraction और आसान codes के लिए small model, कम confidence पर ही strong model, outage के लिए दूसरा provider।

---

## 💻 Code Example — Basic
```python
# Basic: pick the cheapest model that meets a quality bar (pure Python, offline)
candidates = [  # illustrative numbers, NOT real prices or scores
    {"name": "small", "quality": 0.88, "p95_ms": 700, "usd_per_1k_req": 0.4},
    {"name": "mid", "quality": 0.93, "p95_ms": 1500, "usd_per_1k_req": 2.0},
    {"name": "large", "quality": 0.95, "p95_ms": 3500, "usd_per_1k_req": 9.0},
]
bar, max_latency = 0.92, 2000  # requirements
ok = [c for c in candidates if c["quality"] >= bar and c["p95_ms"] <= max_latency]  # filter
best = min(ok, key=lambda c: c["usd_per_1k_req"]) if ok else None  # cheapest passing model
print("choice:", best["name"] if best else "none meets the bar")  # result: mid
```

## 💻 Code Example — Advanced
```python
# Advanced: async eval harness comparing candidate models on a golden set (mocked models)
import asyncio  # async runtime
import time  # latency measurement
from dataclasses import dataclass  # result record

GOLDEN = [("cotton shirt", "6109"), ("smartphone", "8517"), ("laptop", "8471")]  # (input, expected)


@dataclass
class Report:  # per-model result
    name: str  # model name
    accuracy: float  # fraction correct
    avg_ms: float  # mean latency


async def fake_model(name: str, text: str) -> str:  # mock; replace with real API call
    await asyncio.sleep(0.01 if name == "small" else 0.03)  # different speeds
    table = {"cotton shirt": "6109", "smartphone": "8517", "laptop": "8471"}  # perfect knowledge
    if name == "small" and text == "laptop":  # small model errs once
        return "8473"  # wrong
    return table[text]  # right


async def evaluate(name: str) -> Report:  # evaluate one model
    hits, times = 0, []  # counters
    for text, expected in GOLDEN:  # loop items
        t0 = time.perf_counter()  # start timer
        try:
            out = await asyncio.wait_for(fake_model(name, text), timeout=5)  # guarded call
        except asyncio.TimeoutError:  # failure counts as wrong
            out = ""  # empty answer
        times.append((time.perf_counter() - t0) * 1000)  # record ms
        hits += out == expected  # count match
    return Report(name, hits / len(GOLDEN), sum(times) / len(times))  # summary


async def main() -> None:  # run all in parallel
    for r in await asyncio.gather(*(evaluate(n) for n in ("small", "large"))):  # gather
        print(r)  # show


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Hide the choice behind a model-gateway function so you can switch models by config without redeploying clients. Return the model name for tracing.

```python
from fastapi import FastAPI, HTTPException  # app, errors
from pydantic import BaseModel  # schema

app = FastAPI()  # app
MODEL_BY_TIER = {"easy": "small-model", "hard": "large-model"}  # config (placeholder names)


class Q(BaseModel):  # request
    text: str  # question
    tier: str = "easy"  # difficulty hint


@app.post("/answer")  # route
async def answer(q: Q) -> dict[str, str]:
    model = MODEL_BY_TIER.get(q.tier)  # lookup
    if model is None:  # bad tier
        raise HTTPException(status_code=422, detail="unknown tier")  # validation error
    return {"model": model, "answer": "stub"}  # replace with real call
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `init_chat_model` and model classes make providers swappable, and `with_fallbacks` adds a backup model.

```python
from langchain_core.runnables import RunnableLambda  # offline stand-ins

primary = RunnableLambda(lambda x: (_ for _ in ()).throw(RuntimeError("primary down")))  # always fails
backup = RunnableLambda(lambda x: f"backup answered: {x}")  # works
chain = primary.with_fallbacks([backup])  # real LangChain API: fallback on exception
print(chain.invoke("HS code for laptop"))  # falls back to backup
# In production: ChatOpenAI(...).with_fallbacks([ChatAnthropic(...)])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing by public benchmarks only
✅ Correct: evaluate on your own golden set.
```python
# Wrong
model = top_of_leaderboard  # unrelated to your data
# Right
model = cheapest_that_passes(golden_set, bar=0.92)  # measured
```

❌ Mistake 2: Using an unpinned "latest" alias
✅ Correct: pin a dated version and re-run evals before upgrading.
```python
# Wrong
MODEL = "some-model-latest"  # behaviour can change silently
# Right
MODEL = "some-model-2025-01-01"  # pinned (illustrative name)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your provider silently updates the model and accuracy drops 4%. How do you prevent and detect this?"

**Answer**: Prevent by pinning versions, keeping an eval suite in CI, and a nightly canary run on the golden set. Detect with production quality sampling and alerts on output-format failures. Mitigate with a fallback provider and a one-config rollback.

---

## ⚫ Interview Questions + Answers

Q1: What factors drive model choice? (Easy)
A1: Quality on your task, latency, cost, context window, privacy/residency, tool-use and structured-output support, and reliability.

Q2: Why use a small model first? (Easy)
A2: It handles most easy queries at far lower cost and latency; escalate only hard ones.

Q3: Hosted API vs self-hosted open-weight? (Medium)
A3: Hosted: fast to start, no GPU ops, but per-token cost and data leaves your boundary. Self-hosted: control and privacy, cheaper at high steady volume, but you own GPUs, scaling and updates.

Q4: What is a model cascade? (Medium)
A4: Try a cheap model first, check confidence or a verifier, escalate to a stronger model if it fails.

Q5: How to design multi-provider failover? (Hard)
A5: Abstract providers behind one interface, normalise prompts and output schemas, health checks and circuit breakers, retry with backoff, then fallback with quality tests for each provider so the backup is actually acceptable.

---

## 🔷 When to Use + When Not to Use
✅ Use routing/cascades when:
- Mixed difficulty traffic and high volume

❌ Avoid when:
- Low volume where complexity costs more than the savings

---

## 📊 Visual Diagram
```
 request
   │
   ▼
 Small model ──confident?──yes──▶ answer
   │ no
   ▼
 Large model ──fails?──yes──▶ Fallback provider
   │ ok
   ▼
 answer   (all calls logged: model, tokens, latency, cost)
```

---

## 💰 Cost Impact
Cost per request = input tokens x input price + output tokens x output price; large models can be 10-30x costlier than small ones (illustrative; check current provider pricing). If 80% of traffic stays on the small model, the blended cost drops dramatically.
Optimise: cascades, prompt caching where supported, shorter prompts, `max_tokens` limits, batch APIs for offline jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Trusted eval examples | भरोसेमंद test set |
| Cascade | Cheap first, escalate | सस्ते से महँगे की ओर |
| Fallback | Backup model | बैकअप model |
| p95 latency | 95% faster than this | 95% requests इससे तेज़ |
| Open-weight | Downloadable model weights | खुले weights वाला model |
| Pinning | Fix model version | version स्थिर रखना |

---

## ⚡ 3-Line Summary
English: Choose models by your own evals, not hype: quality, latency, cost and constraints.
Use a cheap model first, escalate hard cases, and keep a fallback.
Pin versions and re-test before upgrades.
Hindi: Hype नहीं, अपने evals से model चुनो: quality, latency, cost, constraints।
पहले सस्ता model, कठिन cases पर escalate, और fallback रखो।
Version pin करो और upgrade से पहले दोबारा test करो।

---

## ➡️ Next Topic
**510. Embedding Model Selection** — the same selection discipline for the retrieval layer.
