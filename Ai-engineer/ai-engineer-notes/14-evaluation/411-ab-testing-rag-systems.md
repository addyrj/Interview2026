---

# 411. A/B Testing RAG Systems
# हिंदी में: RAG Systems की A/B Testing

---

## 🔵 Simple Definition (English)
A/B testing a RAG system means serving two versions (A = current, B = new retriever, prompt, or model) to different random groups of real users at the same time, then comparing a success metric (thumbs-up rate, resolution rate, accuracy) with a statistical test to decide if B is truly better.

## 🔵 सरल परिभाषा (Hindi)
RAG system की A/B testing में दो versions (A = मौजूदा, B = नया retriever, prompt या model) एक ही समय पर असली users के अलग-अलग random groups को दिखाए जाते हैं, फिर success metric (thumbs-up rate, resolution rate, accuracy) की statistical test से तुलना करके तय होता है कि B सच में बेहतर है या नहीं।

---

## 🔴 Problem it Solves
Offline eval datasets never perfectly match live traffic. A change that wins offline can lose online (latency, tone, new query types). A/B testing measures real user impact and protects against shipping regressions to everyone.

## 🔴 यह क्यों बना? (Hindi)
Offline eval datasets live traffic से पूरी तरह नहीं मिलते। जो बदलाव offline जीतता है वह online हार सकता है (latency, tone, नए query types)। A/B testing असली user impact नापती है और सब users को regression जाने से बचाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Hypothesis: "Reranker (B) raises correct-answer rate by 3 points"
Step 2 → Pick primary metric + guardrails (latency, cost, error rate)
Step 3 → Compute required sample size (power analysis)
Step 4 → Assign users to A/B deterministically (hash of user_id), e.g. 50/50 or 90/10
Step 5 → Log variant, query, answer, feedback, latency, tokens
Step 6 → Run until sample size reached (do not peek and stop early)
Step 7 → Statistical test (two-proportion z-test / bootstrap), check guardrails
Step 8 → Ship, iterate, or roll back
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Hypothesis: "Reranker (B) सही-जवाब दर 3 points बढ़ाएगा"
Step 2 → Primary metric + guardrails चुनो (latency, cost, error rate)
Step 3 → ज़रूरी sample size निकालो (power analysis)
Step 4 → Users को deterministic तरीके से A/B में बाँटो (user_id का hash), जैसे 50/50 या 90/10
Step 5 → Variant, query, answer, feedback, latency, tokens log करो
Step 6 → Sample size पूरा होने तक चलाओ (बीच में झाँककर जल्दी बंद मत करो)
Step 7 → Statistical test (two-proportion z-test / bootstrap), guardrails जाँचो
Step 8 → Ship, सुधारो या rollback
```

---

## 🟡 Real World Example
**Tariff Classification System**: A = hybrid search (BM25 + vectors), B = hybrid + cross-encoder reranker. Brokers click "code accepted" or "edited code". Primary metric: acceptance rate. Guardrail: p95 latency < 3 s. After 2,000 queries per arm: A 78.0%, B 81.5% (p = 0.01) but latency +0.6 s, still under the guardrail, so B ships.

**Amazon-style**: Product-QA bot with two prompts; metric is "helpful" votes plus add-to-cart rate.

## 🟡 Real Example Hindi mein
**Tariff System**: A = hybrid search (BM25 + vectors), B = hybrid + cross-encoder reranker। Brokers "code accepted" या "edited code" दबाते हैं। Primary metric: acceptance rate। Guardrail: p95 latency < 3 s। हर arm में 2,000 queries के बाद: A 78.0%, B 81.5% (p = 0.01) पर latency +0.6 s, guardrail के अंदर, इसलिए B ship हुआ।

**Amazon-style**: Product-QA bot के दो prompts; metric "helpful" votes और add-to-cart rate।

---

## 💻 Code Example — Basic
```python
# Basic: two-proportion z-test for an A/B result (pure Python, offline)
import math  # sqrt, erf


def z_test(success_a: int, n_a: int, success_b: int, n_b: int) -> tuple[float, float]:
    """Return (z, two-sided p-value) for difference in proportions."""
    if min(n_a, n_b) == 0:  # no data guard
        raise ValueError("both arms need data")  # clear error
    p_a, p_b = success_a / n_a, success_b / n_b  # observed rates
    pooled = (success_a + success_b) / (n_a + n_b)  # pooled rate under H0
    se = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))  # standard error
    if se == 0:  # all successes or all failures
        raise ValueError("zero variance")  # cannot test
    z = (p_b - p_a) / se  # test statistic
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))  # normal tail probability
    return z, p  # statistic and p-value


z, p = z_test(1560, 2000, 1630, 2000)  # A=78.0%, B=81.5%
print(f"z={z:.2f} p={p:.4f}")  # p about 0.01 -> significant at 5%
```

## 💻 Code Example — Advanced
```python
# Advanced: deterministic async A/B router with logging, fallback and guardrail summary
import asyncio  # async
import hashlib  # stable bucketing
import logging  # logs
import time  # latency
from collections import defaultdict  # per-arm stats
from typing import Awaitable, Callable  # types

log = logging.getLogger("ab")  # logger
RagFn = Callable[[str], Awaitable[str]]  # signature of a RAG pipeline


def bucket(user_id: str, experiment: str, split_b: float = 0.5) -> str:
    h = hashlib.sha256(f"{experiment}:{user_id}".encode()).hexdigest()  # stable hash
    frac = int(h[:8], 16) / 0xFFFFFFFF  # map to [0,1]
    return "B" if frac < split_b else "A"  # same user always same arm


class Experiment:
    def __init__(self, name: str, a: RagFn, b: RagFn, split_b: float = 0.5) -> None:
        self.name, self.fns, self.split = name, {"A": a, "B": b}, split_b  # config
        self.stats: dict[str, dict[str, list[float]]] = {
            "A": defaultdict(list), "B": defaultdict(list)}  # per-arm metrics

    async def answer(self, user_id: str, q: str) -> tuple[str, str]:
        arm = bucket(user_id, self.name, self.split)  # choose arm
        t0 = time.perf_counter()  # start timer
        try:
            out = await asyncio.wait_for(self.fns[arm](q), timeout=15)  # run with timeout
        except Exception as exc:  # B failing must not hurt the user
            log.error("arm %s failed: %s", arm, exc)  # log
            self.stats[arm]["errors"].append(1.0)  # count error
            out = await self.fns["A"](q)  # fall back to control
        self.stats[arm]["latency"].append(time.perf_counter() - t0)  # record latency
        return out, arm  # answer + arm for logging

    def feedback(self, arm: str, success: bool) -> None:
        self.stats[arm]["success"].append(1.0 if success else 0.0)  # user feedback

    def summary(self) -> dict:
        res: dict[str, dict] = {}  # output
        for arm, s in self.stats.items():
            n = len(s["success"])  # feedback count
            lat = sorted(s["latency"])  # latencies
            res[arm] = {"n": n, "rate": round(sum(s["success"]) / n, 3) if n else None,
                        "p95_latency": round(lat[int(0.95 * (len(lat) - 1))], 3) if lat else None,
                        "errors": len(s["errors"])}  # per-arm summary
        return res
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # validation

app = FastAPI()  # app


async def rag_a(q: str) -> str:  # control pipeline stub
    return f"A: {q}"


async def rag_b(q: str) -> str:  # candidate pipeline stub
    return f"B: {q}"


exp = Experiment("reranker-test", rag_a, rag_b, split_b=0.1)  # 10% canary to B


class Ask(BaseModel):  # request
    user_id: str
    question: str


class Fb(BaseModel):  # feedback request
    arm: str
    success: bool


@app.post("/ask")  # serve answers
async def ask(r: Ask) -> dict:
    answer, arm = await exp.answer(r.user_id, r.question)  # route
    return {"answer": answer, "arm": arm}  # include arm so feedback can reference it


@app.post("/feedback")  # collect thumbs
async def feedback(f: Fb) -> dict:
    if f.arm not in ("A", "B"):  # validate
        raise HTTPException(400, "arm must be A or B")
    exp.feedback(f.arm, f.success)  # store
    return {"ok": True}


@app.get("/experiment")  # dashboard data
async def experiment() -> dict:
    return exp.summary()
```

---

## 🔗 LangChain / LangGraph Connection
With LCEL you can build two chains and pick one with `RunnableBranch` or a simple router; tag runs with the variant in metadata so LangSmith can filter and compare. In LangGraph, put the variant in graph config and route to different retrieval nodes.

```python
# Tag runs by arm so LangSmith can compare A/B (chain_a, chain_b are LCEL chains)
def run_variant(arm: str, question: str, chain_a, chain_b) -> str:
    chain = chain_b if arm == "B" else chain_a  # choose chain
    return chain.invoke({"question": question},
                        config={"tags": [f"arm:{arm}"], "metadata": {"experiment": "reranker-test"}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Random assignment per request (same user sees both versions)
✅ Correct: hash user_id

```python
# Wrong
arm = random.choice(["A", "B"])
# Right
arm = bucket(user_id, "reranker-test")
```

❌ Mistake 2: Stopping as soon as p < 0.05 (peeking inflates false positives)
✅ Correct: fix sample size in advance or use sequential tests.

❌ Mistake 3: Ignoring cost and latency guardrails.
✅ Correct: track tokens and p95 latency per arm.

---

## 🧠 Tricky Interview Question
**Q**: "B shows +4% thumbs-up, but only 3% of users leave feedback. Can you trust it?"

**Answer**: Not fully. Feedback is self-selected (non-response bias): B may change who gives feedback (e.g. more verbose answers prompt more thumbs). Check response rates per arm, use implicit metrics (follow-up rate, edit rate, task completion), and validate with an LLM-judge or human review on a random sample from both arms.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why bucket by user_id hash?
A1: So each user consistently sees one version, and assignment is random but reproducible.

Q2: [Easy] What is a guardrail metric?
A2: A metric that must not get worse (latency, cost, error rate) even if the primary metric improves.

Q3: [Medium] Why not just trust offline eval?
A3: Offline data differs from live traffic and misses UX effects like latency and tone.

Q4: [Medium] What is statistical power?
A4: Probability of detecting a real effect; low power (small samples) means real improvements are missed.

Q5: [Hard] How do you A/B test when LLM outputs are non-deterministic and feedback is sparse?
A5: Use larger samples, implicit behavioural metrics, a calibrated LLM judge on a random sample, variance reduction (CUPED), and run sequential tests with pre-registered stopping rules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have enough traffic for significance
- Changes affect user experience (retriever, prompt, model)

❌ Avoid when:
- Traffic is tiny (use offline eval + human review)
- The change is risky or unsafe to expose even to a few users

---

## 📊 Visual Diagram
```
 users ─► hash(user_id) ─┬─ 50% ─► Pipeline A (control) ─┐
                         └─ 50% ─► Pipeline B (variant) ─┤
                                                         ▼
                          log: arm, answer, feedback, latency, tokens
                                                         ▼
                          z-test + guardrails ─► ship / iterate / rollback
```

---

## 💰 Cost Impact
You pay for both arms while the test runs, and variant B may cost more per query (e.g. a reranker plus a larger model). Example: 10K queries/day x 1,500 tokens on gpt-4o-mini ≈ $2-3/day; if B uses gpt-4o it is ~15x. Track tokens per arm as a guardrail.
Optimise: start with a 5-10% canary, stop clearly losing variants early with safe sequential rules, and offline pre-screen so only promising variants reach live traffic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| A/B test | Compare two variants live | दो versions की live तुलना |
| Guardrail | Metric that must not worsen | जो metric खराब नहीं होना चाहिए |
| p-value | Chance of result under no effect | बिना असर के ऐसा नतीजा आने की संभावना |
| Power | Chance to detect true effect | असली असर पकड़ने की संभावना |
| Canary | Small initial traffic share | शुरुआती छोटा traffic हिस्सा |

---

## ⚡ 3-Line Summary
English: A/B test RAG changes on live users with deterministic bucketing, a primary metric and guardrails. Fix sample size, avoid peeking, and use a z-test. Watch cost and latency per arm.
Hindi: RAG बदलावों को live users पर deterministic bucketing, primary metric और guardrails के साथ A/B test करो। Sample size पहले तय करो, peeking से बचो और z-test इस्तेमाल करो। हर arm की cost और latency देखो।

---

## ➡️ Next Topic
**412. Retrieval Evaluation** - measuring the retriever alone (recall@k, MRR, nDCG).
