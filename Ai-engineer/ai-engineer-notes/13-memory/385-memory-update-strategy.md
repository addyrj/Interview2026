---

# 385. Memory Update Strategy
# हिंदी में: Memory Update Strategy

---

## 🔵 Simple Definition (English)
A memory update strategy decides when and how memory changes: add a new fact, update a changed one, merge duplicates, or forget stale data. It also decides whether this happens synchronously ("hot path") or in the background.

## 🔵 सरल परिभाषा (Hindi)
Memory update strategy तय करती है कि memory कब और कैसे बदले: नया fact add, बदला हुआ update, duplicates merge, या पुराना data forget। ये भी तय होता है कि ये synchronously ("hot path") हो या background में।

---

## 🔴 Problem it Solves
Append-only memory fills with duplicates and contradictions ("origin China", "origin Vietnam"). Retrieval then returns conflicting facts and the bot looks confused.

## 🔴 यह क्यों बना? (Hindi)
Append-only memory duplicates और contradictions से भर जाती है ("origin China", "origin Vietnam")। Retrieval विरोधी facts लौटाता है और bot confused दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → New information arrives (a candidate fact)
Step 2 → Find similar existing memories (same key or high similarity)
Step 3 → Decide: ADD (new), UPDATE (changed), NONE (same), DELETE (retracted)
Step 4 → Apply with version / timestamp (keep history if needed)
Step 5 → Mark source and confidence
Step 6 → Background job: merge near-duplicates, expire by TTL, decay importance
Step 7 → Log every change for audit and rollback
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → नई जानकारी आती है (candidate fact)
Step 2 → मिलती-जुलती मौजूदा memories ढूँढो (same key या ज़्यादा similarity)
Step 3 → तय करो: ADD (नया), UPDATE (बदला), NONE (वही), DELETE (वापस लिया)
Step 4 → Version / timestamp के साथ apply करो (ज़रूरत हो तो history रखो)
Step 5 → Source और confidence mark करो
Step 6 → Background job: near-duplicates merge, TTL से expire, importance decay
Step 7 → हर बदलाव audit और rollback के लिए log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tariff rates change each budget. Memory "duty for 8507.60 = 20 percent" must be UPDATEd to 15 percent with `valid_from` date, keeping the old value in history for past shipments. **Zomato-style**: "address: Flat 4" updates to the new address; old address expires after 90 days unused.

## 🟡 Real Example Hindi mein
**Tariff System**: हर budget में tariff rates बदलते हैं। Memory "8507.60 की duty = 20 percent" को `valid_from` date के साथ 15 percent में UPDATE करना होगा और पुराने shipments के लिए पुरानी value history में रहेगी। **Zomato-style**: "address: Flat 4" नए address से update हो जाता है; पुराना address 90 दिन unused रहने पर expire।

---

## 💻 Code Example — Basic
```python
# Pure Python versioned memory with ADD / UPDATE / NONE / DELETE. Runs offline.
import time                                                   # timestamps

class VersionedMemory:
    def __init__(self) -> None:
        self.current: dict[str, str] = {}                     # key -> latest value
        self.history: list[tuple[float, str, str, str]] = []  # (time, action, key, value)

    def apply(self, key: str, value: str | None) -> str:
        """value=None means DELETE."""
        if value is None:
            action = "DELETE" if key in self.current else "NONE"
            self.current.pop(key, None)                       # remove if present
        elif key not in self.current:
            action = "ADD"; self.current[key] = value
        elif self.current[key] != value:
            action = "UPDATE"; self.current[key] = value
        else:
            action = "NONE"
        self.history.append((time.time(), action, key, value or ""))   # audit trail
        return action

m = VersionedMemory()
print(m.apply("duty_8507", "20%"))                            # ADD
print(m.apply("duty_8507", "15%"))                            # UPDATE
print(m.apply("duty_8507", "15%"))                            # NONE
print(m.apply("duty_8507", None))                             # DELETE
print(len(m.history), "audit rows")                           # 4
```

## 💻 Code Example — Advanced
```python
# Production: LLM-assisted decision with strict schema, TTL cleanup, async, error handling.
import asyncio                                                # async
import json                                                   # parse
import logging                                                # logs
import time                                                   # time
from typing import Literal                                    # literal types
from pydantic import BaseModel                                # pydantic v2
from openai import AsyncOpenAI, OpenAIError                   # client

log = logging.getLogger("mem_update")                         # logger

class Decision(BaseModel):
    action: Literal["ADD", "UPDATE", "NONE", "DELETE"]        # allowed actions
    target_id: str | None = None                              # which memory to change

class Store:
    def __init__(self) -> None:
        self.rows: dict[str, dict] = {}                       # id -> {text, updated, ttl_days}
        self.client = AsyncOpenAI()                           # needs OPENAI_API_KEY

    async def decide(self, new_fact: str, similar: list[tuple[str, str]]) -> Decision:
        listing = "\n".join(f"{i}: {t}" for i, t in similar) or "(none)"   # existing similar
        prompt = (f"Existing memories:\n{listing}\n\nNew fact: {new_fact}\n"
                  'Return JSON {"action": "ADD|UPDATE|NONE|DELETE", "target_id": id|null}.')
        try:
            r = await self.client.chat.completions.create(
                model="gpt-4o-mini", temperature=0, max_tokens=60,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}])
            return Decision.model_validate(json.loads(r.choices[0].message.content or "{}"))
        except (OpenAIError, ValueError) as exc:              # API or schema error
            log.warning("decide failed, default ADD: %s", exc)
            return Decision(action="ADD")                     # safe default

    async def upsert(self, new_id: str, fact: str, similar: list[tuple[str, str]]) -> str:
        d = await self.decide(fact, similar)                  # ask for a decision
        now = time.time()
        if d.action == "ADD":
            self.rows[new_id] = {"text": fact, "updated": now, "ttl_days": 180}
        elif d.action == "UPDATE" and d.target_id in self.rows:
            self.rows[d.target_id].update(text=fact, updated=now)
        elif d.action == "DELETE" and d.target_id in self.rows:
            del self.rows[d.target_id]
        return d.action

    def expire(self) -> int:
        now = time.time()
        dead = [i for i, r in self.rows.items() if now - r["updated"] > r["ttl_days"] * 86_400]
        for i in dead:
            del self.rows[i]                                  # forget stale memories
        return len(dead)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks                  # app + bg
from pydantic import BaseModel                                # model

app = FastAPI()                                               # app
store = Store()                                               # shared store (DB in prod)

class Fact(BaseModel):
    id: str                                                   # new memory id
    text: str                                                 # fact text

@app.post("/memory")
async def write(f: Fact, bg: BackgroundTasks) -> dict[str, str]:
    bg.add_task(store.upsert, f.id, f.text, [])               # update off the hot path
    return {"status": "queued"}

@app.post("/memory/expire")
async def expire() -> dict[str, int]:
    return {"expired": store.expire()}                        # call from a cron job
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph supports long-term memory through a `Store` (namespaced key-value, optional semantic search). Two update modes appear in LangChain's memory guidance: update "in the hot path" (inside the node, before replying) or "in the background" (separate node/job after replying).

```python
from langgraph.store.memory import InMemoryStore              # dev store (use Postgres in prod)

store_lg = InMemoryStore()                                    # key-value store
ns = ("users", "u1", "facts")                                 # namespace tuple
store_lg.put(ns, "duty_8507", {"text": "20%", "version": 1})  # ADD
store_lg.put(ns, "duty_8507", {"text": "15%", "version": 2})  # UPDATE = overwrite same key
item = store_lg.get(ns, "duty_8507")                          # read back
print(item.value)                                             # {'text': '15%', 'version': 2}
# In a graph node, receive the store via `def node(state, *, store): ...` when compiled with store=...
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Append-only writes
✅ Correct: check for similar memories and update.

```python
# Wrong
db.insert(fact)
# Right
action = decide(fact, db.similar(fact)); apply(action)
```

❌ Mistake 2: Overwriting without history (cannot audit or roll back)
✅ Correct: version rows.

```python
# Wrong
row.text = new
# Right
history.append(row.copy()); row.text = new; row.version += 1
```

---

## 🧠 Tricky Interview Question
**Q**: "A user jokes 'I'm from Mars' and the bot stores it and keeps replying with Mars. How do you prevent bad memory writes?"

**Answer**: Add write gating: confidence/importance thresholds, only store user-stated facts relevant to the product, require explicit statements, keep source and timestamp, allow users to view/edit/delete memories, and let low-confidence memories expire quickly. Memory poisoning (including prompt injection) is a real security risk.

---

## ⚫ Interview Questions + Answers

Q1: Name the four update actions. (Easy)
A1: ADD, UPDATE, DELETE, NONE.

Q2: Hot path vs background updates? (Easy)
A2: Hot path = update before replying (fresh but slower); background = after replying (fast but eventual).

Q3: How do you handle contradictions? (Medium)
A3: Key facts by attribute, newest wins, keep history with timestamps, or ask the user to confirm.

Q4: What is TTL and why use it? (Medium)
A4: Time-to-live; stale memories expire automatically so the store stays small and accurate.

Q5: How do you make updates safe and auditable? (Hard)
A5: Schema-validated decisions, default-to-ADD on failure, versioned rows, audit log, user-visible memory with delete, idempotent writes, and write gating against poisoning.

---

## 🔷 When to Use + When Not to Use
✅ Use LLM-decided updates when:
- Facts are free text and change

❌ Avoid when:
- Fields are structured (use plain DB upserts, cheaper and deterministic)

---

## 📊 Visual Diagram
```
 new fact ─► find similar ─► decide ─┬ ADD    ─► insert
                                     ├ UPDATE ─► new version
                                     ├ DELETE ─► tombstone
                                     └ NONE   ─► ignore
 cron: merge duplicates, expire TTL, decay importance
```

---

## 💰 Cost Impact
LLM-decided update = about 200-400 tokens per write (roughly $0.0001 on gpt-4o-mini). Optimise: rule-based fast path for structured keys, call the LLM only when similar memories exist, batch writes, run in background, use small models.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Upsert | Insert or update | नया डालो या update करो |
| TTL | Expiry time | expire होने का समय |
| Tombstone | Marker for deleted | delete का निशान |
| Hot path | During the request | request के दौरान |
| Memory poisoning | Bad data injected | गलत data डालना |

---

## ⚡ 3-Line Summary
English: Decide ADD, UPDATE, DELETE or NONE for each new fact and version the changes. Run cleanup and merging in the background with TTLs. Gate writes to avoid poisoning.
Hindi: हर नए fact पर ADD, UPDATE, DELETE या NONE तय करो और बदलाव version करो। Cleanup और merge background में TTL के साथ चलाओ। Poisoning से बचने के लिए writes gate करो।

---

## ➡️ Next Topic
**386. Memory for Multi-User Apps** (already covered) - then continue to the Evaluation section, starting at **394. Context Recall Score**.
