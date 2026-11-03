---

# 564. Blue-Green AI Deployment
# हिंदी में: Blue-Green AI Deployment (बिना Downtime के Release)

---

## 🔵 Simple Definition (English)
Blue-green deployment runs two identical environments: "blue" (live) and "green" (new). You test green, then switch traffic from blue to green in one step. If something breaks, switch back. For AI apps, an "environment" is the full bundle: code + model + prompt + vector index.

## 🔵 सरल परिभाषा (Hindi)
Blue-green deployment में दो एक जैसे environments चलते हैं: "blue" (live) और "green" (नया)। Green को test करके traffic एक step में blue से green पर ले जाते हैं। कुछ टूटे तो वापस switch। AI app में environment = code + model + prompt + vector index का पूरा bundle।

---

## 🔴 Problem it Solves
Normal deploys replace running servers: users see errors during restart, and a bad release is hard to undo. AI adds new risks: a new model or prompt can silently change answers, and a re-built vector index can be half-populated. You need to verify the new stack with real-like traffic before users hit it, and be able to revert in seconds.

## 🔴 यह क्यों बना? (Hindi)
Normal deploy में चलते servers बदले जाते हैं: restart में errors और खराब release को undo करना मुश्किल। AI में नए risks: नया model/prompt चुपचाप answers बदल सकता है, और नया vector index अधूरा हो सकता है। Users तक पहुँचने से पहले नए stack को verify करना और seconds में revert करना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Blue = current production (app v1 + model A + prompt v3 + index 2024-10)
Step 2 → Build Green with the change (app v2 + model B + prompt v4 + index 2024-11)
Step 3 → Run smoke tests + golden eval set against Green (no user traffic yet)
Step 4 → Shadow traffic: copy real requests to Green, compare answers, discard Green's output
Step 5 → Flip the router (load balancer / DNS / feature flag): 100% to Green
         (or canary first: 5% -> 25% -> 100%)
Step 6 → Watch error rate, latency, cost/request, quality metrics
Step 7 → Problem? Flip the router back to Blue (seconds)
Step 8 → Healthy for N hours? Retire Blue (or keep it as the next Green)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Blue = मौजूदा production (app v1 + model A + prompt v3 + index पुराना)
Step 2 → बदलाव के साथ Green बनाओ (app v2 + model B + prompt v4 + index नया)
Step 3 → Green पर smoke tests + golden eval चलाओ (अभी user traffic नहीं)
Step 4 → Shadow traffic: असली requests की copy Green को भेजो, answers compare करो, Green का output फेंक दो
Step 5 → Router flip करो (load balancer/DNS/feature flag): 100% Green पर (या पहले canary 5% -> 25% -> 100%)
Step 6 → Error rate, latency, cost/request, quality देखो
Step 7 → दिक्कत हो तो router वापस Blue पर (seconds में)
Step 8 → N घंटे ठीक रहे तो Blue हटाओ (या अगला Green बना लो)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs rules update every quarter. The team builds Green with a re-embedded tariff index and prompt v4. Shadow traffic shows Green disagrees with Blue on 6% of items. A reviewer inspects the disagreements: 5% are corrections (new rules), 1% are regressions. They fix the 1%, then canary 10%, then 100%. A week later a wrong-code spike appears; they flip back to Blue within a minute.

**Amazon-style**: The product-Q&A bot gets a new model; Green is tested on yesterday's questions before the flip.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs rules हर quarter बदलते हैं। Team नया embedded tariff index और prompt v4 के साथ Green बनाती है। Shadow traffic में Green 6% items पर Blue से अलग निकलता है। Reviewer देखता है: 5% सुधार (नए rules), 1% regression। 1% ठीक करके 10% canary, फिर 100%। एक हफ्ते बाद wrong-code spike आता है; एक मिनट में Blue पर वापस।

**Amazon-style**: Product-Q&A bot का नया model; flip से पहले कल के questions पर Green test होता है।

---

## 💻 Code Example — Basic
```python
# Basic blue/green router simulation (pure Python, runs directly)
import random                                    # for weighted traffic split
from typing import Callable                      # type hint for handlers


def blue(question: str) -> str:                  # current production stack
    return f"[blue/prompt-v3] answer to: {question}"


def green(question: str) -> str:                 # new stack under test
    return f"[green/prompt-v4] answer to: {question}"


class Router:
    def __init__(self, blue_fn: Callable[[str], str], green_fn: Callable[[str], str]) -> None:
        self.blue_fn = blue_fn                   # handler for blue
        self.green_fn = green_fn                 # handler for green
        self.green_weight = 0.0                  # 0.0 = all blue, 1.0 = all green

    def set_green_weight(self, weight: float) -> None:
        if not 0.0 <= weight <= 1.0:             # validate input
            raise ValueError("weight must be between 0 and 1")
        self.green_weight = weight               # the "flip"

    def handle(self, question: str) -> str:
        use_green = random.random() < self.green_weight   # weighted coin toss
        fn = self.green_fn if use_green else self.blue_fn  # choose stack
        return fn(question)                      # run the chosen stack


router = Router(blue, green)                     # start: everything goes to blue
print(router.handle("HS code for iPhone?"))      # blue answers
router.set_green_weight(0.1)                     # canary 10%
router.set_green_weight(1.0)                     # full flip
print(router.handle("HS code for iPhone?"))      # green answers
router.set_green_weight(0.0)                     # rollback in one line
print(router.handle("HS code for iPhone?"))      # blue again
```

## 💻 Code Example — Advanced
```python
# Production style: async shadow compare + health-gated flip with auto-rollback
from __future__ import annotations
import asyncio                                   # concurrency
import logging                                   # structured logs
import random                                    # canary split
from dataclasses import dataclass, field         # state containers
from typing import Awaitable, Callable           # type hints

log = logging.getLogger("bluegreen")
Handler = Callable[[str], Awaitable[str]]        # async stack handler


@dataclass
class Stats:
    calls: int = 0                               # total calls
    errors: int = 0                              # failed calls

    @property
    def error_rate(self) -> float:
        return self.errors / self.calls if self.calls else 0.0   # avoid div by zero


@dataclass
class BlueGreen:
    blue: Handler                                # live stack
    green: Handler                               # candidate stack
    green_weight: float = 0.0                    # traffic share for green
    max_error_rate: float = 0.05                 # rollback threshold
    stats: dict[str, Stats] = field(default_factory=lambda: {"blue": Stats(), "green": Stats()})
    diffs: list[tuple[str, str, str]] = field(default_factory=list)  # (q, blue, green)

    async def _call(self, name: str, fn: Handler, q: str) -> str:
        st = self.stats[name]                    # stats for this stack
        st.calls += 1                            # count the call
        try:
            return await asyncio.wait_for(fn(q), timeout=20)  # never hang
        except Exception as exc:                 # any failure counts as an error
            st.errors += 1
            log.warning("%s failed: %s", name, exc)
            raise

    async def shadow(self, q: str) -> str:
        """Serve from blue; run green in background for comparison only."""
        blue_task = asyncio.create_task(self._call("blue", self.blue, q))
        green_task = asyncio.create_task(self._call("green", self.green, q))
        answer = await blue_task                 # user only waits for blue
        try:
            g = await green_task                 # green result is for comparison
            if g != answer:
                self.diffs.append((q, answer, g))  # record disagreement for review
        except Exception:
            pass                                 # green errors already counted
        return answer

    async def serve(self, q: str) -> str:
        use_green = random.random() < self.green_weight
        name, fn = ("green", self.green) if use_green else ("blue", self.blue)
        try:
            return await self._call(name, fn, q)
        except Exception:
            if name == "green":                  # fall back to blue for this request
                return await self._call("blue", self.blue, q)
            raise
        finally:
            self._auto_rollback()                # check health after every call

    def _auto_rollback(self) -> None:
        g = self.stats["green"]
        if self.green_weight > 0 and g.calls >= 20 and g.error_rate > self.max_error_rate:
            log.error("green error rate %.2f > limit, rolling back", g.error_rate)
            self.green_weight = 0.0              # automatic flip back to blue
```

---

## 🟠 FastAPI Integration
The router sits in the API layer (or in a gateway like NGINX/ALB). Expose an admin endpoint to change the weight and a read-only status endpoint.

```python
from fastapi import FastAPI, HTTPException            # framework
from pydantic import BaseModel, Field                 # validation

app = FastAPI()


async def blue_stack(q: str) -> str:                   # real code would call model A
    return f"blue: {q}"


async def green_stack(q: str) -> str:                  # real code would call model B
    return f"green: {q}"


bg = BlueGreen(blue=blue_stack, green=green_stack)     # from Advanced example


class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class Weight(BaseModel):
    green_weight: float = Field(ge=0.0, le=1.0)


@app.post("/ask")
async def ask(body: Ask) -> dict:
    try:
        return {"answer": await bg.serve(body.question)}
    except Exception:
        raise HTTPException(status_code=503, detail="service unavailable")


@app.post("/admin/traffic")                            # protect with auth in real life
async def set_traffic(w: Weight) -> dict:
    bg.green_weight = w.green_weight                   # canary / flip / rollback
    return {"green_weight": bg.green_weight}


@app.get("/admin/status")
async def status() -> dict:
    return {"weight": bg.green_weight,
            "blue_error_rate": bg.stats["blue"].error_rate,
            "green_error_rate": bg.stats["green"].error_rate,
            "diffs": len(bg.diffs)}
```

---

## 🔗 LangChain / LangGraph Connection
A LangChain chain or compiled LangGraph is just a callable, so blue and green are two compiled graphs (different prompt, model, or retriever). Keep checkpointers (conversation state) in a shared store so a user mid-conversation survives a flip; otherwise pin the session to one color.

```python
# two chains = two colors (illustrative; llm_a / llm_b / retriever_* defined elsewhere)
# blue_chain  = prompt_v3 | llm_a | parser
# green_chain = prompt_v4 | llm_b | parser
# handler = lambda q: green_chain.ainvoke({"q": q})   # plug into BlueGreen
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Green uses the same mutable vector index as Blue, then re-indexing corrupts Blue.
✅ Correct: Build a new index (versioned collection name) for Green; never mutate the live one.

```python
# Wrong
index = client.get_collection("tariffs")        # shared, re-embedded in place
# Right
index = client.get_collection("tariffs_2024_11")  # new, immutable collection for green
```

❌ Mistake 2: Flipping 100% instantly with no shadow test or metrics.
✅ Correct: shadow, then canary 5% -> 25% -> 100%, with auto-rollback thresholds.

❌ Mistake 3: Deleting Blue right after the flip. Keep it warm for hours or days.

---

## 🧠 Tricky Interview Question
**Q**: "Green passes all tests and the flip goes fine, yet two days later accuracy drops. Blue is gone. What went wrong?"

**Answer**: Offline evals and short canaries miss slow drifts: new document types, seasonal queries, the provider silently updating an unpinned model alias, or rate-limit/cache effects at full load. Mitigation: keep Blue for a defined soak period, pin model snapshot versions, run continuous online evals (sampled LLM-as-judge) on production, track quality metrics per version, and keep infra as code so Blue can be rebuilt quickly.

---

## ⚫ Interview Questions + Answers

Q1: What is blue-green deployment?
A1: Two identical environments; one serves users, the other holds the new release. Traffic switches in one step and can switch back.

Q2: Blue-green vs canary?
A2: Blue-green flips all traffic at once (fast rollback, needs double capacity). Canary shifts traffic gradually (limits blast radius, slower). Often combined: green receives canary traffic first.

Q3: What counts as an "environment" in an AI app?
A3: App code, model + parameters, prompt version, retriever/vector index, tool configs, and guardrails. All should change together and be versioned.

Q4: What is shadow traffic and why is it useful for LLMs?
A4: Real requests are copied to green; its answers are only logged and compared. LLM outputs are non-deterministic, so compare with semantic similarity or a judge, not exact match.

Q5: (Hard) Costs double during shadowing. How do you control that?
A5: Sample (e.g. 5-10%) of traffic, shadow only a representative slice, use cheaper judge models, cache repeated queries, and limit shadow time to a few hours. The cost of a bad release usually exceeds it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Changing the model, prompt, or embedding index in a customer-facing system
- You need near-zero downtime and fast rollback

❌ Avoid when:
- Prototype or internal tool where a restart is fine
- Stateful changes that cannot run in parallel (use migrations plus feature flags)
- Budget cannot support two stacks (use canary on a small pool)

---

## 📊 Visual Diagram
```
                 ┌────────────────────────┐
 Users ─► Router │ weight: green = 0..1   │
                 └───────┬───────────┬────┘
                         │           │
                  BLUE (live)     GREEN (new)
                  app v1          app v2
                  model A         model B
                  prompt v3       prompt v4
                  index 2024-10   index 2024-11
                         ▲           │
                         └── rollback┘ (set weight 0)
```

---

## 💰 Cost Impact
- Running two stacks doubles infra during the transition; shadow traffic doubles LLM tokens for the shadowed share. Example (illustrative): 1M requests/day x 10% shadow x 1,200 tokens = 120M extra tokens/day.
- Optimise: shadow a sample only, keep the soak window short, scale Blue down after the soak, reuse caches, and use batch/cheaper models for judging diffs.
- A bad release without rollback costs more (wrong customs codes, refunds, trust).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blue | Current live environment | मौजूदा live environment |
| Green | New candidate environment | नया candidate environment |
| Canary | Small gradual traffic share | थोड़ा-थोड़ा traffic |
| Shadow traffic | Copied requests, output discarded | Copy traffic, output इस्तेमाल नहीं |
| Rollback | Switch back to old version | पुराने version पर वापसी |
| Soak period | Waiting time before retiring Blue | Blue हटाने से पहले इंतज़ार |

---

## ⚡ 3-Line Summary
English: Blue-green keeps the live stack untouched while you test the new one, then flips traffic in one step. In AI, the stack includes model, prompt, and index, so all three are versioned and switched together. Shadow tests, canaries, and auto-rollback make releases safe.
Hindi: Blue-green में live stack को छुए बिना नए stack को test करते हैं, फिर traffic एक step में flip करते हैं। AI में stack = model, prompt और index, इसलिए तीनों साथ version और switch होते हैं। Shadow test, canary और auto-rollback से release सुरक्षित बनता है।

---

## ➡️ Next Topic
**565. Monitoring in Production** — once traffic is live, you need metrics, traces, and quality alerts to know when to flip back.
