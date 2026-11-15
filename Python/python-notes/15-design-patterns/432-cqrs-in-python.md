---

# 432. CQRS in Python
# हिंदी में: CQRS in Python (Write और Read को अलग करना)

---

## 🔵 Simple Definition (English)
CQRS (Command Query Responsibility Segregation) splits operations into Commands that change state and Queries that only read. At the larger scale the write model and the read model are separate data structures, with the read side updated from events.

## 🔵 सरल परिभाषा (Hindi)
CQRS (Command Query Responsibility Segregation) operations को Commands (state बदलते हैं) और Queries (सिर्फ पढ़ते हैं) में बांटता है। बड़े स्तर पर write model और read model अलग data structures होते हैं, और read side events से update होती है।

---

## 🔴 Problem it Solves
One model serves both writing (needs strict rules, normalized tables) and reading (needs fast, denormalized, joined views). Dashboards with heavy joins slow down order placement, and read-optimizing the schema makes writes complicated. CQRS lets each side be designed, scaled, and cached for its own job.

## 🔴 यह क्यों बना? (Hindi)
एक ही model लिखने (सख्त नियम, normalized tables) और पढ़ने (तेज, denormalized, joined views) दोनों के लिए इस्तेमाल होता है। भारी joins वाले dashboards order placement को धीमा करते हैं, और read के लिए schema बदलने से writes जटिल हो जाते हैं। CQRS हर side को अपने काम के लिए design, scale और cache करने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends a Command (PlaceOrder) to a command handler
Step 2 → Handler validates and writes to the WRITE store
Step 3 → Handler emits an event (OrderPlaced)
Step 4 → A projection listens and updates the READ model (per-customer totals)
Step 5 → Client sends a Query (customer summary) to a query function
Step 6 → Query reads only from the read model: fast, no side effects
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client Command (PlaceOrder) को command handler को भेजता है
Step 2 → Handler validate करके WRITE store में लिखता है
Step 3 → Handler event (OrderPlaced) emit करता है
Step 4 → Projection सुनकर READ model (per-customer totals) update करता है
Step 5 → Client Query (customer summary) query function को भेजता है
Step 6 → Query सिर्फ read model से पढ़ता है: तेज, कोई side effect नहीं
```

---

## 🟡 Real World Example
An Amazon/Flipkart-style system writes orders into a normalized transactional database, but the 'My Orders' page and the seller dashboard read from a denormalized store (Elasticsearch, Redis, or a materialized view). Banking apps show balances from a read model that is updated after each transaction event.

## 🟡 Real Example Hindi mein
Amazon/Flipkart जैसा system orders को normalized transactional database में लिखता है, लेकिन 'My Orders' page और seller dashboard denormalized store (Elasticsearch, Redis या materialized view) से पढ़ते हैं। Banking apps balance read model से दिखाते हैं जो हर transaction event के बाद update होती है।

---

## 💻 Code Example — Basic
```python
# Basic CQRS: separate write (command) functions from read (query) functions
db: dict[int, str] = {}                       # write store


def create_user(uid: int, name: str) -> None:     # COMMAND: changes state, returns nothing
    db[uid] = name


def get_user_name(uid: int) -> str | None:        # QUERY: reads only, never changes state
    return db.get(uid)


create_user(1, "Asha")
print(get_user_name(1))
print(get_user_name(2))

# Output:
# Asha
# None
```

## 💻 Code Example — Advanced
```python
# Production style: write model + separate denormalised read model updated from events
from dataclasses import dataclass             # commands/events
from typing import Callable                   # handlers


@dataclass(frozen=True)
class PlaceOrder:                             # COMMAND
    order_id: int
    customer: str
    amount: int


@dataclass(frozen=True)
class OrderPlaced:                            # EVENT emitted by write side
    order_id: int
    customer: str
    amount: int


write_store: dict[int, dict[str, object]] = {}         # normalised write model
read_summary: dict[str, dict[str, int]] = {}           # read model: per-customer totals
subscribers: list[Callable[[OrderPlaced], None]] = []  # projections


def handle_place_order(cmd: PlaceOrder) -> None:
    if cmd.amount <= 0:
        raise ValueError("amount must be positive")
    if cmd.order_id in write_store:
        raise ValueError("duplicate order")
    write_store[cmd.order_id] = {"customer": cmd.customer, "amount": cmd.amount}
    event = OrderPlaced(cmd.order_id, cmd.customer, cmd.amount)
    for s in subscribers:                     # tell read side
        s(event)


def project_summary(e: OrderPlaced) -> None:      # keeps the read model fresh
    row = read_summary.setdefault(e.customer, {"orders": 0, "total": 0})
    row["orders"] += 1
    row["total"] += e.amount


subscribers.append(project_summary)


def query_customer_summary(customer: str) -> dict[str, int]:   # QUERY: one cheap lookup
    return read_summary.get(customer, {"orders": 0, "total": 0})


handle_place_order(PlaceOrder(1, "Asha", 500))
handle_place_order(PlaceOrder(2, "Asha", 250))
print(query_customer_summary("Asha"))
print(query_customer_summary("Ravi"))
try:
    handle_place_order(PlaceOrder(2, "Asha", 10))
except ValueError as e:
    print("Error:", e)

# Output:
# {'orders': 2, 'total': 750}
# {'orders': 0, 'total': 0}
# Error: duplicate order
```

Note: this in-process version is synchronous, so the read model is instantly consistent. With a real broker the read side updates later (eventual consistency), so a query right after a command may briefly return old data.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Command handler | function / class per command | NestJS `@CommandHandler` (`@nestjs/cqrs`) |
| Query handler | function / class per query | NestJS `@QueryHandler` |
| Event bus | own bus, Redis, Kafka | EventBus, Kafka |
| Light version | separate GET vs POST code paths | same |

```python
# Python way
def handle_place_order(cmd: PlaceOrder) -> None: ...      # COMMAND: writes, returns nothing
def query_customer_summary(c: str) -> dict[str, int]: ... # QUERY: reads only
```
```javascript
// JavaScript way (NestJS CQRS)
@CommandHandler(PlaceOrderCommand)
class PlaceOrderHandler { execute(cmd) { /* write */ } }
@QueryHandler(CustomerSummaryQuery)
class SummaryHandler { execute(q) { /* read */ } }
```

Key difference: NestJS has an official `@nestjs/cqrs` package. Python has no standard one, so teams write small handler functions (as above) or use libraries such as `eventsourcing`. The idea is language-independent.

---

## 🟠 FastAPI Connection
HTTP already suggests CQRS: POST/PUT/DELETE endpoints are commands (return 202 or 201, no heavy data) and GET endpoints are queries (side-effect free, cacheable). Start with this light CQRS using separate service functions; add a separate read database only when read load or shape demands it.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()
write_db: list[dict[str, int]] = []
read_total: dict[str, int] = {"sum": 0}


@app.post("/orders", status_code=202)         # COMMAND endpoint: POST, returns no data
def place(amount: int) -> dict[str, str]:
    write_db.append({"amount": amount})
    read_total["sum"] += amount
    return {"status": "accepted"}


@app.get("/orders/total")                     # QUERY endpoint: GET, side-effect free
def total() -> dict[str, int]:
    return read_total


c = TestClient(app)
print(c.post("/orders", params={"amount": 100}).status_code, c.get("/orders/total").json())

# Output:
# 202 {'sum': 100}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A query that changes state
✅ Correct: queries are side-effect free

```python
# Wrong
def get_user(uid: int):
    db[uid]["last_seen"] = now()          # a 'read' that writes
    return db[uid]
# Right: a separate command touch_user(uid) updates last_seen
```

❌ Mistake 2: Caching a query without invalidating on commands
✅ Correct: invalidate or rebuild the read model when a command succeeds

```python
# Wrong: @lru_cache on get_name; rename() later -> stale value forever
# Right: rename() calls get_name.cache_clear(), or the projection refreshes the read model
```

❌ Mistake 3: Adopting full CQRS + event sourcing for a simple CRUD app
✅ Correct: start with separate functions; split stores only when needed

```python
# Wrong: two databases, a broker and projections for a todo list
# Right: create_todo() / list_todos() as separate functions on one database
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from functools import lru_cache
db = {1: "Asha"}
@lru_cache
def get_name(i): return db[i]
def rename(i, n): db[i] = n
print(get_name(1)); rename(1, "Ravi"); print(get_name(1), db[1])
```
Answer: Output: `Asha` then `Asha Ravi`. The first query is cached by `lru_cache`. After the command `rename`, the database holds `'Ravi'` but the cached query still returns `'Asha'`, so the read side is stale. In CQRS the read model must be updated or invalidated whenever a command changes the write model.

---

## ⚫ Interview Questions + Answers

Q1: What is CQRS?
A1: Separating commands (change state, return nothing or an id) from queries (return data, change nothing). In full CQRS the write and read models are different and the read model is built from events.

Q2: CQRS vs CRUD?
A2: CRUD uses one model for create/read/update/delete. CQRS uses different models and paths for writes and reads, which helps when read and write needs differ greatly.

Q3: What is eventual consistency?
A3: The read model is updated after the write completes, so for a short time a query can return old data. Design the UI for it (show 'processing', or read-your-writes from the write side).

Q4: CQRS vs Event Sourcing?
A4: Independent ideas often used together. Event sourcing stores state as a sequence of events; CQRS separates read and write models. You can do CQRS with a normal write database.

Q5: When is CQRS a bad idea?
A5: Simple CRUD apps, small teams, and cases needing strict immediate consistency. The extra moving parts (projections, brokers, replay) cost more than they save.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reads and writes have very different load or shape
- Dashboards need denormalized, pre-joined data
- You already use events between services

❌ Avoid when:
- Simple CRUD application
- You need strong consistency everywhere
- Team is not ready to operate projections and a broker

---

## 📊 Visual Diagram
```
        COMMAND side                         QUERY side
POST /orders -> handle_place_order     GET /customers/Asha/summary
        |                                        ^
        v                                        |
  write_store (normalized)     event      read_summary (denormalized)
        +--- OrderPlaced -----> projection ------+
Command returns nothing;  Query changes nothing
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Command | Request to change state | State बदलने का अनुरोध |
| Query | Request to read data | Data पढ़ने का अनुरोध |
| Projection | Code building the read model from events | Events से read model बनाने वाला code |
| Read model | Data shape optimized for reading | पढ़ने के लिए बना data shape |
| Eventual consistency | Read side catches up later | Read side बाद में अपडेट होती है |

---

## ⚡ 3-Line Summary
English: CQRS separates commands that change state from queries that only read, and in full form keeps separate write and read models linked by events. It shines when read and write needs differ, but costs complexity and brings eventual consistency. Start with separate functions and split stores only if needed.
Hindi: CQRS state बदलने वाले commands को सिर्फ पढ़ने वाले queries से अलग करता है, और पूरे रूप में events से जुड़े अलग write और read models रखता है। जब read और write की जरूरतें अलग हों तब यह चमकता है, पर जटिलता और eventual consistency लाता है। अलग functions से शुरू करें और जरूरत पड़ने पर ही stores अलग करें।

---

## ➡️ Next Topic
**433. Event-Driven in Python** — build systems where producers emit events and consumers react asynchronously.
