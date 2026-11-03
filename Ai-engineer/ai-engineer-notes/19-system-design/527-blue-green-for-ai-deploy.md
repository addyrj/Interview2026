---

# 527. Blue-Green for AI Deploy
# हिंदी में: AI Deploy के लिए Blue-Green

---

## 🔵 Simple Definition (English)
Blue-green deployment keeps two identical production environments: blue (live) and green (new). You deploy and test the new version in green, then switch all traffic from blue to green at once. If something is wrong, you switch back to blue immediately.

## 🔵 सरल परिभाषा (Hindi)
Blue-green deployment में दो एक जैसे production environments होते हैं: blue (live) और green (नया)। नया version green में deploy और test करो, फिर पूरा traffic एक बार में blue से green पर switch करो। कुछ गलत हो तो तुरंत वापस blue पर।

---

## 🔴 Problem it Solves
In-place deploys cause downtime or leave the system half-upgraded, and rollback means redeploying the old build (slow, risky). For AI there is more: a new release can include a new prompt, model alias, embedding model, or vector index. Changing the embedding model without re-indexing silently breaks search. Blue-green lets you prepare the whole stack (code + prompt + model + index) and cut over atomically.

## 🔴 यह क्यों बना? (Hindi)
In-place deploy से downtime होता है या system आधा upgrade रहता है, और rollback = पुराना build दोबारा deploy (धीमा, risky)। AI में और भी बातें हैं: release में नया prompt, model alias, embedding model या vector index हो सकता है। Re-index किए बिना embedding model बदलने से search चुपचाप टूट जाता है। Blue-green में पूरा stack (code + prompt + model + index) तैयार करके atomically cut over कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Blue is live and serves 100% traffic
Step 2 → Build green: new code, prompt versions, config, model aliases
Step 3 → Prepare green data: new vector index (re-embedded) or migrated schema, ready and verified
Step 4 → Run smoke tests + offline eval suite + golden-set comparison against green
Step 5 → Warm green (caches, connections, prompt-cache prefixes) so no cold-start spike
Step 6 → Switch the router/load balancer from blue to green (one atomic change)
Step 7 → Watch dashboards: errors, latency, cost, quality metrics, validation failures
Step 8 → Problem? Flip back to blue instantly. Healthy? Keep blue for a while, then retire it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Blue live है और 100% traffic serve करता है
Step 2 → Green बनाओ: नया code, prompt versions, config, model aliases
Step 3 → Green का data तैयार करो: नया vector index (re-embedded) या migrated schema
Step 4 → Smoke tests + offline eval suite + golden-set comparison
Step 5 → Green को warm करो (caches, connections) ताकि cold-start spike न हो
Step 6 → Router/load balancer को blue से green पर switch करो (एक atomic change)
Step 7 → Dashboards देखो: errors, latency, cost, quality, validation failures
Step 8 → गड़बड़ हो तो तुरंत blue पर वापस; ठीक हो तो कुछ समय blue रखकर retire करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team moves to a new embedding model for better recall. The old (blue) index has 1M vectors from the old model; queries embedded by the new model cannot search it. Green gets a fresh index built with the new embeddings, a new reranker setting, and prompt v3. After golden-set evaluation shows better recall@10, traffic flips to green. Blue keeps its old index for 48 hours as an instant rollback.

**Zomato-style**: A new menu-search model is built in green with a fully re-indexed catalogue and activated at a quiet hour.

## 🟡 Real Example Hindi mein
**Tariff System**: बेहतर recall के लिए टीम नया embedding model अपनाती है। पुराने (blue) index में 1M vectors पुराने model के हैं; नए model से embed हुई queries उसमें search नहीं कर सकतीं। Green में नए embeddings से fresh index, नई reranker setting और prompt v3 है। Golden-set पर recall@10 बेहतर दिखे तो traffic green पर जाता है। Blue अपने पुराने index के साथ 48 घंटे instant rollback के लिए रहता है।
**Zomato-style**: Menu-search का नया model green में पूरे re-indexed catalogue के साथ quiet hour में चालू होता है।

---

## 💻 Code Example — Basic
```python
# Blue-green switch with a health gate and instant rollback (pure Python, runs offline)
from dataclasses import dataclass                  # simple environment record

@dataclass
class Env:
    name: str                                      # "blue" or "green"
    version: str                                   # app/prompt/index version label
    healthy: bool = True                           # result of health checks

class Router:
    """Holds which environment is live."""
    def __init__(self, blue: Env, green: Env) -> None:
        self.envs = {"blue": blue, "green": green} # both environments
        self.live = "blue"                         # blue serves traffic first
        self.previous: str | None = None           # remembered for rollback

    def handle(self, text: str) -> str:
        """Route a request to the live environment."""
        env = self.envs[self.live]                 # pick the live env
        return f"[{env.name}/{env.version}] classified: {text}"   # fake response

    def switch(self) -> None:
        """Cut over to the other environment, only if it is healthy."""
        target = "green" if self.live == "blue" else "blue"   # the idle one
        if not self.envs[target].healthy:          # health gate
            raise RuntimeError(f"{target} is not healthy; refusing to switch")
        self.previous, self.live = self.live, target   # atomic swap in memory

    def rollback(self) -> None:
        """Go back to the previous environment."""
        if self.previous is None:                  # nothing to go back to
            raise RuntimeError("no previous environment")
        self.live, self.previous = self.previous, self.live   # swap back

r = Router(Env("blue", "v1"), Env("green", "v2"))  # create the router
print(r.handle("smart phone"))                     # served by blue
r.switch()                                         # cut over
print(r.handle("smart phone"))                     # served by green
r.rollback()                                       # problem found: roll back
print(r.handle("smart phone"))                     # blue again
```

## 💻 Code Example — Advanced
```python
# Cutover orchestrator: golden-set gate, warm-up, post-switch monitoring, auto-rollback (async)
import asyncio                                         # async runtime
from dataclasses import dataclass                      # config/result types
from typing import Awaitable, Callable                 # type hints

Classifier = Callable[[str], Awaitable[str]]           # async fn: text -> hs code

@dataclass
class Gate:
    min_accuracy: float = 0.90                         # golden-set accuracy needed
    max_p95_ms: float = 4000                           # latency ceiling
    max_error_rate: float = 0.02                       # error ceiling after switch

@dataclass
class Result:
    switched: bool                                     # did we cut over
    reason: str                                        # why or why not

async def golden_accuracy(fn: Classifier, golden: list[tuple[str, str]]) -> float:
    """Fraction of golden cases answered correctly (runs concurrently, tolerates errors)."""
    async def one(t: str, want: str) -> bool:
        try:
            return (await asyncio.wait_for(fn(t), 10)) == want   # compare to truth
        except Exception:                              # failure counts as wrong
            return False
    res = await asyncio.gather(*(one(t, w) for t, w in golden))   # run in parallel
    return sum(res) / len(res)                         # accuracy

async def cutover(blue: Classifier, green: Classifier, golden: list[tuple[str, str]],
                  set_live: Callable[[str], None], error_rate_after: Callable[[], Awaitable[float]],
                  gate: Gate = Gate()) -> Result:
    """Verify green, switch, monitor, and roll back automatically if needed."""
    acc_green = await golden_accuracy(green, golden)   # evaluate green
    acc_blue = await golden_accuracy(blue, golden)     # evaluate blue (baseline)
    if acc_green < gate.min_accuracy or acc_green < acc_blue - 0.01:   # not good enough
        return Result(False, f"green accuracy {acc_green:.2f} vs blue {acc_blue:.2f}")
    for t, _ in golden[:5]:                            # warm-up requests (caches, connections)
        await green(t)
    set_live("green")                                  # atomic switch
    await asyncio.sleep(0.1)                           # in production: monitor minutes, not 0.1 s
    err = await error_rate_after()                     # post-switch error rate
    if err > gate.max_error_rate:                      # bad after switching
        set_live("blue")                               # automatic rollback
        return Result(False, f"rolled back: error rate {err:.2%}")
    return Result(True, "green is live")

async def demo() -> None:
    live = {"env": "blue"}                             # fake router state
    async def blue(t: str) -> str: return "8517.13" if "phone" in t else "6109.10"
    async def green(t: str) -> str: return "8517.13" if "phone" in t else "6109.10"
    async def err() -> float: return 0.001             # healthy after switch
    golden = [("smart phone", "8517.13"), ("cotton shirt", "6109.10")] * 3
    print(await cutover(blue, green, golden, lambda e: live.update(env=e), err), live)

if __name__ == "__main__":
    asyncio.run(demo())                                # run
```

---

## 🟠 FastAPI Integration
Expose `/health` and `/ready` per environment and a `/version` endpoint returning code, prompt, model and index versions. The load balancer (or a gateway such as Nginx, an ingress controller, or a cloud LB) switches traffic. Keep readiness false until warm-up and index checks pass. Handle in-flight requests with graceful shutdown.

```python
# FastAPI: versioned, ready-aware service ready for blue-green
import os                                                    # read env vars
from fastapi import FastAPI, HTTPException                   # framework

app = FastAPI()                                              # app
VERSION = {                                                  # versions baked into this environment
    "env": os.getenv("DEPLOY_COLOR", "blue"),
    "code": os.getenv("GIT_SHA", "dev"),
    "prompt": os.getenv("PROMPT_VERSION", "v1"),
    "embedding_model": os.getenv("EMBED_MODEL", "embed-v1"),    # placeholder name
    "index": os.getenv("INDEX_NAME", "tariff-v1"),
}
state = {"warm": False}                                      # becomes True after warm-up

@app.on_event("startup")
async def warm_up() -> None:
    # run a few golden queries to fill caches and check the index
    state["warm"] = True                                     # real code sets this after checks pass

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "alive"}                               # liveness

@app.get("/ready")
async def ready() -> dict[str, str]:
    if not state["warm"]:                                    # not safe for traffic yet
        raise HTTPException(status_code=503, detail="warming up")
    return {"status": "ready"}

@app.get("/version")
async def version() -> dict[str, str]:
    return VERSION                                           # lets you verify which stack answered
```

---

## 🔗 LangChain / LangGraph Connection
Treat the whole chain or graph definition, prompt versions, model aliases, and retriever index names as one versioned artifact per colour. Pin them in config so green never mixes new prompts with old indexes. LangGraph checkpoints (stored threads) must stay compatible: if the graph state schema changes, long-running conversations on blue cannot resume on green unless you migrate state, so version the schema and drain old threads on blue.

```python
# LangChain: build the stack from one version config so blue and green are consistent
from dataclasses import dataclass                            # config record
from langchain_openai import ChatOpenAI                      # chat model
from langchain_core.prompts import ChatPromptTemplate        # prompt

@dataclass(frozen=True)
class StackConfig:
    prompt_text: str                                         # prompt for this release
    model_name: str                                          # model for this release
    index_name: str                                          # vector index for this release

BLUE = StackConfig("HS code for {x}", "gpt-4o-mini", "tariff-v1")
GREEN = StackConfig("Use chapter notes. HS code for {x}", "gpt-4o-mini", "tariff-v2")

def build_chain(cfg: StackConfig):
    return ChatPromptTemplate.from_template(cfg.prompt_text) | ChatOpenAI(model=cfg.model_name)
# retriever = get_retriever(cfg.index_name)  # your function; index must match the embedding model
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Switching the app but not the data (embedding model / index mismatch)
✅ Correct: Ship code, prompt, embedding model and index as one unit.

```python
# Wrong — green uses new embedding model but still queries the old index
query_vec = new_embed(q); index = "tariff-v1"

# Right
cfg = GREEN                       # one config controls everything
query_vec = embed(q, cfg.embedding_model); index = cfg.index_name
```

❌ Mistake 2: Deleting blue right after the switch, or switching without warm-up
✅ Correct: Keep blue for a rollback window, and warm green first.

```python
# Wrong
router.switch(); destroy("blue")

# Right
await warm("green"); router.switch(); monitor(minutes=30); retire("blue", after_hours=48)
```

---

## 🧠 Tricky Interview Question

**Q**: "After a blue-green cutover, the new LLM answers look fine in tests but quality drops in production, and you roll back. Why did the tests miss it, and what does blue-green not protect you from?"

**Answer**: Tests use a small golden set and cannot cover real input diversity; LLM quality problems are statistical and appear on the long tail. Blue-green switches 100% of traffic at once, so all users see the problem before you notice. It gives fast rollback but not gradual exposure. For AI, combine it with shadow traffic (run green on copies of live requests and compare), larger replay evals from logged traffic, and a canary phase (next topic). Also remember side effects: conversations started on green and data it wrote (new indexes, memory, state) may not be readable by blue after rollback, so keep writes backward-compatible.

---

## ⚫ Interview Questions + Answers

Q1: What is blue-green deployment? (Easy)
A1: Two identical environments; deploy and test the new version on the idle one, then switch traffic over and keep the old one for instant rollback.

Q2: Main benefit and main cost? (Easy)
A2: Benefit: near-zero downtime and fast rollback. Cost: you pay for two full environments during the transition.

Q3: What extra things must switch together in an AI release? (Medium)
A3: Prompt versions, model aliases, embedding model and vector index, retrieval settings, guardrail rules, and the schema of stored state. Mismatches cause silent quality loss.

Q4: How do you handle in-flight and long-running requests during the switch? (Medium)
A4: Connection draining: stop sending new requests to blue, let existing ones finish (with a time limit). For long jobs in queues, let blue workers finish theirs while green workers take new ones, and keep job formats compatible.

Q5: How would you re-embed 50M documents for a blue-green cutover without downtime or double-writes drifting? (Hard)
A5: Build the green index in the background from a snapshot, then replay changes (change data capture) made since the snapshot until lag is near zero. Dual-write new documents to both indexes during the transition. Verify with recall tests comparing green against blue and golden queries. Cut over reads, keep dual-write for the rollback window, then stop writing to blue and delete it. Budget embedding cost and rate limits for the bulk job and run it in a queue.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need zero downtime and instant rollback
- The release changes models, indexes, or data formats together
- You can afford duplicate infrastructure temporarily

❌ Avoid when:
- Infrastructure cost for a duplicate stack is too high (consider canary or rolling)
- The change should be exposed to a small share first (use canary)
- Stateful data cannot be shared or migrated safely

---

## 📊 Visual Diagram
```
                 ┌────────── BLUE (v1, live) ──────────┐
Users ─▶ [Router/LB] ───100%──▶ app v1 + prompt v1 + index v1
                 │
                 └─ idle ─── GREEN (v2) app v2 + prompt v2 + index v2
                              ▲ smoke tests, golden eval, warm-up

 SWITCH:  Users ─▶ [Router/LB] ───100%──▶ GREEN (live)
                         BLUE kept idle for rollback (flip back in seconds)
```

---

## 💰 Cost Impact
- Running two stacks doubles infrastructure for the overlap window (hours or days). Illustrative: if serving costs $200/day, a 2-day overlap adds $400.
- AI-specific costs: re-embedding the corpus for the new index (tokens x price: 50M chunks x 300 tokens = 15B tokens; at an illustrative $0.02 per 1M tokens that is about $300), evaluation runs on golden sets (small token cost), and shadow traffic that doubles LLM spend while it runs.
- Optimisations: shadow only a sample (5-10%), use a smaller eval set first, prefer provider batch APIs for re-embedding, and shorten the overlap once metrics are stable.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blue / Green | Live / new environment | Live / नया environment |
| Cutover | Switching traffic | Traffic switch करना |
| Rollback | Return to previous version | पिछले version पर वापसी |
| Warm-up | Prepare caches before traffic | Traffic से पहले तैयारी |
| Connection draining | Let in-flight requests finish | चल रही requests पूरी होने देना |
| Golden set | Trusted test cases | भरोसेमंद test cases |
| Dual-write | Write to both old and new | पुराने और नए दोनों में write |

---

## ⚡ 3-Line Summary
English: Blue-green keeps two environments and switches traffic atomically, with instant rollback. For AI, deploy code, prompts, models and indexes together, test with a golden set, and warm up before cutover. It switches everyone at once, so pair it with shadow tests or canary.
Hindi: Blue-green में दो environments होते हैं और traffic atomically switch होता है, rollback तुरंत। AI में code, prompts, models और indexes साथ deploy करो, golden set से test करो और cutover से पहले warm-up करो। यह सबको एक साथ switch करता है, इसलिए shadow tests या canary साथ रखो।

---

## ➡️ Next Topic
**528. Canary for AI Deploy** — expose the new version to a small slice of traffic first and expand only when the metrics stay healthy.
