---

# 526. Feature Flags for AI
# हिंदी में: AI के लिए Feature Flags

---

## 🔵 Simple Definition (English)
A feature flag is a runtime switch (config value) that turns a feature, prompt version, or model on or off, for everyone or for chosen users, without redeploying code. For AI it works as a kill switch, a gradual rollout tool, and a way to change models and prompts safely.

## 🔵 सरल परिभाषा (Hindi)
Feature flag एक runtime switch (config value) है जो किसी feature, prompt version या model को code redeploy किए बिना सबके लिए या चुने हुए users के लिए on/off करता है। AI में यह kill switch, धीरे-धीरे rollout और model/prompt को safely बदलने का tool है।

---

## 🔴 Problem it Solves
Prompts, models, and thresholds change often, and a bad change can cause hallucinations, high costs, or unsafe output right now. Redeploying takes minutes to hours. Flags separate deploy from release: code ships dark, and you turn it on gradually and off instantly when metrics go bad.

## 🔴 यह क्यों बना? (Hindi)
Prompts, models और thresholds अक्सर बदलते हैं और खराब change से अभी hallucination, ज़्यादा cost या unsafe output आ सकता है। Redeploy में मिनट से घंटे लगते हैं। Flags deploy और release को अलग करते हैं: code चुपचाप ship होता है, धीरे-धीरे on होता है और metrics खराब होने पर तुरंत off।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a flag with a name, type (bool/string/number), default and owner
Step 2 → Store flags in a config service (LaunchDarkly, Unleash, Flagsmith, or your DB/Redis)
Step 3 → App evaluates the flag per request with context (user, tenant, plan, region)
Step 4 → Rules: percentage rollout, allow-lists, tenant plan, kill switch
Step 5 → Code branches on the flag (new prompt vs old, model alias, feature on/off)
Step 6 → Cache flag values locally and refresh often; ALWAYS keep a safe default if the flag service is down
Step 7 → Log flag values in traces so you know what version produced an answer
Step 8 → Remove old flags after rollout (flag debt)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Flag define करो: नाम, type (bool/string/number), default, owner
Step 2 → Flags config service में रखो (LaunchDarkly, Unleash, Flagsmith, या अपना DB/Redis)
Step 3 → हर request पर context (user, tenant, plan, region) के साथ flag evaluate
Step 4 → Rules: percentage rollout, allow-list, tenant plan, kill switch
Step 5 → Code flag पर branch करे (नया/पुराना prompt, model alias, feature on/off)
Step 6 → Flag values local cache करो और जल्दी refresh करो; service down हो तो safe default
Step 7 → Traces में flag values log करो
Step 8 → Rollout के बाद पुराने flags हटाओ (flag debt)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Flags: `classifier.prompt_version` ("v1" / "v2"), `classifier.model` ("small" / "strong"), `classifier.auto_file_enabled` (kill switch), `rag.use_reranker`. On Monday a new model alias is released to 5% of tenants. On Tuesday the flag service sets `auto_file_enabled=false` within seconds after brokers report wrong HS codes, with no deployment.

**Amazon-style**: AI-generated product summaries are enabled per country and per category, and switched off for a category when quality reports spike.

## 🟡 Real Example Hindi mein
**Tariff System**: Flags: `classifier.prompt_version` ("v1"/"v2"), `classifier.model` ("small"/"strong"), `classifier.auto_file_enabled` (kill switch), `rag.use_reranker`। सोमवार को नया model alias 5% tenants को। मंगलवार को brokers के गलत HS codes की रिपोर्ट पर flag service `auto_file_enabled=false` कर देती है, कुछ seconds में, बिना deployment।
**Amazon-style**: AI product summaries country और category के हिसाब से on होती हैं और quality reports बढ़ने पर उस category में off।

---

## 💻 Code Example — Basic
```python
# Tiny feature-flag system (pure Python, runs offline)
import hashlib                                    # stable percentage bucketing
from dataclasses import dataclass, field          # flag definition

@dataclass
class Flag:
    name: str                                     # flag name
    enabled: bool = True                          # master switch (kill switch)
    percent: int = 100                            # rollout percent 0..100
    allow: set[str] = field(default_factory=set)  # users/tenants always on
    value: str = "on"                             # value to return when on
    default: str = "off"                          # value when off

FLAGS: dict[str, Flag] = {                        # in production: loaded from a service
    "classifier.prompt_version": Flag("classifier.prompt_version", percent=20, allow={"tenant-vip"}, value="v2", default="v1"),
    "classifier.auto_file": Flag("classifier.auto_file", enabled=True, value="true", default="false"),
}

def bucket(flag: str, key: str) -> int:
    """Stable number 0..99 for (flag, key)."""
    return int(hashlib.sha256(f"{flag}:{key}".encode()).hexdigest()[:8], 16) % 100

def get(flag_name: str, key: str) -> str:
    """Evaluate a flag for a user/tenant key; unknown flags return a safe default."""
    f = FLAGS.get(flag_name)                      # look up the flag
    if f is None or not f.enabled:                # missing or killed
        return f.default if f else "off"          # safe default
    if key in f.allow or bucket(flag_name, key) < f.percent:   # allow-list or in rollout
        return f.value                            # new behaviour
    return f.default                              # old behaviour

users = [f"tenant-{i}" for i in range(1000)] + ["tenant-vip"]   # sample users
on = sum(get("classifier.prompt_version", u) == "v2" for u in users)   # count v2 users
print(f"{on}/{len(users)} on v2 (about 20% + vip)")              # about 20%
FLAGS["classifier.prompt_version"].enabled = False               # flip the kill switch
print(get("classifier.prompt_version", "tenant-vip"))            # everyone back to v1
```

## 💻 Code Example — Advanced
```python
# Flag client: cached refresh, safe defaults, context rules, async (type hints, error handling)
import asyncio                                           # async runtime
import hashlib                                           # bucketing
import time                                              # cache age
from typing import Any, Awaitable, Callable              # type hints

Fetcher = Callable[[], Awaitable[dict[str, dict[str, Any]]]]   # returns all flag configs

class FlagClient:
    def __init__(self, fetch: Fetcher, ttl_s: float = 5.0) -> None:
        self.fetch = fetch                               # remote source (HTTP/Redis/DB)
        self.ttl = ttl_s                                 # refresh interval
        self.cache: dict[str, dict[str, Any]] = {}       # last good config
        self.fetched_at = 0.0                            # when we last refreshed
        self._lock = asyncio.Lock()                      # one refresh at a time

    async def _refresh(self) -> None:
        """Refresh the cache; on failure keep the last good copy."""
        async with self._lock:                           # avoid a stampede
            if time.monotonic() - self.fetched_at < self.ttl:   # someone refreshed already
                return
            try:
                self.cache = await asyncio.wait_for(self.fetch(), 1.0)   # tight timeout
                self.fetched_at = time.monotonic()       # mark fresh
            except Exception:                            # flag service down
                self.fetched_at = time.monotonic() - self.ttl + 1   # retry in ~1s, keep serving stale
                # IMPORTANT: never crash the request because flags are unavailable

    async def get(self, name: str, ctx: dict[str, str], default: Any) -> Any:
        """Evaluate a flag with context (tenant, plan, user)."""
        if time.monotonic() - self.fetched_at >= self.ttl:   # stale?
            await self._refresh()                        # refresh
        cfg = self.cache.get(name)                       # flag config
        if not cfg or not cfg.get("enabled", False):     # missing/killed
            return default                               # safe default
        if ctx.get("tenant") in cfg.get("deny", []):     # explicit deny list
            return default
        if ctx.get("plan") in cfg.get("plans", []) or ctx.get("tenant") in cfg.get("allow", []):
            return cfg["value"]                          # targeted rule
        h = int(hashlib.sha256(f"{name}:{ctx.get('tenant', '')}".encode()).hexdigest()[:8], 16) % 100
        return cfg["value"] if h < cfg.get("percent", 0) else default   # percentage rollout

async def demo() -> None:
    async def fetch() -> dict[str, dict[str, Any]]:      # fake remote config
        return {"classifier.model": {"enabled": True, "value": "strong", "percent": 10, "plans": ["enterprise"]}}
    fc = FlagClient(fetch)                               # client
    print(await fc.get("classifier.model", {"tenant": "acme", "plan": "enterprise"}, "small"))   # strong (plan rule)
    print(await fc.get("classifier.model", {"tenant": "tiny", "plan": "free"}, "small"))         # mostly small
    print(await fc.get("unknown.flag", {"tenant": "x"}, "small"))                                # default

if __name__ == "__main__":
    asyncio.run(demo())                                  # run
```

---

## 🟠 FastAPI Integration
Evaluate flags in a dependency so every route gets the same context, and put the flag values into response headers and logs. Admin endpoints (protected!) may flip flags in a real setup, but usually a flag service does that.

```python
# FastAPI: flags via dependency injection
from fastapi import Depends, FastAPI, Header                 # framework
from pydantic import BaseModel                               # validation

app = FastAPI()                                              # app
flags = FlagClient(fetch=load_flags_from_service)            # load_flags_from_service = your async fetcher

class Req(BaseModel):
    description: str                                         # product text

async def ctx(x_tenant: str = Header(...), x_plan: str = Header("free")) -> dict[str, str]:
    return {"tenant": x_tenant, "plan": x_plan}              # evaluation context

@app.post("/classify")
async def classify(req: Req, c: dict[str, str] = Depends(ctx)) -> dict:
    prompt_v = await flags.get("classifier.prompt_version", c, "v1")   # which prompt
    model = await flags.get("classifier.model", c, "small")            # which model
    auto = await flags.get("classifier.auto_file", c, False)           # kill switch for auto-filing
    answer = await run_classifier(req.description, prompt_v, model)    # your pipeline function
    return {"answer": answer, "prompt": prompt_v, "model": model, "auto_file": bool(auto)}
```

---

## 🔗 LangChain / LangGraph Connection
Resolve flags before building the chain: choose the prompt template and model by flag value, and pass them as `metadata` so traces show the version. In LangGraph store flag values in state at the entry node and use conditional edges (for example `use_reranker` true or false, `human_review_required`). Avoid evaluating flags deep inside tools without context.

```python
# LangChain: choose prompt/model by flag value, attach to the trace
from langchain_core.prompts import ChatPromptTemplate         # prompts
from langchain_openai import ChatOpenAI                       # model wrapper

PROMPTS = {"v1": "HS code for {x}", "v2": "Use chapter notes. HS code for {x}"}   # versioned prompts
MODELS = {"small": "gpt-4o-mini", "strong": "gpt-4o"}                              # example names

async def run(x: str, prompt_v: str, model_alias: str) -> str:
    chain = ChatPromptTemplate.from_template(PROMPTS[prompt_v]) | ChatOpenAI(model=MODELS[model_alias])
    msg = await chain.ainvoke({"x": x}, config={"metadata": {"prompt_v": prompt_v, "model": model_alias}})
    return msg.content                                         # flag values are in the trace
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No safe default when the flag service fails
✅ Correct: Fail to the known-good behaviour and keep the last cached value.

```python
# Wrong — flag service timeout crashes every request
value = requests.get(FLAG_URL).json()["value"]

# Right
try:
    value = await asyncio.wait_for(fetch_flag(), 0.3)
except Exception:
    value = LAST_KNOWN.get(name, SAFE_DEFAULT)
```

❌ Mistake 2: Leaving flags forever and untracked
✅ Correct: Give each flag an owner and expiry, delete after full rollout.

```python
# Wrong — 200 stale flags nobody understands
if flag("old_experiment_2022"): ...

# Right — cleanup after 100% rollout
result = new_path()     # flag deleted from code and config, ticket closed
```

---

## 🧠 Tricky Interview Question

**Q**: "You roll out prompt v2 to 20% of users with a flag. Support finds that the same user sometimes gets v1 and sometimes v2 in one conversation. Why, and how do you fix it?"

**Answer**: Bucketing is probably per request (random) or uses an unstable key (session ID that changes, request ID). Use a stable hash of the user or conversation ID plus the flag name, and keep it fixed through the conversation (sticky assignment). Also watch for cached flag values differing across servers during refresh; use short TTLs and include the flag version in traces. For multi-step agents capture flag values once at the start of the run and pass them down, so a mid-run flip does not mix versions.

---

## ⚫ Interview Questions + Answers

Q1: What is a feature flag? (Easy)
A1: A runtime config switch that enables or disables behaviour without redeploying code.

Q2: Why do AI systems especially need kill switches? (Easy)
A2: Model behaviour can fail in ways tests miss (hallucination, unsafe output, cost spikes). A kill switch lets you disable or downgrade the feature in seconds.

Q3: What is the difference between deploy and release? (Medium)
A3: Deploy puts code in production; release exposes it to users. Flags let you deploy dark and release gradually, then roll back by flipping the flag.

Q4: How do flags relate to A/B tests and canaries? (Medium)
A4: Flags are the mechanism. A/B tests use flags for random assignment plus measurement. Canary releases use flags (or traffic routing) to expose a small percentage while watching guardrails.

Q5: Design a flag system for 1,000 tenants with prompt versions that must be reproducible for audits. (Hard)
A5: Store immutable prompt versions in a registry; flags reference a version ID per tenant or percentage. Evaluate with local caching and streaming updates, log the resolved flag values and versions in every trace and response record, keep audit logs of who changed which flag and when, require approvals for production flags, support per-tenant pinning for regulated customers, and provide instant global kill switches with a safe default if the flag service is unreachable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Rolling out new prompts, models, tools or features gradually
- You need an instant kill switch
- Different tenants or plans need different behaviour

❌ Avoid when:
- It would create combinatorial complexity (too many interacting flags to test)
- A permanent config setting is more honest than a "temporary" flag

---

## 📊 Visual Diagram
```
Flag service (rules: kill switch, %, allow-list, plan)
        │  refresh every few seconds (cached locally, safe default on failure)
        ▼
Request + context(tenant, plan) ─▶ evaluate flag ─┬─▶ prompt v1 / model small  (old)
                                                  └─▶ prompt v2 / model strong (new)
                                       │
                        log flag values in trace ─▶ metrics ─▶ rollout 5% → 25% → 100%
                                                     (bad? flip kill switch → back to old)
```

---

## 💰 Cost Impact
- Flags cut cost by letting you roll new expensive models out to a small share first and watching spend before scaling. Illustrative: a new strong model for all 1M monthly calls could add $3,000; a 5% rollout adds $150 while you measure.
- Flag evaluation itself is nearly free if cached locally; the cost is a flag service subscription (check vendor pricing) or building your own.
- Flags can cap token spend: for example `max_output_tokens` and `context_chunks` as number flags tuned live. Use a cost kill switch that disables expensive features when daily spend exceeds budget.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Feature flag | Runtime on/off switch | Runtime on/off switch |
| Kill switch | Instant disable | तुरंत बंद करने का switch |
| Gradual rollout | Increase exposure in steps | धीरे-धीरे exposure बढ़ाना |
| Sticky assignment | Same user keeps same variant | User को वही variant मिलना |
| Dark launch | Deploy without releasing | Deploy पर release नहीं |
| Targeting rule | Who gets the flag | किसे flag मिलेगा |
| Flag debt | Old flags left in code | पुराने बचे हुए flags |

---

## ⚡ 3-Line Summary
English: Feature flags let you change prompts, models and features at runtime, roll out gradually, and kill instantly without redeploying. Always keep safe defaults, sticky assignment and flag values in traces. Clean up old flags after rollout.
Hindi: Feature flags से prompts, models और features runtime पर बदलते हैं, धीरे-धीरे rollout होता है और बिना redeploy तुरंत kill किया जा सकता है। Safe defaults, sticky assignment और traces में flag values रखो। Rollout के बाद पुराने flags हटाओ।

---

## ➡️ Next Topic
**527. Blue-Green for AI Deploy** — a deployment pattern that keeps two full environments so you can switch traffic and roll back in one step.
