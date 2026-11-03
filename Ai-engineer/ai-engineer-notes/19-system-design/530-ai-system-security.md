
---

# 530. AI System Security
# हिंदी में: AI System Security

---

## 🔵 Simple Definition (English)
AI system security means protecting the whole LLM application, not just the prompt: who can call it (identity), what data it can see (access control), how data travels and rests (encryption), what tools it can use (least privilege), and how you detect abuse (logging). It combines normal cloud security with LLM-specific defences.

## 🔵 सरल परिभाषा (Hindi)
AI system security का मतलब सिर्फ prompt नहीं, पूरे LLM application की सुरक्षा है: कौन call कर सकता है (identity), कौन सा data देख सकता है (access control), data कैसे चलता और रखा जाता है (encryption), कौन से tools use कर सकता है (least privilege), और abuse कैसे पकड़ें (logging)। यह सामान्य cloud security और LLM-specific बचाव का मेल है।

---

## 🔴 Problem it Solves
- LLM apps connect to sensitive things: private documents, databases, payment or admin APIs.
- Attackers target many layers: stolen API keys, cross-tenant data access, prompt injection, supply chain (malicious packages or model files).
- Compliance rules (GDPR, customer contracts) require proof of control.

## 🔴 यह क्यों बना? (Hindi)
- LLM apps संवेदनशील चीज़ों से जुड़े होते हैं: private documents, databases, payment या admin APIs।
- Attackers कई layers को निशाना बनाते हैं: चोरी हुई API keys, cross-tenant data access, prompt injection, supply chain (गलत packages या model files)।
- Compliance नियम (GDPR, customer contracts) control का सबूत माँगते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identity: authenticate every caller (JWT/OAuth/API key), map to a tenant and role
Step 2 → Authorisation in code: check access per document/tool (never ask the LLM)
Step 3 → Network: TLS everywhere, private subnets for DB/vector store, WAF/gateway at the edge
Step 4 → Data: encrypt at rest, minimise what is sent to the LLM, mask PII, set retention
Step 5 → LLM layer: input/output guards, role separation, tool allow-list, human approval
Step 6 → Secrets: secret manager, rotation, short-lived credentials, no keys in prompts/logs
Step 7 → Supply chain: pin dependencies, scan images, use trusted model sources (safetensors)
Step 8 → Detect and respond: audit logs, anomaly alerts, incident runbook, key revocation
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Identity: हर caller authenticate करो (JWT/OAuth/API key), tenant और role से map करो
Step 2 → Authorisation code में: हर document/tool पर access check करो (LLM से कभी मत पूछो)
Step 3 → Network: हर जगह TLS, DB/vector store private subnet में, edge पर WAF/gateway
Step 4 → Data: rest पर encrypt, LLM को कम से कम data भेजो, PII mask, retention तय
Step 5 → LLM layer: input/output guards, role separation, tool allow-list, human approval
Step 6 → Secrets: secret manager, rotation, short-lived credentials, prompts/logs में keys नहीं
Step 7 → Supply chain: dependencies pin करो, images scan करो, भरोसेमंद model sources (safetensors)
Step 8 → Detect और respond: audit logs, anomaly alerts, incident runbook, key revoke
```

---

## 🟡 Real World Example
**Tariff Classification System**: Two customs brokers (tenant A and tenant B) upload shipment documents. Security design:
- Each request carries a JWT with `tenant_id`; the server (not the client) sets it as a mandatory filter on the vector DB query.
- Documents are stored encrypted; the vector DB is in a private subnet.
- The LLM sees only the needed chunks, with tax IDs masked.
- The agent has read-only tools; "update duty rate" requires an admin and a human approval.
- Every request logs tenant, user, chunk ids retrieved and token count (not raw text).

**Zomato-style AI**: Support bot sees only the current customer's orders; the order lookup tool takes the customer id from the auth token, never from the chat text.

## 🟡 Real Example Hindi mein
**Tariff System**: दो customs brokers (tenant A और tenant B) shipment documents upload करते हैं। Security design:
- हर request में `tenant_id` वाला JWT है; server (client नहीं) इसे vector DB query पर अनिवार्य filter के रूप में लगाता है।
- Documents encrypted रखे जाते हैं; vector DB private subnet में है।
- LLM को सिर्फ ज़रूरी chunks दिखते हैं, tax IDs masked के साथ।
- Agent के tools read-only हैं; "duty rate update" के लिए admin और human approval चाहिए।
- हर request tenant, user, retrieved chunk ids और token count log करती है (raw text नहीं)।

**Zomato-style AI**: Support bot सिर्फ मौजूदा customer के orders देखता है; order lookup tool customer id auth token से लेता है, chat text से कभी नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: tenant-isolated retrieval (pure Python simulation of a vector store)
from dataclasses import dataclass                      # simple record

@dataclass
class Chunk:
    tenant_id: str                                     # owner of this data
    text: str                                          # content

STORE: list[Chunk] = [
    Chunk("A", "Tenant A: invoice for phones"),
    Chunk("B", "Tenant B: invoice for steel pipes"),
]

def search(query: str, tenant_id: str) -> list[str]:
    """Keyword search that ALWAYS filters by tenant first."""
    mine = [c for c in STORE if c.tenant_id == tenant_id]  # mandatory filter
    return [c.text for c in mine if query.lower() in c.text.lower()]

if __name__ == "__main__":
    print(search("invoice", "A"))                      # only tenant A data
    print(search("steel", "A"))                        # [] : B's data is invisible
```

## 💻 Code Example — Advanced
```python
# Advanced: JWT-style auth dependency + tool authorisation + audit log (stdlib only)
import asyncio                                         # async demo
import hashlib                                         # hash user ids for logs
import hmac                                            # constant-time compare
import json                                            # audit format
import logging                                         # audit logger
import time                                            # timestamps
from dataclasses import dataclass

audit = logging.getLogger("audit")                     # separate audit stream

@dataclass(frozen=True)
class Principal:
    user_id: str                                       # who
    tenant_id: str                                     # which tenant
    role: str                                          # 'viewer' or 'admin'

class Forbidden(Exception):
    """Raised when policy says no."""

TOOL_ROLES: dict[str, set[str]] = {                    # tool -> allowed roles
    "get_duty_rate": {"viewer", "admin"},
    "update_duty_rate": {"admin"},
}

def authorize_tool(p: Principal, tool: str) -> None:
    """Deny by default; authorisation is code, never the LLM's decision."""
    allowed = TOOL_ROLES.get(tool)                     # None if unknown tool
    if allowed is None or p.role not in allowed:
        audit.warning(json.dumps({"event": "deny", "tool": tool,
                                  "user": hashlib.sha256(p.user_id.encode()).hexdigest()[:8]}))
        raise Forbidden(tool)                          # stop here

def verify_api_key(given: str, expected: str) -> bool:
    """Constant-time comparison avoids timing leaks."""
    return bool(expected) and hmac.compare_digest(given.encode(), expected.encode())

async def run_tool(p: Principal, tool: str, args: dict[str, str]) -> str:
    authorize_tool(p, tool)                            # check BEFORE running
    await asyncio.sleep(0)                             # pretend I/O
    audit.info(json.dumps({"event": "tool", "tool": tool, "tenant": p.tenant_id,
                           "ts": int(time.time())}))   # audit trail without raw args
    return f"{tool} ok"

async def main() -> None:
    viewer = Principal("u1", "A", "viewer")
    print(await run_tool(viewer, "get_duty_rate", {"hs": "8517.13"}))
    try:
        await run_tool(viewer, "update_duty_rate", {"hs": "8517.13"})  # blocked
    except Forbidden as exc:
        print("forbidden:", exc)
    print(verify_api_key("abc", "abc"), verify_api_key("abc", ""))   # True False

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Security in FastAPI: `OAuth2PasswordBearer` or an API-key header dependency, role checks as dependencies, CORS limited to known origins, and tenant id taken from the token only.

```python
# FastAPI: tenant comes from the verified token, never from the request body
from fastapi import Depends, FastAPI, HTTPException, Header

app = FastAPI()

def decode_token(token: str) -> Principal:
    """Placeholder: real code verifies a JWT signature (e.g. PyJWT) and expiry."""
    if token == "token-a":
        return Principal("u1", "A", "viewer")
    raise HTTPException(status_code=401, detail="invalid token")

async def current_principal(authorization: str = Header(default="")) -> Principal:
    scheme, _, token = authorization.partition(" ")    # "Bearer <token>"
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="missing token")
    return decode_token(token)

@app.get("/search")
async def search_route(q: str, p: Principal = Depends(current_principal)) -> dict[str, list[str]]:
    return {"results": search(q, p.tenant_id)}         # tenant forced from token
```

---

## 🔗 LangChain / LangGraph Connection
- Pass `tenant_id` into the retriever as a metadata filter via `search_kwargs={"filter": {...}}` (the exact filter syntax depends on your vector store).
- In LangGraph, put the `Principal` into graph state or `config["configurable"]`, and check it inside tool nodes before running a tool.
- Add a human approval `interrupt` before write tools.

```python
# LangChain retriever with a forced tenant filter (illustrative; syntax varies by store)
# retriever = vectorstore.as_retriever(search_kwargs={"k": 4, "filter": {"tenant_id": principal.tenant_id}})
# In a LangGraph tool node:
# def tool_node(state, config):
#     p = config["configurable"]["principal"]
#     authorize_tool(p, state["tool_name"])   # reuse the same function
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting tenant id from the client
```python
# Wrong: attacker sets tenant_id=B in the JSON body
results = search(req.q, req.tenant_id)
# Right: from the verified token
results = search(req.q, principal.tenant_id)
```

❌ Mistake 2: Letting the LLM decide permissions ("only answer if the user is admin")
✅ Correct: Check permissions in code before data or tools reach the model.

❌ Mistake 3: Loading untrusted model files with pickle
✅ Correct: Prefer `safetensors`, verify checksums, pin versions, and pull from trusted registries.

---

## 🧠 Tricky Interview Question

**Q**: "Your LLM app has strong prompt-injection defences, but a pentester still reads another customer's data. How?"

**Answer**: Likely an ordinary access-control bug (IDOR/broken authorisation), not an LLM one: for example the vector search has no tenant filter, a cache key lacks the tenant id, the chat-history endpoint accepts a `session_id` from the client without checking ownership, or a tool takes `customer_id` from the model's arguments. LLM defences do not fix these. Fix: derive identity from the token, enforce tenant filters at the data layer, scope cache keys and memory per tenant, validate tool arguments against the principal, and write automated cross-tenant tests.

---

## ⚫ Interview Questions + Answers

Q1: What is least privilege?
A1: Give each component only the access it needs. The LLM agent gets read-only tools and a read-only DB user, not admin.

Q2: Why encrypt data and use TLS?
A2: TLS protects data in transit (network sniffing). Encryption at rest protects stored data if disks or backups leak.

Q3: What is an IDOR bug?
A3: Insecure Direct Object Reference: the app uses an id from the client (like `doc_id`) without checking that the user owns it. It is common in chat-history and document APIs.

Q4: How can the supply chain attack an AI app?
A4: Malicious or typo-squatted Python packages, poisoned model files (pickle can run code on load), compromised container base images, or tampered datasets. Pin versions, scan, use trusted sources.

Q5 (Hard): Your data must not leave the country and customers may not want their data used by a third-party LLM. What are your options?
A5: Use a region-pinned deployment of a managed model (for example a cloud provider's in-region endpoint, subject to their data-use terms), or self-host an open model in your own VPC. Send minimal data (mask PII, send chunks not whole files), sign a data-processing agreement, disable provider training on your data, log what leaves, and keep vector DB and storage in-region. Trade-off: self-hosting adds GPU and ops cost and usually lower model quality than top hosted models.

---

## 🔷 When to Use + When Not to Use
✅ Use full-stack security when:
- Multi-tenant, regulated (legal, finance, health, customs) or public apps
- Agents with tools that can change data

❌ Avoid over-engineering when:
- A local prototype with synthetic data (still keep keys out of git)
- Adding controls that duplicate each other without a threat they address

---

## 📊 Visual Diagram
```
 Internet
    |  TLS
 +--v----------+     +-------------------------------------------+
 | WAF/Gateway |---->| App (FastAPI)  - verify JWT -> Principal  |
 | rate limit  |     |  - tenant filter, tool authz (code)       |
 +-------------+     |  - guards in/out, audit log               |
                     +-----+----------------+--------------------+
                           |                |
              private subnet|               | egress allow-list
                +----------v--+      +------v---------+
                | Vector DB / |      | LLM provider   |
                | SQL (RO user)|     | (masked data)  |
                | encrypted   |      +----------------+
                +-------------+
   Secrets: secret manager   |   Logs: audit, masked   |   Scans: deps, images
```

---

## 💰 Cost Impact
- Security controls are mostly cheap in tokens: auth, filters and redaction run in code.
- Biggest cost risks are abuse: stolen keys and unbounded loops. Per-tenant token budgets and rate limits cap the loss.
- Sending less data to the LLM (masking, chunking, summarising) reduces both leak risk and input tokens.
- Self-hosting for data residency swaps per-token cost for fixed GPU cost; compare at your volume.
- Prices vary by provider and change; treat any number as illustrative.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Authentication | Proving who you are | आप कौन हैं, यह सिद्ध करना |
| Authorisation | What you are allowed to do | आप क्या कर सकते हैं |
| Tenant isolation | One customer cannot see another's data | एक customer दूसरे का data नहीं देख सकता |
| IDOR | Using someone else's id to get their data | दूसरे की id से उसका data पाना |
| Encryption at rest | Stored data is encrypted | Stored data encrypted |
| Supply chain | Packages, models, images you depend on | निर्भर packages, models, images |
| Audit log | Tamper-resistant record of actions | Actions का भरोसेमंद record |

---

## ⚡ 3-Line Summary
English: AI security is cloud security plus LLM defences: identity, authorisation in code, tenant isolation, encryption, least-privilege tools and audit logs. Most real leaks are access-control bugs, not clever prompts. Secure the supply chain and keep secrets out of prompts and logs.
Hindi: AI security यानी cloud security के साथ LLM बचाव: identity, code में authorisation, tenant isolation, encryption, least-privilege tools और audit logs। ज़्यादातर असली leaks चालाक prompts नहीं, access-control bugs से होते हैं। Supply chain सुरक्षित रखो और secrets को prompts व logs से दूर रखो।

---

## ➡️ Next Topic
**531. Design: RAG for 1M Documents** — a full system design exercise that applies scale, cost and security together.
