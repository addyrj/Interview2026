---

# 563. Prompt Version Control
# हिंदी में: Prompt Version Control (Prompts का Version Management)

---

## 🔵 Simple Definition (English)
Prompt version control means storing every prompt as a versioned artifact (like code): each change gets an ID, a changelog, an owner, and an eval score. You can roll back, compare, and deploy a prompt without redeploying the whole app.

## 🔵 सरल परिभाषा (Hindi)
Prompt version control का मतलब है हर prompt को code की तरह versioned रखना: हर change का ID, changelog, owner और eval score। इससे आप app दोबारा deploy किए बिना prompt rollback, compare और deploy कर सकते हैं।

---

## 🔴 Problem it Solves
Prompts hidden inside Python strings get edited casually. One "small wording fix" can drop classification accuracy from 92% to 80% and nobody knows which edit did it. Without versions you cannot reproduce an old answer, roll back fast, or A/B test. Prompts are the "source code" of LLM behaviour, so they need the same discipline as code: history, review, tests, rollback.

## 🔴 यह क्यों बना? (Hindi)
Prompts अक्सर Python strings में छुपे होते हैं और कोई भी उन्हें बदल देता है। एक छोटा wording change accuracy 92% से 80% कर सकता है और पता नहीं चलता कौन सा edit था। Versions के बिना पुराना behaviour reproduce, fast rollback या A/B test नहीं हो सकता। Prompt = LLM का source code, इसलिए code जैसा अनुशासन चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Move prompt text out of code into a registry (file, DB, or tool like LangSmith Hub)
Step 2 → Each edit creates a new immutable version (v1, v2, v3) with content hash
Step 3 → Attach metadata: author, date, model, changelog, eval score
Step 4 → Run the eval set (golden questions) on the candidate version
Step 5 → If score >= current production score, promote the version via an alias ("production")
Step 6 → App loads prompt by alias at runtime (cached, with TTL)
Step 7 → Log prompt_version with every LLM call (traceability)
Step 8 → Regression found? Move alias back to the previous version (instant rollback)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Prompt text को code से बाहर registry (file/DB/LangSmith Hub) में रखो
Step 2 → हर edit एक नया immutable version बनाता है (v1, v2, v3) + content hash
Step 3 → Metadata जोड़ो: author, date, model, changelog, eval score
Step 4 → Candidate version पर golden questions का eval चलाओ
Step 5 → Score production से बेहतर हो तो alias ("production") उस version पर ले जाओ
Step 6 → App runtime पर alias से prompt load करता है (cache + TTL)
Step 7 → हर LLM call के साथ prompt_version log करो
Step 8 → Regression मिले तो alias पुराने version पर वापस = instant rollback
```

---

## 🟡 Real World Example
**Tariff Classification System**: The system prompt says "Return the 8-digit HS code with a confidence." A teammate edits it to "be brief" (v4). Accuracy on the 200-item golden set drops from 91% to 84% because the model stops giving the reasoning. Because prompts are versioned, the eval gate blocks v4, and the `production` alias stays on v3. Every API response logs `prompt_version=v3`, so a customer complaint can be replayed exactly.

**Zomato-style**: The "dish description" prompt is A/B tested: 90% traffic on v7, 10% on v8; keep v8 only if click-through improves.

## 🟡 Real Example Hindi mein
**Tariff System**: System prompt में लिखा है "8-digit HS code और confidence दो"। कोई teammate इसे "brief रहो" (v4) कर देता है। 200 golden items पर accuracy 91% से 84% हो जाती है क्योंकि model reasoning देना बंद कर देता है। Versioning होने से eval gate v4 को रोक देता है और `production` alias v3 पर रहता है। हर response में `prompt_version=v3` log होता है, इसलिए customer complaint replay हो सकती है।

**Zomato-style**: Dish description prompt पर A/B test: 90% traffic v7 पर, 10% v8 पर; click-through बढ़े तभी v8 रखो।

---

## 💻 Code Example — Basic
```python
# Basic in-memory prompt registry (pure Python, runs directly)
import hashlib                                   # to create a content hash per version
from dataclasses import dataclass, field         # simple data container
from datetime import datetime, timezone          # timestamps for audit trail


@dataclass(frozen=True)                          # frozen = immutable, versions never change
class PromptVersion:
    name: str                                    # prompt name, e.g. "tariff_classifier"
    version: int                                 # 1, 2, 3 ...
    template: str                                # the prompt text with {placeholders}
    changelog: str                               # why this version exists
    created_at: str                              # ISO timestamp
    sha: str                                     # short hash of the template


@dataclass
class PromptRegistry:
    store: dict[str, list[PromptVersion]] = field(default_factory=dict)   # name -> versions
    aliases: dict[tuple[str, str], int] = field(default_factory=dict)     # (name, alias) -> version

    def add(self, name: str, template: str, changelog: str) -> PromptVersion:
        versions = self.store.setdefault(name, [])                        # get or create list
        sha = hashlib.sha256(template.encode()).hexdigest()[:8]           # content fingerprint
        pv = PromptVersion(name, len(versions) + 1, template, changelog,
                           datetime.now(timezone.utc).isoformat(), sha)   # build new version
        versions.append(pv)                                               # append, never overwrite
        return pv

    def promote(self, name: str, version: int, alias: str = "production") -> None:
        if not any(v.version == version for v in self.store.get(name, [])):
            raise ValueError(f"{name} v{version} does not exist")        # guard bad promote
        self.aliases[(name, alias)] = version                             # move alias pointer

    def get(self, name: str, alias: str = "production") -> PromptVersion:
        version = self.aliases[(name, alias)]                             # KeyError if no alias
        return self.store[name][version - 1]                              # versions are 1-based


reg = PromptRegistry()                                                    # create registry
reg.add("tariff", "Classify {item}. Give HS code + reasoning.", "initial")
reg.add("tariff", "Classify {item}. Be brief.", "shorter (worse!)")
reg.promote("tariff", 1)                                                  # v1 is production
print(reg.get("tariff").version, reg.get("tariff").sha)                   # prints 1 and a hash
reg.promote("tariff", 2)                                                  # deploy v2
reg.promote("tariff", 1)                                                  # instant rollback
print("after rollback:", reg.get("tariff").version)                       # prints 1
```

## 💻 Code Example — Advanced
```python
# Production style: file-backed registry, TTL cache, eval gate, async loader
from __future__ import annotations
import asyncio                                   # async support
import json                                      # persist registry as JSON
import time                                      # TTL cache clock
from pathlib import Path                         # filesystem paths
from typing import Awaitable, Callable           # type hints for the eval function


class PromptNotFound(Exception):
    """Raised when a prompt or alias is missing."""


class FilePromptStore:
    """Stores {name: {"versions": [...], "aliases": {...}}} in one JSON file."""

    def __init__(self, path: Path, ttl_seconds: float = 60.0) -> None:
        self.path = path                                          # JSON file location
        self.ttl = ttl_seconds                                    # cache lifetime
        self._cache: dict[tuple[str, str], tuple[float, str]] = {}  # key -> (loaded_at, text)

    def _read(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))  # load file
        except FileNotFoundError:
            return {}                                                 # empty registry
        except json.JSONDecodeError as exc:
            raise PromptNotFound(f"corrupt registry: {exc}") from exc  # clear error

    def _write(self, data: dict) -> None:
        tmp = self.path.with_suffix(".tmp")                           # write to temp first
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")  # serialise
        tmp.replace(self.path)                                        # atomic swap

    def publish(self, name: str, template: str, changelog: str) -> int:
        data = self._read()                                           # current state
        entry = data.setdefault(name, {"versions": [], "aliases": {}})  # create if new
        entry["versions"].append({"template": template, "changelog": changelog})
        self._write(data)                                             # persist
        return len(entry["versions"])                                 # new version number

    def promote(self, name: str, version: int, alias: str = "production") -> None:
        data = self._read()
        if name not in data or version > len(data[name]["versions"]):
            raise PromptNotFound(f"{name} v{version}")                # reject unknown
        data[name]["aliases"][alias] = version                        # move pointer
        self._write(data)
        self._cache.pop((name, alias), None)                          # invalidate cache

    def load(self, name: str, alias: str = "production") -> tuple[int, str]:
        now = time.monotonic()                                        # monotonic clock
        hit = self._cache.get((name, alias))                          # cached?
        if hit and now - hit[0] < self.ttl:
            version, text = json.loads(hit[1])                        # cached JSON pair
            return version, text
        data = self._read()
        try:
            version = data[name]["aliases"][alias]                    # resolve alias
            text = data[name]["versions"][version - 1]["template"]    # get text
        except (KeyError, IndexError) as exc:
            raise PromptNotFound(f"{name}@{alias}") from exc
        self._cache[(name, alias)] = (now, json.dumps([version, text]))  # store
        return version, text

    async def aload(self, name: str, alias: str = "production") -> tuple[int, str]:
        return await asyncio.to_thread(self.load, name, alias)       # file IO off the event loop


EvalFn = Callable[[str], Awaitable[float]]                            # template -> accuracy 0..1


async def promote_if_better(store: FilePromptStore, name: str, candidate: int,
                            eval_fn: EvalFn, margin: float = 0.0) -> bool:
    """Eval gate: promote candidate only if it beats production."""
    _, prod_text = await store.aload(name, "production")              # current prod text
    data = await asyncio.to_thread(store._read)                       # read registry off-loop
    cand_text = data[name]["versions"][candidate - 1]["template"]
    prod_score, cand_score = await asyncio.gather(eval_fn(prod_text), eval_fn(cand_text))
    if cand_score >= prod_score + margin:                             # beat production?
        store.promote(name, candidate)                                # deploy
        return True
    return False                                                      # blocked
```

---

## 🟠 FastAPI Integration
Load the prompt by alias on each request (cached), and return `prompt_version` so every answer is traceable. An admin route moves the alias (rollback without redeploy).

```python
from fastapi import FastAPI, HTTPException            # web framework
from pathlib import Path                              # path for registry
from pydantic import BaseModel                        # request validation

app = FastAPI()                                       # app instance
store = FilePromptStore(Path("prompts.json"))         # from the Advanced example


class ClassifyReq(BaseModel):
    item: str                                         # product description


class RollbackReq(BaseModel):
    name: str                                         # prompt name
    version: int                                      # version to point production at


@app.post("/classify")
async def classify(req: ClassifyReq) -> dict:
    try:
        version, template = await store.aload("tariff")        # resolve production alias
    except PromptNotFound as exc:
        raise HTTPException(status_code=500, detail=str(exc))  # misconfigured registry
    prompt = template.format(item=req.item)                    # fill placeholders
    # answer = await llm.ainvoke(prompt)  # real call goes here
    return {"prompt_version": version, "prompt": prompt}       # log version for tracing


@app.post("/admin/rollback")
async def rollback(req: RollbackReq) -> dict:
    try:
        await asyncio.to_thread(store.promote, req.name, req.version)  # move alias
    except PromptNotFound:
        raise HTTPException(status_code=404, detail="unknown version")
    return {"production": req.version}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `PromptTemplate` / `ChatPromptTemplate` are the runtime objects; versioning is done around them. LangSmith has a Prompt Hub (`client.pull_prompt("tariff:production")`) with commit hashes and tags. In LangGraph, each node that calls an LLM should record the prompt version in its state so traces show which version produced which output.

```python
from langchain_core.prompts import ChatPromptTemplate   # runtime prompt object

version, text = store.load("tariff")                     # from our registry
prompt = ChatPromptTemplate.from_messages([
    ("system", text),                                    # versioned system text
    ("human", "{item}"),                                 # user input
])
# chain = prompt | llm ; result = chain.invoke({"item": "iPhone 15"},
#     config={"metadata": {"prompt_version": version}})  # shows up in LangSmith traces
```
(Hub API names can change between releases; treat `pull_prompt` usage as illustrative and check current docs.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Editing the live prompt in place
✅ Correct: publish a new immutable version and move an alias.

```python
# Wrong — history lost, no rollback:
PROMPT = "Classify the item."      # edited directly in code, then redeployed

# Right — new version + gated promotion:
v = store.publish("tariff", "Classify the item with reasoning.", "add reasoning")
# run eval, then store.promote("tariff", v)
```

❌ Mistake 2: Not logging which version answered
✅ Correct: attach `prompt_version` (and model name) to every log/trace line.

```python
# Wrong
logger.info("answered")
# Right
logger.info("answered", extra={"prompt_version": version, "model": "gpt-4o-mini"})
```

❌ Mistake 3: Changing prompt and model together, then you cannot tell which caused the regression. Change one thing at a time.

---

## 🧠 Tricky Interview Question
**Q**: "You rolled back the prompt to v3 but users still see v4 behaviour for several minutes. Why, and how do you fix it?"

**Answer**: The app caches prompts with a TTL, and each replica has its own cache. Rollback moved the alias in the store, but replicas keep the old text until the TTL expires. Fixes: short TTL (30-60 s), cache invalidation via pub/sub or a version-poll endpoint, or include the version in the cache key and read the alias version cheaply on each request. Also confirm no in-flight conversation pinned itself to v4 (sticky versions per session are sometimes intentional).

---

## ⚫ Interview Questions + Answers

Q1: Why version prompts at all?
A1: Prompts change model behaviour as much as code does. Versioning gives history, review, rollback, reproducibility and A/B testing.

Q2: What is a prompt alias?
A2: A movable name like `production` or `staging` that points to a specific immutable version. Deploy and rollback are just alias moves.

Q3: Where should prompts live: code repo or a registry?
A3: Repo (Git) gives review and CI but needs redeploy. A registry or DB allows fast changes and rollback but needs access control and audit. Many teams keep prompts in Git, run evals in CI, and sync to a registry for runtime.

Q4: How do you test a new prompt version safely?
A4: Run it on a golden eval set (with LLM-as-judge or exact-match metrics), then shadow traffic or a canary (5-10%), compare quality, latency and cost, and only then promote.

Q5: (Hard) How do you handle prompts that depend on a specific model version?
A5: Store model name and parameters (temperature, max_tokens) in the version metadata, treat (prompt, model, params) as one deployable unit, and re-run evals whenever the provider updates the model. Pin dated model snapshots where available so behaviour does not drift silently.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prompts affect revenue or compliance (Tariff classification)
- Multiple people edit prompts
- You need A/B tests, audit trails, or fast rollback

❌ Avoid when:
- One-off script or prototype with a single throwaway prompt
- Heavy tooling would cost more than the risk (simple Git file is enough)

---

## 📊 Visual Diagram
```
 Editor ──► new version v4 ──► Eval gate (golden set)
                                   │ pass            │ fail
                                   ▼                 ▼
                          alias: production→v4   stay on v3
                                   │
 App (cache, TTL) ◄── load by alias┘
   │
   └─► LLM call + log(prompt_version=v4) ──► Trace / Monitoring
 Rollback: alias production → v3 (no redeploy)
```

---

## 💰 Cost Impact
- Versioning itself costs ~0 tokens. Savings come from catching bad prompts early: a verbose prompt that adds 300 tokens to every call at 1M calls/month adds 300M input tokens (about $45 at an illustrative $0.15/1M).
- Optimise: track tokens per prompt version in your eval report, reject versions that grow tokens without quality gain, keep static prefixes stable so provider prompt caching works (editing the prefix breaks the cache).
- Prices are illustrative; check the provider's pricing page.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prompt version | Immutable snapshot of a prompt | Prompt का fixed snapshot |
| Alias | Movable pointer like "production" | Version की तरफ इशारा करने वाला नाम |
| Rollback | Return to a previous version | पुराने version पर वापस जाना |
| Eval gate | Automatic quality check before deploy | Deploy से पहले quality check |
| Golden set | Fixed test questions with expected answers | Fixed test सवाल-जवाब |
| Changelog | Reason for a change | बदलाव का कारण |

---

## ⚡ 3-Line Summary
English: Treat prompts like code: immutable versions, changelog, eval gate, and aliases for deploy and rollback. Log the prompt version on every call so any answer can be traced and reproduced. Cache with a short TTL so rollbacks take effect fast.
Hindi: Prompts को code की तरह रखो: immutable versions, changelog, eval gate और deploy/rollback के लिए aliases। हर call पर prompt version log करो ताकि हर answer trace हो सके। Cache का TTL छोटा रखो ताकि rollback जल्दी लागू हो।

---

## ➡️ Next Topic
**564. Blue-Green AI Deployment** — after versioning prompts, learn how to switch whole AI stacks (model + prompt + index) with zero downtime and instant rollback.
