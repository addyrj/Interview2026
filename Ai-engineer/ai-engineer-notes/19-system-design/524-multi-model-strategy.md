---

# 524. Multi-model Strategy
# हिंदी में: Multi-model Strategy

---

## 🔵 Simple Definition (English)
A multi-model strategy uses several models in one system and picks the right one per task: a small fast model for easy work, a large model for hard reasoning, an embedding model for search, and maybe another provider for backup. Right model, right job, right price.

## 🔵 सरल परिभाषा (Hindi)
Multi-model strategy में एक system में कई models होते हैं और हर task के लिए सही model चुना जाता है: आसान काम के लिए छोटा तेज़ model, कठिन reasoning के लिए बड़ा model, search के लिए embedding model, और backup के लिए दूसरा provider। सही model, सही काम, सही price।

---

## 🔴 Problem it Solves
One model for everything is either too expensive (large model for trivial tasks) or too weak (small model for hard tasks). Single-vendor lock-in also risks outages, price hikes, and deprecations. Different models are best at different things: speed, reasoning, long context, multilingual, vision, code.

## 🔴 यह क्यों बना? (Hindi)
सब कुछ एक model से करने पर या तो बहुत महँगा (आसान काम पर बड़ा model) या कमज़ोर (कठिन काम पर छोटा model)। Single vendor lock-in से outage, price hike और deprecation का risk रहता है। अलग models अलग चीज़ों में best हैं: speed, reasoning, long context, multilingual, vision, code।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Break the product into tasks (classify, extract, reason, summarise, embed, vision)
Step 2 → Build an eval set per task and measure quality, cost, latency per candidate model
Step 3 → Choose a primary model per task (cheapest that meets the quality bar)
Step 4 → Add a router: rules (task type, input size, language) or a small classifier model
Step 5 → Add escalation: low confidence or failed validation -> stronger model
Step 6 → Add backup per task (different provider) behind a common gateway interface
Step 7 → Keep prompts/config per model in versioned config, not hard-coded
Step 8 → Re-evaluate monthly: new models appear often, prices change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Product को tasks में तोड़ो (classify, extract, reason, summarise, embed, vision)
Step 2 → हर task का eval set बनाओ, हर model की quality, cost, latency नापो
Step 3 → हर task के लिए सबसे सस्ता model चुनो जो quality bar पूरा करे
Step 4 → Router जोड़ो: rules (task type, input size, language) या छोटा classifier
Step 5 → Escalation: low confidence या validation fail पर बड़ा model
Step 6 → हर task का backup (दूसरा provider) common gateway के पीछे
Step 7 → Prompts/config model-wise versioned config में रखो
Step 8 → हर महीने दोबारा evaluate करो: नए models और prices बदलते रहते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: (1) an embedding model retrieves candidate HS chapters; (2) a small, cheap LLM classifies clear descriptions ("cotton t-shirt"); (3) a stronger reasoning model handles ambiguous items ("multi-purpose smart device with sensors"); (4) a vision model reads scanned invoices; (5) a different provider is the backup. Names of specific models change often, so the router config stores model IDs outside code.

**Amazon-style**: Product title cleanup uses a tiny model on millions of items, while customer-service escalations use a stronger model.

## 🟡 Real Example Hindi mein
**Tariff System**: (1) embedding model से candidate HS chapters; (2) साफ descriptions ("cotton t-shirt") के लिए छोटा सस्ता LLM; (3) ambiguous items के लिए मज़बूत reasoning model; (4) scanned invoices के लिए vision model; (5) backup के लिए दूसरा provider। Model names बदलते रहते हैं, इसलिए router config में model IDs code से बाहर रखो।
**Amazon-style**: Product title cleanup लाखों items पर छोटा model करता है, customer-service escalations पर मज़बूत model।

---

## 💻 Code Example — Basic
```python
# Rule-based model router (pure Python, runs offline)
# Model names here are placeholders; read real ones from config
ROUTES: dict[str, str] = {            # task -> model alias
    "classify_easy": "small-fast",    # cheap model for simple tasks
    "classify_hard": "large-smart",   # stronger model for hard tasks
    "ocr": "vision-model",            # vision-capable model
}

def pick_task(text: str, has_image: bool = False) -> str:
    """Decide which task type a request is."""
    if has_image:                     # images need vision
        return "ocr"
    words = len(text.split())         # rough size of the input
    hard_words = {"multi-purpose", "composite", "kit", "assembly", "mixture"}   # tricky hints
    if words > 40 or hard_words & set(text.lower().split()):   # long or tricky
        return "classify_hard"
    return "classify_easy"            # default

def route(text: str, has_image: bool = False) -> str:
    """Return the model alias to use."""
    return ROUTES[pick_task(text, has_image)]   # task -> model

for sample in ["cotton t-shirt", "multi-purpose smart device with sensors and display"]:
    print(sample[:30].ljust(32), "->", route(sample))    # show routing decisions
print("scanned invoice ->", route("", has_image=True))   # vision route
```

## 💻 Code Example — Advanced
```python
# Router with confidence escalation, per-model stats, and backup (async, typed)
import asyncio                                          # async runtime
from dataclasses import dataclass, field                # config and stats
from typing import Awaitable, Callable                  # type hints

@dataclass
class ModelSpec:
    alias: str                                          # internal name
    in_price: float                                     # illustrative $/1M input tokens
    out_price: float                                    # illustrative $/1M output tokens
    call: Callable[[str], Awaitable[dict]]              # async fn -> {"code","confidence","in","out"}

@dataclass
class Stats:
    calls: int = 0                                      # number of calls
    cost: float = 0.0                                   # dollars spent

class MultiModelRouter:
    def __init__(self, cheap: ModelSpec, strong: ModelSpec, backup: ModelSpec,
                 threshold: float = 0.85) -> None:
        self.cheap, self.strong, self.backup = cheap, strong, backup   # model roles
        self.threshold = threshold                      # escalate below this
        self.stats: dict[str, Stats] = {m.alias: Stats() for m in (cheap, strong, backup)}

    def _track(self, m: ModelSpec, r: dict) -> None:
        """Record usage and dollars."""
        s = self.stats[m.alias]                         # stats row
        s.calls += 1                                    # count call
        s.cost += r["in"] * m.in_price / 1e6 + r["out"] * m.out_price / 1e6   # add cost

    async def _try(self, m: ModelSpec, text: str) -> dict | None:
        """Call a model; return None on any failure."""
        try:
            r = await asyncio.wait_for(m.call(text), 10)   # timeout guard
            self._track(m, r)                           # meter
            return r
        except Exception:                               # outage, 429, timeout
            return None

    async def classify(self, text: str) -> dict:
        """Cheap first, escalate on low confidence, backup on failure."""
        r = await self._try(self.cheap, text)           # step 1: cheap model
        used = self.cheap.alias
        if r is None or r["confidence"] < self.threshold:   # failed or unsure
            r2 = await self._try(self.strong, text)     # step 2: strong model
            if r2 is not None:
                r, used = r2, self.strong.alias
        if r is None:                                   # both failed
            r = await self._try(self.backup, text)      # step 3: other provider
            used = self.backup.alias
        if r is None:                                   # nothing worked
            raise RuntimeError("all models failed")
        return {"code": r["code"], "confidence": r["confidence"], "model": used}

async def demo() -> None:
    async def cheap(t: str) -> dict:                    # confident only on simple text
        return {"code": "6109.10", "confidence": 0.95 if len(t) < 20 else 0.5, "in": 600, "out": 40}
    async def strong(t: str) -> dict:
        return {"code": "8543.70", "confidence": 0.97, "in": 600, "out": 120}
    async def backup(t: str) -> dict:
        return {"code": "8543.70", "confidence": 0.8, "in": 600, "out": 120}
    router = MultiModelRouter(
        ModelSpec("cheap", 0.15, 0.60, cheap), ModelSpec("strong", 3.0, 15.0, strong),
        ModelSpec("backup", 1.0, 5.0, backup))
    print(await router.classify("cotton shirt"))                                   # cheap answers
    print(await router.classify("multi-purpose smart device with sensors"))        # escalates
    print({k: (v.calls, round(v.cost, 6)) for k, v in router.stats.items()})       # usage per model

if __name__ == "__main__":
    asyncio.run(demo())                                 # run
```

---

## 🟠 FastAPI Integration
Keep model choice behind one service (an LLM gateway). Routes call `router.classify`; clients never name vendors. Let an optional `X-Model-Tier` header (authorised users only) force a tier for debugging, and expose per-model stats for dashboards.

```python
# FastAPI: gateway endpoint with model stats
from fastapi import FastAPI                                  # framework
from pydantic import BaseModel                               # validation

app = FastAPI()                                              # app
router = build_router_from_config()                          # your factory that reads model IDs from config/env

class Req(BaseModel):
    description: str                                         # product text

@app.post("/classify")
async def classify(req: Req) -> dict:
    return await router.classify(req.description)            # route inside the gateway

@app.get("/admin/model-stats")
async def stats() -> dict[str, dict[str, float]]:
    return {k: {"calls": v.calls, "cost_usd": round(v.cost, 6)} for k, v in router.stats.items()}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain gives a common chat-model interface across vendors, so swapping is a config change. `init_chat_model` can create a model from a name and provider string. `RunnableBranch` or a custom `RunnableLambda` can route; `with_fallbacks` adds backups. In LangGraph a `router` node writes the chosen model into state and conditional edges send work to the matching node; each node can use a different model.

```python
# LangChain: route by a rule between two models
from langchain_core.runnables import RunnableBranch, RunnableLambda   # routing blocks
from langchain_openai import ChatOpenAI                               # model wrapper

small = ChatOpenAI(model="gpt-4o-mini")                      # cheap tier (example name)
large = ChatOpenAI(model="gpt-4o")                           # strong tier (example name)

route = RunnableBranch(
    (lambda x: len(x["text"].split()) > 40, large),          # long/complex -> large
    small,                                                   # default -> small
)
# answer = await route.ainvoke({"text": "..."})              # picks a model per input
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing models by hype instead of your evals
✅ Correct: Benchmark on your own labelled data.

```python
# Wrong
MODEL = "whatever-is-trending"

# Right
for m in candidates:
    print(m, accuracy(m, tariff_eval_set), avg_cost(m), p95_latency(m))
```

❌ Mistake 2: Hard-coding model names and vendor-specific code everywhere
✅ Correct: Config + a gateway layer.

```python
# Wrong
client.chat.completions.create(model="gpt-4o-mini", ...)   # scattered in 40 files

# Right
llm = get_model("classify_easy")      # alias resolved from config, one place to change
```

---

## 🧠 Tricky Interview Question

**Q**: "You route 80% of traffic to a cheap model with confidence-based escalation. Accuracy drops silently. Why might confidence not protect you?"

**Answer**: Model confidence (especially a self-reported number from the LLM) is poorly calibrated: small models can be confidently wrong. Escalation only helps if the confidence signal is reliable. Fix: calibrate on a labelled set, use stronger signals (log-probabilities where available, agreement between two cheap samples, validation against trusted tables, a small verifier model), sample a percentage of cheap-path answers for offline grading by the strong model, and alert on drift. Also shadow-test changes before shifting traffic.

---

## ⚫ Interview Questions + Answers

Q1: Why use more than one model? (Easy)
A1: To balance cost, quality, speed and availability: cheap models for simple tasks, strong models for hard ones, plus backups.

Q2: What is model routing? (Easy)
A2: A component that picks which model handles each request, using rules (task, size, language), a classifier, or cost/latency constraints.

Q3: How do you decide which model per task? (Medium)
A3: Build an eval set per task, run candidates, compare accuracy, cost per task and p95 latency, then choose the cheapest model that passes the quality bar. Re-run when models or prices change.

Q4: What are the downsides of multi-model systems? (Medium)
A4: More complexity: more prompts to maintain, different output quirks, more evals, harder debugging, and multiple vendor contracts and data-privacy reviews. Mitigate with a gateway, shared schemas and tracing.

Q5: Design a router that learns from feedback. (Hard)
A5: Log features (task, length, language, retrieved-chunk scores) and outcomes (validation pass, human corrections, strong-model agreement). Train a lightweight classifier predicting "cheap model will succeed". Route with a cost-aware threshold, keep an exploration slice (for example 5%) sent to the strong model to gather labels, guard with offline evals and canary rollout, and monitor accuracy per segment to avoid hidden regressions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tasks vary in difficulty and traffic is large
- You need vendor redundancy
- Different modalities (text, vision, embeddings) are needed

❌ Avoid when:
- Volume is low, so complexity outweighs savings
- You lack evals to compare models fairly

---

## 📊 Visual Diagram
```
                 ┌──▶ [Small fast model] ──conf≥0.85──▶ answer
Request ─▶[Router]│            │ low conf
 (rules /        │            ▼
  classifier)    ├──▶ [Large model] ──────────────────▶ answer
                 ├──▶ [Vision model] (images/scans)
                 └──▶ [Embedding model] (retrieval)
 Any model fails ─▶ [Backup provider]   Metrics per model ─▶ cost / quality / latency
```

---

## 💰 Cost Impact
Illustrative prices ($/1M tokens, input/output): small 0.15/0.60, large 3.00/15.00. For 1M requests of 700 in + 100 out tokens: all-large = $3,600; all-small = $165. With routing (80% small, 20% large): 0.8 x $165 + 0.2 x $3,600 = about $852, so around 76% cheaper than all-large. Add escalation cost (cheap call plus strong call) for uncertain cases, perhaps 10%, about $165 x 0.1 extra tokens' worth. Optimise by tuning the threshold with real evals, caching, and prompt caching on static prefixes. Token usage differs per model (tokenizers differ), so meter per model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Model routing | Choose model per request | हर request के लिए model चुनना |
| Escalation | Move to a stronger model | बड़े model पर भेजना |
| LLM gateway | One layer in front of all models | सभी models के आगे एक layer |
| Vendor lock-in | Dependence on one provider | एक vendor पर निर्भरता |
| Calibration | Confidence matches real accuracy | Confidence = असली accuracy |
| Shadow testing | Run new model silently in parallel | नया model चुपचाप parallel चलाना |
| Eval set | Labelled data for comparing models | Models की तुलना का labelled data |

---

## ⚡ 3-Line Summary
English: Use different models for different tasks: cheap for easy, strong for hard, vision and embeddings where needed, plus a backup vendor. Pick by your own evals and route through a gateway with confidence-based escalation. Watch calibration, or the cheap path fails silently.
Hindi: अलग tasks के लिए अलग models: आसान के लिए सस्ता, कठिन के लिए मज़बूत, ज़रूरत पर vision/embedding और एक backup vendor। अपने evals से चुनो और gateway से confidence-based escalation के साथ route करो। Calibration देखो, वरना सस्ता path चुपचाप fail होगा।

---

## ➡️ Next Topic
**525. A/B Testing AI Systems** — how to compare two models or prompts safely using real traffic.
