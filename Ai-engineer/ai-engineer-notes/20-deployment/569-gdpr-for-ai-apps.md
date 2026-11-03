---

# 569. GDPR for AI Apps
# हिंदी में: AI Apps के लिए GDPR

---

## 🔵 Simple Definition (English)
GDPR is the EU's data protection law. If your AI app processes personal data of people in the EU (names, emails, IDs, chat content that identifies someone), you need a lawful basis, must minimise and protect the data, let people access or delete it, and be careful when sending it to third parties such as LLM providers. (This note is engineering guidance, not legal advice.)

## 🔵 सरल परिभाषा (Hindi)
GDPR EU का data protection कानून है। अगर आपका AI app EU के लोगों का personal data (नाम, email, ID, किसी को पहचानने वाली chat content) process करता है, तो lawful basis चाहिए, data कम से कम रखना और सुरक्षित करना होगा, लोगों को access या delete का अधिकार देना होगा, और LLM providers जैसे third parties को भेजते समय सावधानी रखनी होगी। (यह engineering guidance है, कानूनी सलाह नहीं।)

---

## 🔴 Problem it Solves
AI apps copy personal data into many places: prompts, provider logs, vector databases, chat history, traces, and fine-tuning sets. Users have rights (access, correction, erasure, portability), but data scattered across embeddings and logs makes those rights hard to honour. Fines can reach 4% of global turnover or EUR 20 million, whichever is higher. Privacy must be designed in.

## 🔴 यह क्यों बना? (Hindi)
AI apps personal data को कई जगह copy करते हैं: prompts, provider logs, vector databases, chat history, traces और fine-tuning sets। Users के अधिकार हैं (access, correction, erasure, portability), पर embeddings और logs में बिखरे data से इन्हें निभाना मुश्किल होता है। Fine global turnover का 4% या 20 मिलियन यूरो (जो ज़्यादा हो) तक हो सकती है। Privacy शुरू से design में होनी चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Map data flows: where does personal data enter, get stored, and leave (provider, logs, index)?
Step 2 → Pick a lawful basis (consent, contract, legitimate interest) and state the purpose
Step 3 → Minimise: send only needed fields; redact/pseudonymise PII before the LLM call
Step 4 → Provider contract: Data Processing Agreement (DPA), no-training setting, region (EU endpoints) if needed
Step 5 → Store with a user_id on EVERYTHING (chats, chunks, embeddings, traces) so it can be found
Step 6 → Retention: auto-delete after N days; short log retention
Step 7 → Rights: endpoints for export (access/portability) and delete (erasure) across all stores
Step 8 → Security + breach process (notify authority within 72 hours); DPIA for high-risk use
Step 9 → Automated decisions with legal effect (Art. 22): allow human review and explanation
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Data flow map करो: personal data कहाँ आता, store होता और बाहर जाता है (provider, logs, index)?
Step 2 → Lawful basis चुनो (consent, contract, legitimate interest) और purpose बताओ
Step 3 → Minimise: सिर्फ ज़रूरी fields भेजो; LLM call से पहले PII redact/pseudonymise करो
Step 4 → Provider contract: DPA, no-training setting, ज़रूरत हो तो EU region
Step 5 → हर चीज़ (chats, chunks, embeddings, traces) पर user_id रखो ताकि ढूँढा जा सके
Step 6 → Retention: N दिन बाद auto-delete; logs की retention छोटी
Step 7 → Rights: export (access/portability) और delete (erasure) endpoints, सब stores में
Step 8 → Security + breach process (authority को 72 घंटे में सूचना); high-risk use पर DPIA
Step 9 → कानूनी असर वाले automated decisions (Art. 22): human review और explanation की सुविधा
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importer invoices contain company names, addresses, and sometimes personal contact details. Before calling the LLM, a redaction step replaces names/emails with tokens (`<PERSON_1>`); the tariff question only needs the product description. Chat history is stored with `tenant_id` and `user_id` and deleted after 90 days. When a user requests erasure, a job deletes their rows, vector chunks, and cached answers.

**Zomato-style**: A food assistant that remembers addresses must let users view and delete saved addresses, and must not feed delivery addresses to analytics prompts without need.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer invoices में company names, addresses और कभी-कभी personal contact details होते हैं। LLM call से पहले redaction step names/emails को tokens (`<PERSON_1>`) से बदलता है; tariff सवाल को सिर्फ product description चाहिए। Chat history `tenant_id` और `user_id` के साथ store होती है और 90 दिन बाद delete। Erasure request पर job उनकी rows, vector chunks और cached answers delete करता है।

**Zomato-style**: जो food assistant addresses याद रखता है उसे users को saved addresses देखने और delete करने देना होगा, और बिना ज़रूरत delivery addresses analytics prompts में नहीं डालने होंगे।

---

## 💻 Code Example — Basic
```python
# Basic PII redaction with reversible placeholders (pure Python, runs directly)
import re                                        # regex patterns

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")           # simple email pattern
PHONE = re.compile(r"\+?\d[\d\s-]{8,13}\d")               # simple phone pattern


def redact(text: str) -> tuple[str, dict[str, str]]:
    """Replace emails/phones with placeholders; return the mapping to restore later."""
    mapping: dict[str, str] = {}                          # placeholder -> original value

    def _sub(prefix: str):
        def inner(m: re.Match[str]) -> str:
            key = f"<{prefix}_{len(mapping) + 1}>"        # unique placeholder
            mapping[key] = m.group(0)                     # remember original
            return key
        return inner

    text = EMAIL.sub(_sub("EMAIL"), text)                 # redact emails first
    text = PHONE.sub(_sub("PHONE"), text)                 # then phones
    return text, mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():                    # put originals back (locally only)
        text = text.replace(key, value)
    return text


safe, mp = redact("Contact ravi@example.com or +91 98765 43210 about HS code for laptops")
print(safe)                                               # placeholders instead of PII
print(restore(safe, mp))                                  # original, never sent to the LLM
```
(Regex redaction is only a baseline. Names and addresses need NER tools such as Microsoft Presidio.)

## 💻 Code Example — Advanced
```python
# Production style: user-data registry with export + erasure across stores (async)
from __future__ import annotations
import asyncio                                   # run deletions in parallel
import logging                                   # audit log
from typing import Protocol                      # interface for stores

log = logging.getLogger("gdpr")


class UserDataStore(Protocol):
    """Every system holding personal data implements this."""
    name: str
    async def export_user(self, user_id: str) -> dict: ...
    async def delete_user(self, user_id: str) -> int: ...      # returns number of records removed


class GdprService:
    def __init__(self, stores: list[UserDataStore]) -> None:
        self.stores = stores                                   # chats, vectors, cache, traces ...

    async def export(self, user_id: str) -> dict[str, dict]:
        """Right of access / portability."""
        results = await asyncio.gather(*(s.export_user(user_id) for s in self.stores),
                                       return_exceptions=True)
        out: dict[str, dict] = {}
        for store, res in zip(self.stores, results):
            out[store.name] = {"error": str(res)} if isinstance(res, Exception) else res
        return out

    async def erase(self, user_id: str) -> dict[str, int | str]:
        """Right to erasure: must hit EVERY store; report failures to retry."""
        results = await asyncio.gather(*(s.delete_user(user_id) for s in self.stores),
                                       return_exceptions=True)
        report: dict[str, int | str] = {}
        for store, res in zip(self.stores, results):
            if isinstance(res, Exception):
                log.error("erasure failed store=%s", store.name)     # no PII in the log
                report[store.name] = "FAILED_RETRY"
            else:
                report[store.name] = res
        log.info("erasure processed user_hash=%s", hash(user_id) & 0xFFFF)   # pseudonymous audit
        return report
```

---

## 🟠 FastAPI Integration
Expose data-subject endpoints behind authentication. The user can only act on their own ID.

```python
from fastapi import Depends, FastAPI, HTTPException   # framework

app = FastAPI()
service = GdprService(stores=[])                      # plug in chat store, vector store, cache


async def current_user_id() -> str:                   # replace with real auth (JWT)
    return "user-123"


@app.get("/me/data")
async def my_data(uid: str = Depends(current_user_id)) -> dict:
    return await service.export(uid)                  # access / portability


@app.delete("/me")
async def delete_me(uid: str = Depends(current_user_id)) -> dict:
    report = await service.erase(uid)                 # erasure across all stores
    if any(v == "FAILED_RETRY" for v in report.values()):
        raise HTTPException(status_code=202, detail=report)   # accepted, retry pending
    return {"status": "erased", "report": report}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph checkpointers store conversation state (which may contain PII), so key them by `thread_id` that maps to a `user_id`, and delete threads on erasure (checkpointer APIs vary; check the docs for your saver). For RAG, store `user_id` in vector metadata and delete by filter. Add a redaction step as the first node or a runnable in the chain, and disable tracing of raw inputs (or mask them) in LangSmith for sensitive workloads.

```python
from langchain_core.runnables import RunnableLambda

redactor = RunnableLambda(lambda t: redact(t)[0])      # strip PII before the prompt
# chain = redactor | prompt | llm | parser
# vectorstore.delete(filter={"user_id": uid})           # erasure by metadata (store-dependent, illustrative)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending full raw records (names, phone numbers) to the LLM when the task does not need them.
✅ Correct: minimise and redact first.

```python
# Wrong
answer = await llm.ainvoke(full_customer_record)
# Right
clean, mapping = redact(full_customer_record)
answer = await llm.ainvoke(clean)
```

❌ Mistake 2: "Deleting" the user from the database but leaving embeddings, caches, logs, and backups.
✅ Correct: keep a data inventory and delete across all stores (backups: expire on schedule and document it).

❌ Mistake 3: Using user chats to fine-tune models without a lawful basis or consent. Anonymise or get consent first.

---

## 🧠 Tricky Interview Question
**Q**: "A user asks to be forgotten, but their data was used to fine-tune your model. What do you do?"

**Answer**: Erasing from the dataset is easy; removing influence from trained weights is hard (machine unlearning is not a solved, routine process). Practical approach: avoid training on identifiable data in the first place (anonymise or use consent), keep dataset lineage so you know which models used whose data, retrain/refresh on a schedule excluding erased users, and document the approach with legal counsel. Prefer RAG for personal data, since deleting a document row/vector truly removes it from future answers.

---

## ⚫ Interview Questions + Answers

Q1: What counts as personal data in an AI app?
A1: Anything that identifies or can identify a person: name, email, phone, IP, device ID, location, and free text in chats that reveals identity. Embeddings derived from personal text can also be personal data.

Q2: What is data minimisation?
A2: Collect and send only the data needed for the purpose. Example: send the product description to the LLM, not the importer's name.

Q3: Which user rights matter most for AI apps?
A3: Access, rectification, erasure, portability, objection, and rights about solely automated decisions with significant effects.

Q4: Is sending data to an LLM provider allowed?
A4: Possibly, if you have a lawful basis, a DPA, appropriate transfer safeguards (e.g. SCCs or EU region) and settings that prevent training on your data. Check each provider's current terms with legal counsel.

Q5: (Hard) How do you design RAG so erasure is reliable?
A5: Put `user_id`/`tenant_id` and `source_id` in metadata on every chunk, record ingestion lineage, delete by filter, invalidate caches (semantic cache keys), purge traces/logs by retention policy, and verify with a post-deletion search test. Keep an inventory of all stores.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users or data subjects are in the EU/UK (or similar laws apply: India's DPDP Act, CCPA)
- Handling HR, health, finance, or customer records with AI

❌ Avoid when:
- Never ignore it; for truly anonymous, non-personal data (public tariff schedules) GDPR does not apply, so skip the heavy machinery there

---

## 📊 Visual Diagram
```
 User input (PII) ─► [Redact / pseudonymise] ─► LLM provider (DPA, no-train, EU region)
        │                     │
        ▼                     ▼
  Chat store (user_id)   Vector DB (user_id metadata)
  Traces (short TTL)     Cache (keyed, purgeable)
        └───────────┬─────────┘
                    ▼
        Erasure request ─► delete in ALL stores ─► audit report
        Access request  ─► export from ALL stores
```

---

## 💰 Cost Impact
- Redaction removes tokens (placeholders are short; dropped fields reduce prompt size), so minimisation can lower token cost slightly. NER-based redaction adds compute but no tokens when run locally.
- Costs to plan for: EU-region endpoints (sometimes priced differently, check provider pricing), storage of audit logs, engineering for erasure pipelines, and DPIA/legal reviews.
- Retention limits cut storage and index size, cutting vector DB cost.
- The risk-cost of a violation (fines up to 4% of turnover) dwarfs these.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Personal data | Info identifying a person | व्यक्ति की पहचान वाला data |
| Data subject | The person the data is about | जिसका data है वह व्यक्ति |
| DPA | Data Processing Agreement with vendor | Vendor के साथ data processing समझौता |
| Erasure | Right to be forgotten | भूल जाने का अधिकार |
| Data minimisation | Use only what is needed | सिर्फ ज़रूरी data |
| DPIA | Data Protection Impact Assessment | Data protection जोखिम आकलन |
| Pseudonymisation | Replace identifiers with tokens | पहचान को tokens से बदलना |

---

## ⚡ 3-Line Summary
English: GDPR requires lawful basis, minimisation, security, retention limits, and user rights such as access and erasure. In AI apps personal data spreads across prompts, vectors, caches, and logs, so tag it with user IDs and build export and delete across every store. Redact before calling providers and sign a DPA.
Hindi: GDPR में lawful basis, minimisation, security, retention limits और access/erasure जैसे user rights ज़रूरी हैं। AI apps में personal data prompts, vectors, caches और logs में फैलता है, इसलिए user IDs से tag करो और हर store में export और delete बनाओ। Provider को भेजने से पहले redact करो और DPA साइन करो।

---

## ➡️ Next Topic
**570. AI Production Checklist** — bring versioning, monitoring, cost, limits, security and privacy together into one pre-launch checklist.
