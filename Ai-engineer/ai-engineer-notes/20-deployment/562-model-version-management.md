---

# 562. Model Version Management
# हिंदी में: Model Version Management

---

## 🔵 Simple Definition (English)
Model version management means controlling exactly which LLM (and embedding model) your app uses, and changing it deliberately. You pin a specific model identifier, test new versions before switching, and keep the ability to roll back quickly.

## 🔵 सरल परिभाषा (Hindi)
Model version management का मतलब है कि आपका app कौन सा LLM (और embedding model) इस्तेमाल करता है इसे ठीक से control करना और बदलाव सोच-समझकर करना। आप एक specific model identifier pin करते हैं, नए version को switch से पहले test करते हैं और जल्दी rollback की क्षमता रखते हैं।

---

## 🔴 Problem it Solves
Providers update models behind aliases (like "latest") and retire old ones. Behaviour, tone, JSON format and cost can change overnight, breaking your app. Embedding models are worse: if you change one, all stored vectors become incompatible with new query vectors, and retrieval silently breaks.

## 🔴 यह क्यों बना? (Hindi)
Providers aliases (जैसे "latest") के पीछे models बदलते हैं और पुराने बंद करते हैं। Behaviour, tone, JSON format और cost रातों-रात बदल सकते हैं। Embedding models में और बड़ा खतरा: एक बदला तो सारे stored vectors नए query vectors से मेल नहीं खाते और retrieval चुपचाप टूट जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep model ids in config (env / registry), never scattered in code
Step 2 → Pin dated/snapshot ids where the provider offers them (avoid floating aliases in prod)
Step 3 → Record model id + prompt version + embedding model in every log/trace
Step 4 → New model candidate → run eval set + cost/latency comparison
Step 5 → Shadow traffic or canary (e.g. 5%) with live metrics
Step 6 → Promote gradually; keep old id as instant rollback (config flip, no redeploy)
Step 7 → Embedding change → re-embed into a NEW collection, switch alias when ready, delete old later
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Model ids config (env / registry) में रखें, code में बिखरे नहीं
Step 2 → जहाँ provider दे, dated/snapshot ids pin करें; prod में floating alias से बचें
Step 3 → हर log/trace में model id + prompt version + embedding model लिखें
Step 4 → नया candidate → eval set + cost/latency तुलना
Step 5 → Shadow traffic या canary (जैसे 5%) live metrics के साथ
Step 6 → धीरे-धीरे promote; पुराना id instant rollback के लिए
Step 7 → Embedding बदला → NEW collection में re-embed, तैयार होने पर alias switch
```

---

## 🟡 Real World Example
**Tariff Classification System**: The classifier runs `gpt-4o-mini` pinned via `CLASSIFIER_MODEL`. A cheaper candidate is evaluated on 200 labelled invoices: accuracy 91.5% vs 92.0% but 40% cheaper. It goes to 10% canary, metrics hold, then 100%. The embeddings (`text-embedding-3-small`) stay unchanged; upgrading them would require re-embedding the full HS-code database into `hs_codes_v2` and switching an alias.

**Amazon-style**: Search embeddings are versioned; a new index is built offline and swapped atomically.

## 🟡 Real Example Hindi mein
**Tariff System**: Classifier `CLASSIFIER_MODEL` से pinned `gpt-4o-mini` चलाता है। सस्ता candidate 200 labelled invoices पर test: accuracy 91.5% vs 92.0% पर 40% सस्ता। 10% canary, metrics ठीक, फिर 100%। Embeddings बदलने पर पूरा HS-code database `hs_codes_v2` में re-embed करके alias switch करना पड़ेगा।

---

## 💻 Code Example — Basic
```python
# Basic: central model registry loaded from env, with safe defaults
import os  # read environment variables

# One place for every model id the app uses
MODELS: dict[str, str] = {
    "classifier": os.getenv("CLASSIFIER_MODEL", "gpt-4o-mini"),            # chat model
    "embedding": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),   # vector model
}


def model_for(task: str) -> str:
    """Return the model id for a task, failing loudly on typos."""
    try:
        return MODELS[task]                         # look up
    except KeyError:
        raise ValueError(f"unknown task: {task}")   # clear error


print(model_for("classifier"))                       # gpt-4o-mini unless overridden
```

## 💻 Code Example — Advanced
```python
# Advanced: weighted canary routing + metadata stamping + rollback via config reload
import asyncio                                   # async
import hashlib                                   # stable hashing for sticky routing
import json                                      # config parsing
from dataclasses import dataclass                # small data class
from typing import Awaitable, Callable           # types


@dataclass(frozen=True)
class ModelConfig:
    stable: str                                  # current production model id
    candidate: str | None                        # model under test, or None
    candidate_pct: int                           # 0..100 traffic share


def load_config(raw: str) -> ModelConfig:
    """Parse JSON config; invalid config falls back to a safe default."""
    try:
        d = json.loads(raw)                                        # parse
        pct = int(d.get("candidate_pct", 0))                       # share
        if not 0 <= pct <= 100:
            raise ValueError("pct out of range")                   # validate
        return ModelConfig(d["stable"], d.get("candidate"), pct)   # build
    except (ValueError, KeyError, json.JSONDecodeError):
        return ModelConfig("gpt-4o-mini", None, 0)                 # safe fallback


def pick_model(cfg: ModelConfig, user_id: str) -> str:
    """Sticky routing: same user always gets the same arm."""
    if cfg.candidate is None or cfg.candidate_pct == 0:
        return cfg.stable                                          # no experiment
    bucket = int(hashlib.sha256(user_id.encode()).hexdigest(), 16) % 100   # 0..99
    return cfg.candidate if bucket < cfg.candidate_pct else cfg.stable


async def classify(user_id: str, text: str, cfg: ModelConfig,
                   call: Callable[[str, str], Awaitable[str]]) -> dict[str, str]:
    model = pick_model(cfg, user_id)                               # choose arm
    try:
        out = await asyncio.wait_for(call(model, text), timeout=20)   # run model
    except Exception:
        if model != cfg.stable:                                    # candidate failed:
            model = cfg.stable                                     # fall back to stable
            out = await call(model, text)
        else:
            raise                                                  # stable failed: surface it
    return {"answer": out, "model": model}                         # stamp the model used


async def demo_call(model: str, text: str) -> str:
    return f"8517 (by {model})"                                    # fake model call


cfg = load_config('{"stable": "gpt-4o-mini", "candidate": "gpt-4o", "candidate_pct": 10}')
print(asyncio.run(classify("user-1", "phone", cfg, demo_call)))    # offline demo
```

---

## 🟠 FastAPI Integration
Expose the active model in responses and a `/version` route; reload config without redeploy (e.g. from env, SSM Parameter Store or a feature-flag service).

```python
# FastAPI: model stamped in every response, admin reload endpoint
import os                                         # env
from fastapi import FastAPI, Header, HTTPException   # framework

app = FastAPI()                                   # app
STATE: dict[str, str] = {"model": os.getenv("CLASSIFIER_MODEL", "gpt-4o-mini")}


@app.get("/version")
async def version() -> dict[str, str]:
    return dict(STATE)                            # shows pinned model


@app.post("/admin/model")
async def set_model(name: str, x_admin: str = Header(default="")) -> dict[str, str]:
    if x_admin != os.getenv("ADMIN_TOKEN", "change-me"):   # simple guard (use real auth in prod)
        raise HTTPException(status_code=403, detail="forbidden")
    STATE["model"] = name                         # instant switch / rollback
    return dict(STATE)
```

---

## 🔗 LangChain / LangGraph Connection
Build the LLM from config so swapping is a config change. Use `.with_fallbacks([...])` to fall back to another model on error, and `configurable_fields` / `init_chat_model` to choose the model at runtime. Check current LangChain docs for exact signatures.

```python
# LangChain: model chosen from config, with a fallback model
from langchain_openai import ChatOpenAI           # pip install langchain-openai

primary = ChatOpenAI(model="gpt-4o-mini", temperature=0)       # pinned primary
backup = ChatOpenAI(model="gpt-4o", temperature=0)             # stronger fallback
llm = primary.with_fallbacks([backup])                         # retries on failure with backup
# result = await llm.ainvoke("HS code for a laptop?")          # needs OPENAI_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using floating aliases in production
✅ Correct: Pin a specific version/snapshot id and upgrade on purpose.
```python
# Wrong
model = "gpt-4o"            # alias may point to a new snapshot with different behaviour
# Right
model = os.environ["CLASSIFIER_MODEL"]   # e.g. a dated snapshot id, changed only after eval
```

❌ Mistake 2: Changing the embedding model in place
✅ Correct: Re-embed into a new collection and switch an alias.
```python
# Wrong: client.upsert(old_collection, new_model_vectors)   # mixed vector spaces -> garbage search
# Right: build "hs_codes_v2" fully, test, then point alias "hs_codes" -> v2; keep v1 for rollback
```

---

## 🧠 Tricky Interview Question
**Q**: "Provider announces deprecation of your pinned model in 60 days. Embeddings are from the same provider. What is your plan?"

**Answer**: Treat chat and embeddings separately. Chat: eval candidates on the golden set, compare cost/latency, canary, then switch via config. Embeddings: new model means new vector space, so build a parallel collection (re-embed all docs, budget the token cost), evaluate retrieval recall on the new index, dual-read or shadow-test, then flip an alias. Keep the old index until confidence is high. Start early because re-embedding millions of chunks takes time and money.

---

## ⚫ Interview Questions + Answers

Q1: Why pin model versions?
A1: Reproducible behaviour and costs; avoid surprise changes.

Q2: Why log the model id with each request?
A2: To correlate quality or cost changes to a model switch and to debug.

Q3: How do you roll back a bad model change quickly?
A3: Model id lives in config/flags, so flip it back without a redeploy; keep the old version available.

Q4: What is shadow testing?
A4: Send real traffic also to the candidate, discard its output to users, compare offline.

Q5: How to keep prompts and models consistent across versions?
A5: Version prompt+model+params as one release unit, store eval results per unit, and promote the unit together; different models often need prompt tweaks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production app depending on a hosted or self-hosted model
- Multiple environments (dev/staging/prod)

❌ Avoid when:
- Over-engineering a prototype with one model and no users

---

## 📊 Visual Diagram
```
  config: stable=A, candidate=B, pct=10
                │
   request ──► router (hash user_id) ──┬─ 90% ─► model A
                                        └─ 10% ─► model B
                │                              │
                └──── log: model, prompt_v, tokens, latency ◄──┘
   metrics ok? ─► pct 50 ─► 100 ─► stable=B   (A kept for rollback)
   embeddings change ─► NEW collection v2 ─► alias switch
```

---

## 💰 Cost Impact
Model choice dominates token cost. Example (illustrative prices): moving 1M requests/month of 1,000 tokens from a model at $5/M to one at $0.50/M saves roughly $4,500/month. But a bad downgrade that lowers accuracy costs more in rework. Re-embedding cost = total chunk tokens x embedding price, so estimate it before committing. Optimise: eval-driven switches, route easy traffic to cheap models, log tokens per model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pinning | Fixing an exact version | Exact version fix करना |
| Alias | Moving name like "latest" | बदलने वाला नाम |
| Canary | Small-share rollout | थोड़े traffic पर rollout |
| Shadow test | Silent parallel run | चुपचाप parallel run |
| Rollback | Return to old version | पुराने version पर वापस |
| Re-embedding | Recompute all vectors | सारे vectors दोबारा बनाना |

---

## ⚡ 3-Line Summary
English: Pin exact model versions in config and log them on every request. Test candidates with evals, canary them, and keep instant rollback. Changing an embedding model requires re-embedding into a new index.
Hindi: Exact model versions config में pin करें और हर request पर log करें। Candidates को evals से test करें, canary चलाएँ और instant rollback रखें। Embedding model बदलने पर नए index में re-embed करना ज़रूरी है।

---

## ➡️ Next Topic
**563. Prompt Version Control** — the same discipline applied to prompts (already covered in this folder); then move to the interview-problems section starting with **571. Build Basic LLM Chat (FastAPI)**.
