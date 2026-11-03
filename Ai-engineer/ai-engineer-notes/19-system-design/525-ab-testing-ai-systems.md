---

# 525. A/B Testing AI Systems
# हिंदी में: AI Systems की A/B Testing

---

## 🔵 Simple Definition (English)
A/B testing sends part of real traffic to version A (current) and part to version B (new prompt, model, or retrieval setting) and compares measured results. It tells you with evidence whether the change is better, instead of trusting a few test examples.

## 🔵 सरल परिभाषा (Hindi)
A/B testing में real traffic का एक हिस्सा version A (मौजूदा) को और एक हिस्सा version B (नया prompt, model या retrieval setting) को जाता है और नतीजों की तुलना होती है। कुछ test examples पर भरोसा करने की जगह सबूत मिलता है कि बदलाव बेहतर है या नहीं।

---

## 🔴 Problem it Solves
LLM outputs are non-deterministic and quality is hard to judge with unit tests. A prompt that looks better on 10 examples may be worse on real users. Offline evals miss real behaviour, and a full rollout of a bad change hurts everyone. A/B testing limits the damage and gives statistically meaningful answers.

## 🔴 यह क्यों बना? (Hindi)
LLM outputs non-deterministic हैं और quality unit tests से नापना कठिन है। 10 examples पर बेहतर दिखने वाला prompt real users पर खराब हो सकता है। Offline evals real behaviour miss करते हैं, और खराब change का full rollout सबको नुकसान देता है। A/B testing नुकसान सीमित रखती है और statistically सही जवाब देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a hypothesis ("Prompt B raises correct-code rate by 3 points")
Step 2 → Pick ONE primary metric (accuracy, acceptance rate) plus guardrails (cost, latency, errors)
Step 3 → Pass offline evals first; B must not be obviously worse
Step 4 → Randomly assign by a stable hash of user/tenant ID (same user always sees same variant)
Step 5 → Log variant, inputs, outputs, tokens, latency, and feedback for every request
Step 6 → Compute sample size in advance; run long enough (full weekly cycle)
Step 7 → Analyse with a proper test (proportion test / bootstrap), not by eyeballing
Step 8 → Decide: ship B, keep A, or iterate; document the learning
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Hypothesis लिखो ("Prompt B से correct-code rate 3 points बढ़ेगा")
Step 2 → एक primary metric (accuracy, acceptance) और guardrails (cost, latency, errors)
Step 3 → पहले offline evals पास करो; B साफ़ तौर पर खराब न हो
Step 4 → User/tenant ID के stable hash से random assignment (एक user को हमेशा एक ही variant)
Step 5 → हर request पर variant, input, output, tokens, latency, feedback log करो
Step 6 → पहले से sample size निकालो; पूरा हफ्ता चलाओ
Step 7 → सही test (proportion test / bootstrap) से analyse करो, अंदाज़े से नहीं
Step 8 → फैसला: B ship, A रखो या iterate; सीख document करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Prompt A is the current prompt. Prompt B adds three worked examples and a "check chapter notes" instruction. Metric: percentage of classifications accepted by brokers without edits. Guardrails: cost per classification and p95 latency. Brokers (by company ID hash) are split 90/10 at first, then 50/50. B raises acceptance from 82% to 86% but adds 400 input tokens per call, so the team decides whether +4 points is worth the cost.

**Zomato-style**: Two versions of the "dish description generator" are compared on click-through and order rate.

## 🟡 Real Example Hindi mein
**Tariff System**: Prompt A मौजूदा prompt है। Prompt B में तीन worked examples और "chapter notes check करो" instruction जुड़ा है। Metric: brokers द्वारा बिना edit के accept हुई classifications का %। Guardrails: cost per classification और p95 latency। Company ID hash से पहले 90/10, फिर 50/50 split। B से acceptance 82% से 86% हुई पर हर call में 400 input tokens बढ़े, तो टीम तय करती है कि +4 points की कीमत ठीक है या नहीं।
**Zomato-style**: Dish description generator के दो versions को click-through और order rate पर compare करते हैं।

---

## 💻 Code Example — Basic
```python
# Deterministic bucketing + two-proportion z-test (pure Python, runs offline)
import hashlib                                     # stable hashing for assignment
import math                                        # sqrt and erf for the p-value
import random                                      # simulate outcomes

def variant(user_id: str, experiment: str, pct_b: float = 0.5) -> str:
    """Assign a user to A or B. Same user + experiment always gives the same result."""
    h = hashlib.sha256(f"{experiment}:{user_id}".encode()).hexdigest()   # hash
    bucket = int(h[:8], 16) / 0xFFFFFFFF           # map to a number in [0, 1]
    return "B" if bucket < pct_b else "A"          # below threshold means B

def z_test(success_a: int, n_a: int, success_b: int, n_b: int) -> tuple[float, float]:
    """Return (z, two-sided p-value) comparing two proportions."""
    p_a, p_b = success_a / n_a, success_b / n_b    # observed rates
    pooled = (success_a + success_b) / (n_a + n_b) # pooled rate under H0
    se = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))   # standard error
    z = (p_b - p_a) / se                           # z statistic
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))     # two-sided p-value
    return z, p

random.seed(7)                                     # repeatable simulation
counts = {"A": [0, 0], "B": [0, 0]}                # [successes, total]
for i in range(4000):                              # simulate 4000 users
    v = variant(f"user{i}", "prompt-v2")           # assign
    accepted = random.random() < (0.82 if v == "A" else 0.86)   # B truly better
    counts[v][0] += accepted                       # count success
    counts[v][1] += 1                              # count total
z, p = z_test(counts["A"][0], counts["A"][1], counts["B"][0], counts["B"][1])
print(counts, f"z={z:.2f} p={p:.4f}")              # significant if p < 0.05
```

## 💻 Code Example — Advanced
```python
# Experiment framework: assignment, logging, guardrails, bootstrap CI (async, typed)
import asyncio                                           # async runtime
import hashlib                                           # stable assignment
import random                                            # bootstrap sampling
import statistics                                        # mean
import time                                              # latency
from dataclasses import dataclass, field                 # data classes
from typing import Awaitable, Callable                   # type hints

@dataclass
class Event:
    variant: str                                         # A or B
    success: bool                                        # primary metric outcome (e.g. accepted)
    cost_usd: float                                      # guardrail metric
    latency_s: float                                     # guardrail metric

@dataclass
class Experiment:
    name: str                                            # experiment id
    pct_b: float = 0.1                                   # share of traffic for B
    events: list[Event] = field(default_factory=list)    # in production write to a DB/warehouse

    def assign(self, unit_id: str) -> str:
        """Stable assignment by hash."""
        h = int(hashlib.sha256(f"{self.name}:{unit_id}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        return "B" if h < self.pct_b else "A"

    async def run(self, unit_id: str, text: str,
                  handlers: dict[str, Callable[[str], Awaitable[tuple[str, float]]]]) -> str:
        """Serve the assigned variant; fall back to A if B errors."""
        v = self.assign(unit_id)                         # which variant
        start = time.perf_counter()                      # timer
        try:
            out, cost = await handlers[v](text)          # run assigned handler
        except Exception:                                # B must never break users
            v = "A"                                      # fall back to control
            out, cost = await handlers["A"](text)
        self._latency = time.perf_counter() - start      # last latency (simple demo)
        self._pending = (v, cost, self._latency)         # remember for feedback
        return out

    def record(self, variant: str, success: bool, cost: float, latency: float) -> None:
        """Log feedback when the outcome is known."""
        self.events.append(Event(variant, success, cost, latency))

    def bootstrap_diff(self, n: int = 2000) -> tuple[float, float]:
        """95% CI for (rate_B - rate_A) by bootstrap."""
        a = [e.success for e in self.events if e.variant == "A"]
        b = [e.success for e in self.events if e.variant == "B"]
        if not a or not b:                               # need data in both arms
            raise ValueError("need events for both variants")
        diffs = sorted(                                  # resample many times
            statistics.fmean(random.choices(b, k=len(b))) - statistics.fmean(random.choices(a, k=len(a)))
            for _ in range(n))
        return diffs[int(0.025 * n)], diffs[int(0.975 * n)]

async def demo() -> None:
    random.seed(3)                                       # repeatable
    exp = Experiment("prompt-v2", pct_b=0.5)             # 50/50
    async def a(t: str) -> tuple[str, float]: return "A-answer", 0.0002
    async def b(t: str) -> tuple[str, float]: return "B-answer", 0.0003
    for i in range(1000):                                # simulate users
        await exp.run(f"u{i}", "smart phone", {"A": a, "B": b})
        v, cost, lat = exp._pending                      # variant actually served
        exp.record(v, random.random() < (0.82 if v == "A" else 0.86), cost, lat)
    lo, hi = exp.bootstrap_diff()
    print(f"B-A diff 95% CI: [{lo:.3f}, {hi:.3f}]")      # if the CI excludes 0, the effect is real

if __name__ == "__main__":
    asyncio.run(demo())                                  # run
```

---

## 🟠 FastAPI Integration
Assignment belongs in the API layer so one user always sees one variant. Return the variant in a header, log it, and expose a feedback endpoint (thumbs up/down or "accepted") that records the primary metric.

```python
# FastAPI: variant assignment + feedback endpoint
from fastapi import FastAPI, Header, Response               # framework
from pydantic import BaseModel                              # validation

app = FastAPI()                                             # app
exp = Experiment("prompt-v2", pct_b=0.1)                    # 10% to B (see advanced block)

class Req(BaseModel):
    description: str                                        # product text

class Feedback(BaseModel):
    request_id: str                                         # which answer
    variant: str                                            # A or B
    accepted: bool                                          # user outcome

@app.post("/classify")
async def classify(req: Req, resp: Response, x_user_id: str = Header(...)) -> dict:
    out = await exp.run(x_user_id, req.description, HANDLERS)   # HANDLERS = {"A": ..., "B": ...} your two prompt functions
    resp.headers["X-Variant"] = exp.assign(x_user_id)       # visible in logs and clients
    return {"answer": out}

@app.post("/feedback")
async def feedback(fb: Feedback) -> dict[str, str]:
    exp.record(fb.variant, fb.accepted, cost=0.0, latency=0.0)   # real code looks up cost and latency by request_id
    return {"status": "recorded"}
```

---

## 🔗 LangChain / LangGraph Connection
Use LangSmith (or Langfuse and similar) to tag runs with `metadata={"variant": "B"}` and compare experiments; LangSmith datasets and evaluators run offline comparisons before any live test. In LangGraph, put the variant in state or config and use a conditional edge to choose a prompt or node. Keep the rest of the graph identical so you test one change at a time.

```python
# LangChain: tag runs with the variant so traces can be compared later
from langchain_core.prompts import ChatPromptTemplate         # prompts
from langchain_openai import ChatOpenAI                       # model wrapper

prompts = {                                                   # two prompt versions
    "A": ChatPromptTemplate.from_template("HS code for: {x}"),
    "B": ChatPromptTemplate.from_template("Think about chapter notes, then give HS code for: {x}"),
}
llm = ChatOpenAI(model="gpt-4o-mini")                         # same model in both arms

async def run(x: str, variant: str) -> str:
    chain = prompts[variant] | llm                            # pick the prompt
    msg = await chain.ainvoke({"x": x}, config={"metadata": {"variant": variant}, "tags": ["exp:prompt-v2"]})
    return msg.content                                        # variant is attached to the trace
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Peeking and stopping when B looks ahead
✅ Correct: Fix the sample size or use sequential testing methods.

```python
# Wrong — check daily and stop at the first p < 0.05 (inflates false positives)
if p_value < 0.05: ship_B()

# Right — decide n up front, evaluate once at the end
if n_a >= required_n and n_b >= required_n and p_value < 0.05: ship_B()
```

❌ Mistake 2: Random assignment per request instead of per user
✅ Correct: Hash the user ID so people get a consistent experience.

```python
# Wrong — same user flips between variants, metrics get contaminated
variant = random.choice(["A", "B"])

# Right
variant = "B" if int(hashlib.sha256(user_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF < 0.1 else "A"
```

---

## 🧠 Tricky Interview Question

**Q**: "B shows +2% accuracy as judged by an LLM-as-judge, but users complain more. What is going on?"

**Answer**: The judge metric and user value are misaligned. LLM judges have known biases (they prefer longer or more confident answers and answers from their own model family). Validate the judge against human labels, use real outcome metrics (acceptance, edits, complaints, escalations), add guardrails (latency, cost, refusal rate), look at segments (a gain in one segment can hide a loss in another), and check for novelty or sample-ratio-mismatch bugs. Trust the user-outcome metric once the judge disagrees with it.

---

## ⚫ Interview Questions + Answers

Q1: What is an A/B test in AI? (Easy)
A1: Comparing two versions (prompt, model, retrieval config) on randomly split live traffic and measuring a metric to see which is better.

Q2: Why assign users by hash? (Easy)
A2: So the same user always sees the same variant, which keeps experience consistent and the data clean, and keeps assignment reproducible without storing state.

Q3: What metrics do you use for LLM A/B tests? (Medium)
A3: Primary: task success (acceptance, resolution, correctness from labels). Secondary: thumbs, edit distance, escalation. Guardrails: cost per task, latency, error and refusal rates, safety flags. LLM-judge scores are supporting evidence only.

Q4: Offline eval vs A/B test? (Medium)
A4: Offline evals are fast, cheap and repeatable on a fixed dataset, good for filtering bad ideas. A/B tests measure real user behaviour and unknown unknowns but are slower and riskier. Use offline first, then a small live test.

Q5: How do you A/B test with low traffic or delayed outcomes? (Hard)
A5: Use bigger effect targets, longer duration, paired or interleaved evaluation, variance reduction (CUPED) and stratification, replay of logged traffic, and human-labelled samples. For delayed outcomes (a customs decision weeks later) use proxy metrics validated against the final outcome, or analyse in cohorts once outcomes mature.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Changing prompts, models, retrieval, or UX that affects quality or cost
- You have enough traffic and a measurable outcome
- The change passed offline evals and is safe to expose

❌ Avoid when:
- The change is risky or irreversible (legal, safety): use shadow mode or canary on internal users first
- Traffic is too small to reach significance

---

## 📊 Visual Diagram
```
                         ┌──▶ Variant A (control) ──┐
Users ─▶ hash(user_id) ──┤                          ├─▶ log: variant, output,
                         └──▶ Variant B (new, 10%) ─┘      tokens, latency, feedback
                                                              │
                                               stats: z-test / bootstrap CI
                                                              ▼
                                  ship B  |  keep A  |  iterate   (guardrails: cost, latency)
```

---

## 💰 Cost Impact
- The experiment runs B on a share of traffic, so cost changes proportionally. Illustrative: B adds 400 input tokens on 100K daily calls at $0.15/1M = $6/day for the whole fleet; with a 10% test the experiment costs about $0.60/day extra. Cheap insurance against shipping a worse prompt.
- Big models in B can be expensive: cap the share, set a budget guardrail, and stop early on a clear harm (safety or cost), not on a "win".
- Log tokens per variant so the decision includes cost per successful task, not accuracy alone. Reuse logged traffic for offline replay to avoid paying for repeated live tests.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Control / Treatment | Current / new version | मौजूदा / नया version |
| Primary metric | Main success measure | मुख्य सफलता का पैमाना |
| Guardrail metric | Must-not-worsen measure | जो बिगड़ना नहीं चाहिए |
| Statistical significance | Unlikely to be chance | Chance से होने की कम संभावना |
| Sample ratio mismatch | Split differs from plan | Split का plan से अलग होना |
| Shadow mode | Run B silently without showing | B को चुपचाप चलाना |
| LLM-as-judge | Model scores outputs | Model से outputs की scoring |

---

## ⚡ 3-Line Summary
English: A/B testing compares versions on real traffic with stable user assignment, one primary metric, and cost/latency guardrails. Decide sample size up front, analyse with a proper test, and do not trust LLM-judge scores alone. Offline evals first, live tests second.
Hindi: A/B testing में real traffic पर stable user assignment, एक primary metric और cost/latency guardrails के साथ versions compare होते हैं। Sample size पहले तय करो, सही test से analyse करो और सिर्फ LLM-judge पर भरोसा मत करो। पहले offline evals, फिर live test।

---

## ➡️ Next Topic
**526. Feature Flags for AI** — the switchboard that lets you control which variant, model or feature each user gets, and turn things off instantly.
