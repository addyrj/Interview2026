
---

# 457. Multi-tenant Caching
# हिंदी में: Multi-tenant Caching

---

## 🔵 Simple Definition (English)
Multi-tenant caching means one cache serves many customers (tenants) while keeping their data separate. Every key and every vector entry carries the tenant ID, and every lookup is filtered by it, so tenant A can never receive tenant B's cached answer. You may also share a **global** cache for public, non-sensitive answers.

## 🔵 सरल परिभाषा (Hindi)
Multi-tenant caching में एक cache कई customers (tenants) को serve करता है, पर उनका data अलग रहता है। हर key और vector entry में tenant ID होती है और हर lookup उसी से filter होता है, इसलिए tenant A को कभी tenant B का cached answer नहीं मिलता। Public, non-sensitive answers के लिए एक **global** shared cache भी रख सकते हैं।

---

## 🔴 Problem it Solves
A SaaS tariff product serves many importers. Their prompts include private data (shipment details, prices, supplier names). A shared cache without tenant isolation can return Company A's answer to Company B: a data leak and often a contract breach. Also, one noisy tenant could fill the cache and evict everyone else's entries.

## 🔴 यह क्यों बना? (Hindi)
Tariff SaaS कई importers को serve करता है। उनके prompts में private data होता है (shipment details, prices, supplier names)। बिना isolation वाला shared cache Company A का answer Company B को दे सकता है: data leak और अक्सर contract का उल्लंघन। साथ ही एक noisy tenant पूरा cache भरकर बाकियों की entries निकाल सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Authenticate request → derive tenant_id from the token (never from the body)
Step 2 → Build key: "cache:{tenant_id}:{version}:{hash(normalised prompt)}"
Step 3 → Lookup only inside that tenant's namespace (or filter on tenant_id)
Step 4 → Public/global questions: optional shared namespace "cache:global:..."
Step 5 → Per-tenant quotas, TTLs and max memory to stop noisy neighbours
Step 6 → Per-tenant invalidation: delete by prefix / filter when data changes
Step 7 → Audit: log hits with tenant_id for investigations
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request authenticate करो → tenant_id token से लो (body से कभी नहीं)
Step 2 → Key बनाओ: "cache:{tenant_id}:{version}:{hash(prompt)}"
Step 3 → Lookup सिर्फ़ उस tenant के namespace में (या tenant_id filter)
Step 4 → Public सवालों के लिए optional shared namespace "cache:global:..."
Step 5 → Per-tenant quota, TTL और memory limit रखो
Step 6 → Per-tenant invalidation: prefix / filter से delete
Step 7 → Audit: tenant_id के साथ hits log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importer A has a negotiated duty-drawback rule in its prompt context; importer B does not. Their cache keys include `tenant_id`, so each gets the right answer. General "what is HS 8517" explanations go to the global namespace and are shared, saving money for everyone. **Amazon-style**: seller-specific answers ("my return rate") are per tenant, while product-catalogue FAQs are global.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer A के context में negotiated duty-drawback rule है, B के पास नहीं। Keys में `tenant_id` होती है, इसलिए दोनों को सही answer मिलता है। "HS 8517 क्या है" जैसी general explanations global namespace में shared होती हैं और सबका पैसा बचता है। **Amazon-style**: seller-specific answers per tenant, catalogue FAQs global।

---

## 💻 Code Example — Basic
```python
# Basic: tenant-isolated cache with a global fallback (pure Python)
import hashlib                                             # stable hashing

store: dict[str, str] = {}                                 # one dict, namespaced keys

def make_key(tenant: str, prompt: str) -> str:
    digest = hashlib.sha256(prompt.lower().strip().encode()).hexdigest()[:16]  # short hash
    return f"cache:{tenant}:{digest}"                      # tenant is part of the key

def get(tenant: str, prompt: str, public: bool = False) -> str | None:
    scope = "global" if public else tenant                 # public answers are shared
    return store.get(make_key(scope, prompt))              # lookup in that scope only

def put(tenant: str, prompt: str, answer: str, public: bool = False) -> None:
    scope = "global" if public else tenant                 # choose namespace
    store[make_key(scope, prompt)] = answer                # write

put("acme", "our duty rate?", "5% (acme contract)")        # private to acme
put("acme", "what is HS 8517?", "Telephones...", public=True)   # shared
print(get("globex", "our duty rate?"))                     # None: no leak
print(get("globex", "what is HS 8517?", public=True))      # shared answer
```

## 💻 Code Example — Advanced
```python
# Production: Redis-backed per-tenant cache with quota, TTL and prefix invalidation (async)
# pip install redis
import hashlib                                             # hashing
import json                                                # serialise values
from typing import Optional                                # type hints
import redis.asyncio as redis                              # async Redis client

class TenantCache:
    def __init__(self, url: str = "redis://localhost:6379/0", max_keys_per_tenant: int = 10_000) -> None:
        self.r = redis.from_url(url, decode_responses=True)    # async client
        self.max_keys = max_keys_per_tenant                # quota per tenant

    @staticmethod
    def _key(tenant: str, version: str, prompt: str) -> str:
        h = hashlib.sha256(prompt.lower().strip().encode()).hexdigest()   # full hash
        return f"cache:{tenant}:{version}:{h}"             # namespaced key

    async def get(self, tenant: str, version: str, prompt: str) -> Optional[dict]:
        try:
            raw = await self.r.get(self._key(tenant, version, prompt))   # fetch
            return json.loads(raw) if raw else None        # decode JSON
        except Exception:
            return None                                    # cache failure = miss

    async def set(self, tenant: str, version: str, prompt: str, value: dict, ttl: int = 86_400) -> bool:
        try:
            counter = f"count:{tenant}"                    # per-tenant key counter
            if int(await self.r.get(counter) or 0) >= self.max_keys:
                return False                               # quota reached: skip caching
            await self.r.set(self._key(tenant, version, prompt), json.dumps(value), ex=ttl)
            await self.r.incr(counter)                     # count it (approximate)
            return True
        except Exception:
            return False                                   # never break the request

    async def invalidate_tenant(self, tenant: str) -> int:
        n = 0                                              # deleted counter
        async for k in self.r.scan_iter(match=f"cache:{tenant}:*", count=500):  # safe iteration
            await self.r.delete(k)                         # delete one key
            n += 1
        await self.r.delete(f"count:{tenant}")             # reset quota counter
        return n                                           # how many removed
```

---

## 🟠 FastAPI Integration
Take `tenant_id` from the authenticated principal, never from user input.

```python
from fastapi import Depends, FastAPI, Header, HTTPException   # FastAPI tools
from pydantic import BaseModel                             # schema

app = FastAPI()
tc = TenantCache()                                         # from advanced example
API_KEYS = {"key-acme": "acme", "key-globex": "globex"}    # demo mapping; use a DB/JWT in production

def current_tenant(x_api_key: str = Header(...)) -> str:
    tenant = API_KEYS.get(x_api_key)                       # resolve tenant from credential
    if tenant is None:
        raise HTTPException(status_code=401, detail="invalid api key")
    return tenant                                          # trusted tenant id

class Q(BaseModel):
    question: str                                          # user text only (no tenant here)

@app.post("/classify")
async def classify(body: Q, tenant: str = Depends(current_tenant)) -> dict:
    hit = await tc.get(tenant, "v1", body.question)        # tenant-scoped lookup
    if hit:
        return {**hit, "cached": True}                     # hit
    result = {"answer": "8517.13"}                         # placeholder for the LLM call
    await tc.set(tenant, "v1", body.question, result)      # tenant-scoped store
    return {**result, "cached": False}
```

---

## 🔗 LangChain / LangGraph Connection
Keep `tenant_id` in the LangGraph state (or `config["configurable"]`) and pass it to every cache and retriever call. For vector caches, put it in metadata and filter on it.

```python
from langgraph.graph import StateGraph, END                # graph builder
from typing import TypedDict                               # state schema

class S(TypedDict, total=False):
    tenant_id: str; question: str; answer: str             # tenant travels in state

async def cache_node(state: S) -> S:
    hit = await tc.get(state["tenant_id"], "v1", state["question"])   # scoped lookup
    return {"answer": hit["answer"]} if hit else {}        # fill answer if hit

# Run with tenant in config so every node can read it:
# await graph.ainvoke({"tenant_id": "acme", "question": q}, config={"configurable": {"thread_id": "t1"}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Key without tenant
```python
# Wrong — everyone shares the same entry:
key = f"cache:{hash(prompt)}"

# Correct:
key = f"cache:{tenant_id}:{hash(prompt)}"
```

❌ Mistake 2: Trusting tenant_id from the request body
```python
# Wrong — attacker sends another company's tenant_id:
tenant = body.tenant_id

# Correct — derive from verified auth token / API key:
tenant = Depends(current_tenant)
```

❌ Mistake 3: Putting private answers into the global cache
```python
# Wrong — cache everything globally to raise hit rate
# Correct — global only for content classified as public; default to private
```

---

## 🧠 Tricky Interview Question
**Q**: "Tenants A and B ask the identical question, and the cached answer is generated from A's private documents. Is it safe to serve B from the shared cache?"

**Answer**: No. Even if the question text is identical, the answer was derived from A's private context (RAG documents, system prompt, preferences). The cache key must represent **all inputs that influence the output**: tenant, retrieved-document set / ACL, prompt version, model, and temperature. Only answers generated **without** tenant-specific context can go into the global cache. A safe design is a flag set by the pipeline ("used_private_context") that decides the namespace.

---

## ⚫ Interview Questions + Answers

Q1: Why must the cache key include tenant_id?
A1: To prevent one customer seeing another's cached answers (data leak).

Q2: Where should tenant_id come from?
A2: From the authenticated identity (JWT claim, API key lookup), never from client-supplied fields.

Q3: Shared collection with filter or one collection per tenant in a vector DB?
A3: Shared collection plus a tenant-indexed payload filter scales better for many small tenants; separate collections give stronger isolation and simpler deletion for few large or regulated tenants. A hybrid is common.

Q4: How do you stop a noisy tenant evicting others?
A4: Per-tenant quotas and TTLs, per-tenant key counters, separate Redis DBs or instances for large tenants, and eviction policies that account for namespaces.

Q5: (Hard) How do you delete all of a tenant's cached data for GDPR erasure?
A5: Namespaced keys let you scan by prefix (or keep a per-tenant set index of keys), delete vectors by tenant filter, rotate tenant-specific encryption keys, and log the deletion. Avoid `KEYS` in production; use `SCAN` or an index set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- B2B SaaS serving multiple customers from one deployment
- Some content is public (share) and some private (isolate)

❌ Avoid shared global caching when:
- Answers use tenant-specific context or documents
- Compliance requires hard data separation (use separate stores)

---

## 📊 Visual Diagram
```
  Request + API key ──► auth ──► tenant_id = "acme"
                                      │
          ┌───────────────────────────┴──────────────┐
          ▼                                          ▼
  cache:acme:v1:<hash>                      cache:global:v1:<hash>
  (private, quota, TTL)                     (public answers only)
          │ miss                                     │ miss
          └──────────────► LLM ──► store in correct namespace
```

---

## 💰 Cost Impact
- Isolation lowers the hit rate versus one big shared cache (fewer shared entries), so cost savings are smaller per tenant. Share only public answers globally to recover savings safely.
- Memory cost grows with tenants x entries; enforce quotas and TTL.
- Token usage: hits cost 0 LLM tokens; misses cost full tokens. Track hit rate per tenant to see who benefits.
- Prices illustrative; check your provider.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tenant | One customer organisation | एक customer organisation |
| Namespace | Key prefix separating data | key का अलग हिस्सा |
| Isolation | One tenant cannot see another's data | tenants का data अलग |
| Noisy neighbour | Tenant using too much shared resource | दूसरों के resource खाने वाला tenant |
| Quota | Per-tenant limit | per-tenant सीमा |
| ACL | Access control list | access नियम सूची |

---

## ⚡ 3-Line Summary
English: Put tenant_id (from auth) in every cache key or filter so tenants never see each other's answers. Share a global namespace only for public content. Add quotas, TTLs and per-tenant deletion.
Hindi: हर cache key या filter में tenant_id (auth से) रखो ताकि tenants एक-दूसरे के answers न देखें। Global namespace सिर्फ़ public content के लिए। Quota, TTL और per-tenant deletion जोड़ो।

---

## ➡️ Next Topic
**458. Cache Security** — poisoning, leakage, encryption and other attacks on caches.
