---

# 135. Pinecone Namespaces
# हिंदी में: Pinecone Namespaces (index के अंदर अलग-अलग हिस्से)

---

## 🔵 Simple Definition (English)
A namespace is a named partition inside one Pinecone index. Every upsert, query, fetch and delete targets exactly one namespace, and a query only sees vectors in that namespace. They are created automatically on first write. Think of an index as a building and namespaces as locked rooms.

## 🔵 सरल परिभाषा (Hindi)
Namespace एक Pinecone index के अंदर नाम वाला partition है। हर upsert, query, fetch और delete सिर्फ़ एक namespace पर चलता है और query सिर्फ़ उसी namespace के vectors देखती है। पहली write पर अपने-आप बन जाता है। Index को building और namespaces को बंद कमरे समझो।

---

## 🔴 Problem it Solves
Multi-tenant apps must never leak one customer's data to another, and want cheap per-customer deletion. Creating one index per tenant is costly and limited (index count quotas). Filtering by `tenant_id` on a shared namespace works but a single missed filter leaks data and scans more vectors. Namespaces give hard isolation, faster scoped scans and one-call deletion.

## 🔴 यह क्यों बना? (Hindi)
Multi-tenant apps में एक customer का data दूसरे को कभी नहीं दिखना चाहिए, और per-customer delete सस्ता होना चाहिए। हर tenant का अलग index महँगा है और quota सीमित है। Shared namespace में `tenant_id` filter काम करता है पर एक filter छूटा तो data leak, और scan भी ज़्यादा। Namespaces hard isolation, तेज़ scoped scan और एक call में delete देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a namespace naming scheme: f"{tenant_id}" or f"{env}-{tenant_id}-{kind}"
Step 2 → index.upsert(vectors=[...], namespace="tenant-acme")   # created automatically
Step 3 → index.query(vector=q, top_k=5, namespace="tenant-acme")  # sees ONLY that namespace
Step 4 → index.describe_index_stats() -> {"namespaces": {"tenant-acme": {"vector_count": 1200}}}
Step 5 → index.delete(delete_all=True, namespace="tenant-acme")   # wipe a tenant (GDPR)
Step 6 → Default namespace is "" (empty string) when you pass none
Step 7 → There is no cross-namespace query: to search many, query each and merge (or use one namespace + filter)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Naming scheme चुनो: f"{tenant_id}" या f"{env}-{tenant_id}-{kind}"
Step 2 → index.upsert(vectors=[...], namespace="tenant-acme")   # अपने-आप बनता है
Step 3 → index.query(vector=q, top_k=5, namespace="tenant-acme")  # सिर्फ़ उसी namespace को देखता है
Step 4 → describe_index_stats() से हर namespace का vector_count मिलता है
Step 5 → index.delete(delete_all=True, namespace="tenant-acme")   # tenant का पूरा data हटाओ (GDPR)
Step 6 → namespace न दो तो default namespace "" (खाली string) होता है
Step 7 → Cross-namespace query नहीं है: कई में search करना हो तो हर में query करके merge करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: a SaaS for customs brokers. Each broker firm uploads private rulings and past declarations. Namespace `firm-1042` holds that firm's vectors; shared public tariff schedules live in namespace `public-IN`. Each request queries `public-IN` and the firm's namespace, merges the results, and reranks. When a firm cancels its contract, one `delete_all` call erases its data.

**Zomato AI**: namespaces `prod-dishes`, `staging-dishes` keep environments apart inside one index.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs brokers के लिए SaaS। हर firm अपने private rulings और declarations upload करती है। Namespace `firm-1042` में उसी firm के vectors; public tariff schedules namespace `public-IN` में। हर request `public-IN` और firm के namespace दोनों में query करती है, results merge और rerank करती है। Firm का contract खत्म होने पर एक `delete_all` call से data मिट जाता है। **Zomato**: `prod-dishes` और `staging-dishes` namespaces एक ही index में environments अलग रखते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: demonstrate namespace isolation with a tiny in-memory model (runs offline).
from collections import defaultdict                     # auto-creating dict
from typing import Any, Dict, List, Tuple               # type hints

class NamespacedStore:
    """Mimics Pinecone: every operation targets exactly one namespace."""
    def __init__(self) -> None:
        self.ns: Dict[str, Dict[str, List[float]]] = defaultdict(dict)   # namespace -> id -> vector

    def upsert(self, items: Dict[str, List[float]], namespace: str = "") -> None:
        self.ns[namespace].update(items)                # created automatically on first write

    def query(self, q: List[float], k: int = 1, namespace: str = "") -> List[Tuple[str, float]]:
        rows = self.ns.get(namespace, {})               # unknown namespace -> empty (no error)
        scored = [(i, sum(a * b for a, b in zip(q, v))) for i, v in rows.items()]   # dot product
        return sorted(scored, key=lambda t: -t[1])[:k]  # best first

    def delete_namespace(self, namespace: str) -> None:
        self.ns.pop(namespace, None)                    # one call wipes a tenant

    def stats(self) -> Dict[str, int]:
        return {n: len(v) for n, v in self.ns.items()}  # vector counts per namespace

s = NamespacedStore()                                   # create the store
s.upsert({"r1": [1.0, 0.0]}, namespace="firm-1042")     # firm A private ruling
s.upsert({"r2": [1.0, 0.0]}, namespace="firm-2001")     # firm B private ruling (identical vector!)
s.upsert({"h1": [0.9, 0.1]}, namespace="public-IN")     # shared public heading
print(s.query([1.0, 0.0], namespace="firm-1042"))       # only r1: firm A cannot see firm B
print(s.query([1.0, 0.0], namespace="typo-ns"))         # [] : a mistyped namespace silently returns nothing
print(s.stats())                                        # counts per namespace
s.delete_namespace("firm-1042")                         # tenant offboarding
print(s.stats())                                        # firm-1042 gone
```

## 💻 Code Example — Advanced
```python
# Advanced: tenant-aware wrapper: server-side namespace resolution, multi-namespace search
# with merge, offboarding, stats; async via threads. `index` is a pinecone Index handle.
import asyncio                                           # async runtime
import logging                                           # logs
import re                                                # validate namespace names
from typing import Any, Dict, List                       # type hints

log = logging.getLogger("tenant-ns")                     # logger
NS_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,62}$")        # conservative namespace pattern

class TenantVectors:
    def __init__(self, index: Any, env: str = "prod", public_ns: str = "public-IN") -> None:
        self.index = index                               # Pinecone Index handle
        self.env = env                                   # environment prefix
        self.public_ns = public_ns                       # shared knowledge namespace

    def ns_for(self, tenant_id: str) -> str:
        name = f"{self.env}-firm-{tenant_id}".lower()    # deterministic naming
        if not NS_RE.match(name):                        # reject odd characters (defence in depth)
            raise ValueError(f"invalid tenant id: {tenant_id!r}")
        return name

    async def _query_one(self, ns: str, vec: List[float], k: int) -> List[Dict[str, Any]]:
        res = await asyncio.to_thread(                   # blocking SDK call off the event loop
            self.index.query, vector=vec, top_k=k, namespace=ns, include_metadata=True)
        return [{"id": m.id, "score": m.score, "ns": ns, **(m.metadata or {})} for m in res.matches]

    async def search(self, tenant_id: str, vec: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search the tenant's private namespace AND the shared public one, then merge."""
        namespaces = [self.ns_for(tenant_id), self.public_ns]        # both are queried in parallel
        results = await asyncio.gather(*(self._query_one(n, vec, k) for n in namespaces),
                                       return_exceptions=True)       # one failing ns should not kill all
        merged: List[Dict[str, Any]] = []
        for ns, r in zip(namespaces, results):
            if isinstance(r, Exception):                 # log and continue with partial results
                log.error("query failed for %s: %s", ns, r)
                continue
            merged.extend(r)                             # collect hits
        merged.sort(key=lambda h: h["score"], reverse=True)          # global ranking by score
        return merged[:k]                                # top-k across namespaces

    async def offboard(self, tenant_id: str) -> None:
        ns = self.ns_for(tenant_id)                      # compute (and validate) the namespace
        await asyncio.to_thread(self.index.delete, delete_all=True, namespace=ns)   # erase tenant data
        log.warning("deleted namespace %s", ns)          # audit trail

    async def sizes(self) -> Dict[str, int]:
        stats = await asyncio.to_thread(self.index.describe_index_stats)   # per-namespace counts
        return {n: s.vector_count for n, s in stats.namespaces.items()}

# Note: scores from different namespaces are comparable only if they use the same embedding model and metric (they do: same index).
# Token usage: 0 for namespace operations; one query embedding (~20 tokens) is reused for both namespaces.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, HTTPException        # FastAPI
from openai import AsyncOpenAI                              # embeddings
from pydantic import BaseModel                              # request schema

app = FastAPI()                                             # app
oai = AsyncOpenAI()                                         # client
tv = TenantVectors(index)                                   # shared wrapper (index created at startup)

class User(BaseModel):
    tenant_id: str                                          # comes from the verified JWT, not the body

def current_user() -> User:                                 # replace with real JWT parsing
    return User(tenant_id="1042")

@app.get("/rulings/search")                                 # search route
async def search(q: str, user: User = Depends(current_user)) -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)
    try:
        hits = await tv.search(user.tenant_id, emb.data[0].embedding)   # namespace derived server-side
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {"hits": hits}

@app.delete("/tenants/me")                                  # GDPR erasure endpoint
async def delete_me(user: User = Depends(current_user)) -> dict:
    await tv.offboard(user.tenant_id)
    return {"status": "deleted"}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import OpenAIEmbeddings               # embeddings
from langchain_pinecone import PineconeVectorStore           # integration

emb = OpenAIEmbeddings(model="text-embedding-3-small")       # embedding model

def retriever_for(tenant_id: str):                           # one retriever per tenant
    vs = PineconeVectorStore(index_name="tariff-hs-te3s-v1", embedding=emb,
                             namespace=f"prod-firm-{tenant_id}")   # namespace binds the store
    return vs.as_retriever(search_kwargs={"k": 5})           # standard LCEL retriever

docs = retriever_for("1042").invoke("wireless earbuds")      # only this tenant's vectors
# LangGraph: pass tenant_id via config["configurable"] and build the retriever inside the node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Writing to one namespace and querying another (or the default)
✅ Correct: use the same namespace string for both; centralise it in one function.

```python
# Wrong: upsert in "headings", query default "" -> empty results, no error
index.upsert(vectors=v, namespace="headings"); index.query(vector=q, top_k=5)
# Right
index.query(vector=q, top_k=5, namespace="headings")
```

❌ Mistake 2: Taking the namespace from user input
✅ Correct: derive it from the authenticated identity.

```python
# Wrong: client can read anyone's data
ns = request.query_params["namespace"]
# Right
ns = tv.ns_for(current_user.tenant_id)
```

---

## 🧠 Tricky Interview Question

**Q**: "You have 50,000 tiny tenants. Namespaces per tenant or one namespace with a `tenant_id` filter?"

**Answer**: Namespaces are the recommended pattern for multi-tenancy: isolation is structural (no filter to forget), queries scan only that tenant's data (faster, cheaper reads), and deletion is one call. Pinecone serverless supports a very large number of namespaces per index (check the current limit in the docs). Use a metadata filter instead when you need to search across tenants in one query (since there is no cross-namespace query), or when categories are soft attributes rather than isolation boundaries. A hybrid works well: namespace per tenant, filters for attributes within the tenant.

---

## ⚫ Interview Questions + Answers

Q1: What is a namespace in Pinecone?
A1: A logical partition within an index. Operations target one namespace, and data in different namespaces is isolated.

Q2: How do you create a namespace?
A2: Just upsert with a new `namespace` name; it is created implicitly. The default namespace is the empty string.

Q3: How do you delete all data of one tenant?
A3: `index.delete(delete_all=True, namespace="tenant")`.

Q4: Can one query search several namespaces?
A4: No. Query each one (in parallel) and merge results by score, or keep data in a single namespace and use metadata filters.

Q5: How do namespaces and metadata filters compare for security and cost?
A5: Namespaces isolate by construction: a bug cannot accidentally return another tenant's vectors, and reads scan only that partition, which lowers read-unit cost. Filters share one data pool; a missing filter clause leaks data, and selective filters can scan large pools. For compliance workloads choose namespaces plus server-derived names, test cross-tenant access, log offboarding, and keep an external inventory of namespaces because listing them via stats can be large for many tenants.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-tenant SaaS and per-customer deletion
- Separating prod/staging, or document types with different lifecycles

❌ Avoid when:
- You must search across all partitions in a single query
- Partitioning attribute is soft and changes often (use metadata)

---

## 📊 Visual Diagram
```
 Index "tariff-hs-te3s-v1"  (dim 1536, cosine)
 ┌──────────────────────────────────────────────────────────┐
 │ ns "public-IN"      ▓▓▓▓▓▓▓▓▓▓  shared tariff headings   │
 │ ns "prod-firm-1042" ▓▓▓         private rulings, firm A  │
 │ ns "prod-firm-2001" ▓▓          private rulings, firm B  │
 └──────────────────────────────────────────────────────────┘
 Request from firm A:  query(ns="prod-firm-1042") + query(ns="public-IN") ─► merge by score ─► LLM
 Firm B's namespace is never touched.
```

---

## 💰 Cost Impact
- Namespaces are free to create; you pay for stored vectors and read/write units. Scoped reads scan less data, which reduces read units compared with one huge shared namespace.
- One index with many namespaces beats many indexes (each index has minimum overhead and quota limits).
- Querying two namespaces costs two reads, but both can use the same query embedding, so token cost is unchanged (~20 tokens). Query only the namespaces you need.
- Deleting a churned tenant's namespace immediately stops its storage cost, so offboard promptly.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Namespace | Named partition inside an index | Index के अंदर नाम वाला partition |
| Multi-tenancy | Many customers share one system | कई customers एक system share करते हैं |
| Isolation | One tenant cannot see another's data | एक tenant दूसरे का data नहीं देख सकता |
| Default namespace | The empty-string namespace | खाली string वाला namespace |
| Offboarding | Removing a tenant's data | Tenant का data हटाना |
| Fan-out query | Query several partitions and merge | कई partitions में query करके merge करना |
| delete_all | Remove everything in a namespace | Namespace का सब कुछ हटाना |

---

## ⚡ 3-Line Summary
English: Namespaces partition one index into isolated groups; every operation targets one namespace. They give safe multi-tenancy, cheaper scoped reads and one-call deletion. Derive the namespace from the authenticated user and query several namespaces yourself when needed.
Hindi: Namespaces एक index को isolated groups में बाँटते हैं; हर operation एक namespace पर चलता है। ये सुरक्षित multi-tenancy, सस्ते scoped reads और एक call में delete देते हैं। Namespace authenticated user से निकालो और ज़रूरत पर कई namespaces में खुद query करो।

---

## ➡️ Next Topic
**136. Pinecone Serverless vs Pod** — the two deployment models, their cost behaviour and when to choose each.
