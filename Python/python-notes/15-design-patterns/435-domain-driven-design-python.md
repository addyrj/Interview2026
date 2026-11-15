---

# 435. Domain Driven Design Python
# हिंदी में: Domain Driven Design (DDD) Python में

---

## 🔵 Simple Definition (English)
Domain Driven Design (DDD) is a way to build software around the business itself. You model the business with the same words the experts use (Order, Seat, Payment) and protect its rules inside objects called entities, value objects and aggregates.

## 🔵 सरल परिभाषा (Hindi)
Domain Driven Design (DDD) software को business के आसपास बनाने का तरीका है। आप business को उन्हीं शब्दों में model करते हैं जो experts इस्तेमाल करते हैं (Order, Seat, Payment) और उसके rules को entities, value objects और aggregates के अंदर सुरक्षित रखते हैं।

---

## 🔴 Problem it Solves
In big systems the code and the business drift apart. Developers talk about "rows" and "status = 3" while the business talks about "a placed order" and "refund window". Result: rules are copy-pasted in many services, bugs appear when someone sets a status directly, and new team members cannot read the code as a description of the business. DDD gives a shared language and clear boundaries so rules live in one place.

## 🔴 यह क्यों बना? (Hindi)
बड़े systems में code और business अलग हो जाते हैं। Developers "rows" और "status = 3" की बात करते हैं जबकि business "placed order" और "refund window" की। नतीजा: rules कई services में copy-paste होते हैं, कोई status सीधे बदल दे तो bugs आते हैं, और नया member code को business के वर्णन की तरह नहीं पढ़ पाता। DDD एक साझा भाषा और साफ सीमाएँ देता है ताकि rules एक ही जगह रहें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ubiquitous language: devs and business use the SAME words in talk AND code
Step 2 → Split into bounded contexts (Ordering, Payments, Shipping), each with its own model
Step 3 → Value Object: immutable, equal by value (Money, Address) - no id
Step 4 → Entity: has identity that survives changes (Order "ORD-1")
Step 5 → Aggregate: a cluster changed as one unit; the Aggregate Root is the only door in
Step 6 → Invariants (rules that must always hold) are checked INSIDE the aggregate
Step 7 → Domain events ("OrderPlaced") announce what happened; other contexts react
Step 8 → Repository loads/saves whole aggregates; one aggregate per transaction
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Ubiquitous language: devs और business बातचीत और code में एक ही शब्द बोलें
Step 2 → Bounded contexts में बाँटो (Ordering, Payments, Shipping), हर एक का अपना model
Step 3 → Value Object: immutable, value से बराबर (Money, Address) - कोई id नहीं
Step 4 → Entity: identity होती है जो बदलावों में भी वही रहती है (Order "ORD-1")
Step 5 → Aggregate: objects का समूह जो एक unit की तरह बदलता है; Aggregate Root अकेला दरवाज़ा है
Step 6 → Invariants (जो rules हमेशा सही रहने चाहिए) aggregate के अंदर check होते हैं
Step 7 → Domain events ("OrderPlaced") बताते हैं क्या हुआ; दूसरे contexts react करते हैं
Step 8 → Repository पूरा aggregate load/save करता है; एक transaction में एक aggregate
```

---

## 🟡 Real World Example
BookMyShow-style seat booking. The `Show` aggregate owns its reserved seats. The invariant "never sell more seats than the capacity, and max 6 per booking" is checked inside `Show.reserve()`, so no route, script or admin tool can break it. After a successful reservation the aggregate raises `SeatsReserved`; the Payments context listens and starts a 10-minute payment timer, and the Notification context sends an SMS. Zomato does the same with `Order`, `Delivery` and `Restaurant` as separate contexts.

## 🟡 Real Example Hindi mein
BookMyShow जैसी seat booking। `Show` aggregate अपनी reserved seats का मालिक है। Invariant "capacity से ज़्यादा seats कभी नहीं बिकेंगी, और एक booking में max 6" `Show.reserve()` के अंदर check होता है, इसलिए कोई route, script या admin tool इसे तोड़ नहीं सकता। सफल reservation के बाद aggregate `SeatsReserved` event उठाता है; Payments context सुनकर 10 मिनट का payment timer शुरू करता है और Notification context SMS भेजता है। Zomato भी `Order`, `Delivery` और `Restaurant` को अलग contexts में रखकर यही करता है।

---

## 💻 Code Example — Basic
```python
# Basic DDD: Value Object, Entity, Aggregate Root with invariants
from dataclasses import dataclass, field          # data classes
from decimal import Decimal                       # exact money math


@dataclass(frozen=True)                           # VALUE OBJECT: immutable, equal by value
class Money:
    amount: Decimal                               # numeric part
    currency: str = "INR"                         # currency code

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:       # rule: no mixing currencies
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)   # new object, never mutate


@dataclass(frozen=True)
class OrderLine:                                  # value object inside the aggregate
    sku: str
    price: Money
    qty: int


@dataclass
class Order:                                      # AGGREGATE ROOT: only way in/out of its lines
    id: str                                       # identity (entity)
    lines: list[OrderLine] = field(default_factory=list)
    status: str = "DRAFT"
    events: list[str] = field(default_factory=list)   # domain events raised

    def add_line(self, sku: str, price: Money, qty: int) -> None:
        if self.status != "DRAFT":                # invariant: only draft orders change
            raise ValueError("order is locked")
        if qty <= 0:                              # invariant: positive quantity
            raise ValueError("qty must be > 0")
        self.lines.append(OrderLine(sku, price, qty))   # allowed change

    def total(self) -> Money:
        total = Money(Decimal("0"))               # start from zero
        for line in self.lines:                   # sum every line
            total = total + Money(line.price.amount * line.qty, line.price.currency)
        return total

    def place(self) -> None:
        if not self.lines:                        # invariant: not empty
            raise ValueError("empty order")
        self.status = "PLACED"                    # state transition
        self.events.append(f"OrderPlaced({self.id})")   # record domain event


print(Money(Decimal("10")) == Money(Decimal("10")))   # equal by value -> True
o = Order("ORD-1")                                # create aggregate
o.add_line("biryani", Money(Decimal("250")), 2)   # add lines through the root
o.add_line("raita", Money(Decimal("40")), 1)
print(o.total())                                  # Money(amount=Decimal('540'), currency='INR')
o.place()                                         # place order
print(o.status, o.events)
try:
    o.add_line("coke", Money(Decimal("60")), 1)   # locked now
except ValueError as e:
    print("Error:", e)
try:
    Money(Decimal("1")).amount = Decimal("2")     # value objects are frozen
except Exception as e:
    print(type(e).__name__)

# Output (real run, Python 3.13):
# True
# Money(amount=Decimal('540'), currency='INR')
# PLACED ['OrderPlaced(ORD-1)']
# Error: order is locked
# FrozenInstanceError
```

## 💻 Code Example — Advanced
```python
# Advanced DDD: aggregate + domain events + repository + unit of work + FastAPI
from __future__ import annotations                # allow forward references
from dataclasses import dataclass, field          # entities / events
from typing import Callable, Protocol             # types

from fastapi import FastAPI, HTTPException        # web layer
from fastapi.testclient import TestClient         # tests


# ---------- domain ----------
@dataclass(frozen=True)
class SeatsReserved:                              # domain event (past tense, immutable)
    show_id: str
    user: str
    seats: int


@dataclass
class Show:                                       # aggregate root (BookMyShow style)
    id: str
    capacity: int
    reserved: dict[str, int] = field(default_factory=dict)   # user -> seats
    _events: list[SeatsReserved] = field(default_factory=list, repr=False)

    @property
    def free(self) -> int:
        return self.capacity - sum(self.reserved.values())   # derived value

    def reserve(self, user: str, seats: int) -> None:
        if seats < 1 or seats > 6:                # invariant 1
            raise ValueError("1 to 6 seats per booking")
        if seats > self.free:                     # invariant 2: never overbook
            raise ValueError("not enough seats")
        self.reserved[user] = self.reserved.get(user, 0) + seats
        self._events.append(SeatsReserved(self.id, user, seats))   # raise event

    def pull_events(self) -> list[SeatsReserved]:
        events, self._events = self._events, []   # hand over and clear
        return events


class ShowRepository(Protocol):                   # repository: collection-like port
    def get(self, show_id: str) -> Show | None: ...
    def add(self, show: Show) -> None: ...


# ---------- infrastructure ----------
class InMemoryShows:                              # adapter
    def __init__(self) -> None:
        self._d: dict[str, Show] = {}
    def get(self, show_id: str) -> Show | None:
        return self._d.get(show_id)
    def add(self, show: Show) -> None:
        self._d[show.id] = show


class UnitOfWork:                                 # one business transaction
    def __init__(self, shows: ShowRepository, publish: Callable[[object], None]) -> None:
        self.shows, self._publish = shows, publish

    def commit(self, *aggregates: Show) -> None:
        for agg in aggregates:                    # after "saving", publish its events
            for event in agg.pull_events():
                self._publish(event)


# ---------- application service ----------
def reserve_seats(uow: UnitOfWork, show_id: str, user: str, seats: int) -> int:
    show = uow.shows.get(show_id)                 # load aggregate
    if show is None:
        raise LookupError("show not found")
    show.reserve(user, seats)                     # all rules live in the aggregate
    uow.commit(show)                              # persist + publish events
    return show.free


# ---------- interface ----------
log: list[str] = []                               # fake message bus
repo = InMemoryShows()
repo.add(Show("S1", capacity=8))
uow = UnitOfWork(repo, lambda e: log.append(repr(e)))   # event handler = log
app = FastAPI()


@app.post("/shows/{show_id}/reserve")
def reserve(show_id: str, user: str, seats: int) -> dict[str, int]:
    try:
        return {"free": reserve_seats(uow, show_id, user, seats)}
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))


c = TestClient(app)
print(c.post("/shows/S1/reserve", params={"user": "asha", "seats": 5}).json())
print(c.post("/shows/S1/reserve", params={"user": "ravi", "seats": 5}).json())
print(c.post("/shows/S1/reserve", params={"user": "ravi", "seats": 9}).json())
print(c.post("/shows/ZZ/reserve", params={"user": "x", "seats": 1}).status_code)
print(log)

# Output (real run, Python 3.13):
# {'free': 3}
# {'detail': 'not enough seats'}
# {'detail': '1 to 6 seats per booking'}
# 404
# ["SeatsReserved(show_id='S1', user='asha', seats=5)"]
```

Note: the in-memory repository and the list-based "event bus" are stand-ins. In production the repository saves to PostgreSQL in one transaction and events go through an outbox table to Kafka/RabbitMQ so they are never lost. In the second request `ravi` asks for 5 seats when only 3 are free, so the aggregate refuses. Only the successful reservation produced an event.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / TypeScript |
|---------|--------|------------------------|
| Value object | `@dataclass(frozen=True)` | `Object.freeze`, readonly class fields |
| Entity | `@dataclass` with an id | class with id |
| Money math | `decimal.Decimal` | no built-in decimal (use integers or `decimal.js`) |
| Domain events | list of dataclasses | EventEmitter / class instances |
| Framework help | plain Python, `cosmicpython` book patterns | NestJS CQRS module |

```python
# Python way — value object that cannot be changed
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

e = Email("a@b.com")
print(e == Email("a@b.com"))      # True - equal by value
# e.value = "x"                   # FrozenInstanceError
```
```javascript
// JavaScript way — freeze manually and compare manually
class Email {
  constructor(value) { this.value = value; Object.freeze(this); }
  equals(o) { return this.value === o.value; }   // no automatic value equality
}
console.log(new Email("a@b.com").equals(new Email("a@b.com"))); // true
```

Key difference: in JavaScript `==` on two objects compares references, so you write `equals()` yourself. Python dataclasses generate `__eq__` and `__hash__` (when frozen) for you, which makes value objects almost free. Also never use `float` for money in Python or JavaScript: `0.1 + 0.2 != 0.3`.

---

## 🟠 FastAPI Connection
In a DDD style FastAPI app the route is a thin "application service" caller. It reads the request (Pydantic), calls a function that loads an aggregate from a repository, tells the aggregate what to do, commits, and returns. Domain errors (`ValueError`) become HTTP 409/422. The aggregate itself never imports FastAPI.

```python
# FastAPI example — thin route, rules live in the aggregate
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

class Wallet:                                    # tiny aggregate
    def __init__(self, balance: int) -> None:
        self.balance = balance
    def debit(self, amt: int) -> None:
        if amt > self.balance:                   # invariant: no negative balance
            raise ValueError("insufficient funds")
        self.balance -= amt

wallets: dict[str, Wallet] = {"u1": Wallet(100)}  # stand-in repository
app = FastAPI()

@app.post("/wallets/{uid}/debit")
def debit(uid: str, amount: int) -> dict[str, int]:
    try:
        wallets[uid].debit(amount)               # aggregate decides
    except ValueError as e:
        raise HTTPException(409, str(e))         # translate to HTTP
    return {"balance": wallets[uid].balance}

c = TestClient(app)
print(c.post("/wallets/u1/debit", params={"amount": 30}).json())   # {'balance': 70}
print(c.post("/wallets/u1/debit", params={"amount": 90}).status_code)  # 409
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Anemic domain model (entities are just bags of fields, logic in services)
✅ Correct: put behaviour next to the data it protects

```python
# Wrong — anyone can break the rule
order.status = "PLACED"          # skips the "not empty" check
# Right — only the method knows the rules
order.place()                    # raises ValueError if there are no lines
```

❌ Mistake 2: Making huge aggregates (User owns all orders, addresses, payments...)
✅ Correct: keep aggregates small; refer to other aggregates by id

```python
# Wrong: Order holds a full User object and User holds all Orders -> loads everything, locks everything
# Right: Order keeps user_id: int; load the User separately only when needed
```

❌ Mistake 3: Using `float` for money or mutating a value object
✅ Correct: `Decimal` (or integer paise) and `frozen=True`

```python
print(0.1 + 0.2)                 # Wrong: 0.30000000000000004
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))   # Right: 0.3
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from dataclasses import dataclass

@dataclass(frozen=True)
class Tag:
    names: list[str]

t = Tag(["a"])
t.names.append("b")
print(t.names)
print(hash(t))
```
Answer: `['a', 'b']` is printed: `frozen=True` only blocks re-assigning the attribute (`t.names = ...`); it does not make the list inside immutable, so `append` works. Then `hash(t)` raises `TypeError: unhashable type: 'list'` because a frozen dataclass builds `__hash__` from its fields and a list is not hashable. For a real value object use immutable field types such as `tuple[str, ...]` or `frozenset`.

---

## ⚫ Interview Questions + Answers

Q1: Entity vs Value Object?
A1: An entity has identity: two orders with the same data but different ids are different, and an order stays the same order when its status changes. A value object has no identity and is equal when its values are equal (`Money(10, "INR")`); it is immutable, so you replace it instead of changing it.

Q2: What is an aggregate and why only one root?
A2: A cluster of objects treated as one consistency unit. Outside code may hold a reference only to the root, and all changes go through it, so invariants are always checked. One transaction should change one aggregate; use events for cross-aggregate work (eventual consistency).

Q3: What is a bounded context?
A3: A boundary inside which one model and one vocabulary is valid. "Customer" in Billing (tax id, invoices) is a different model from "Customer" in Support (tickets). Contexts talk through APIs or events, not shared tables.

Q4: What is a domain event and how is it published reliably?
A4: A fact in the past tense, immutable (`OrderPlaced`). Reliable publishing uses the Outbox pattern: save the event in the same DB transaction as the aggregate, and a background relay sends it to the broker, so you never lose or invent events.

Q5: DDD vs Clean Architecture?
A5: DDD is about modelling the business core (language, aggregates, contexts). Clean/Hexagonal is about layering the application so that core does not depend on tools. They work well together: the DDD model lives in Clean Architecture's innermost layers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The business domain is complex and changes often (finance, logistics, booking)
- Many rules (invariants) must always hold
- Several teams need clear boundaries
- Domain experts are available to define the language

❌ Avoid when:
- Simple CRUD, reporting dashboards, data pipelines
- Small team with a short-lived product
- Mostly technical problems (e.g., image processing) with little business logic

---

## 📊 Visual Diagram
```
 Bounded Context: Ordering                 Bounded Context: Payments
 +-----------------------------+           +--------------------------+
 | Order (Aggregate Root)      |  event    | Payment (Aggregate Root) |
 |  |-- OrderLine (value obj)  | --------> |  |-- Money (value obj)   |
 |  |-- Money (value obj)      | OrderPlaced|  |-- status             |
 |  '-- invariants: not empty, |           +--------------------------+
 |      qty > 0, lock after    |
 |      placed                 |
 +-----------------------------+
        ^
        | Repository (load/save the whole aggregate)
 [ Application service / FastAPI route ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ubiquitous language | Same words in business and code | business और code की साझा भाषा |
| Bounded context | Boundary of one model | एक model की सीमा |
| Entity | Object with identity | identity वाला object |
| Value object | Immutable, equal by value | immutable, value से बराबर |
| Aggregate root | Single entry to a cluster | समूह का इकलौता प्रवेश द्वार |
| Invariant | Rule that must always hold | जो rule हमेशा सही रहे |
| Domain event | Fact that happened | जो घटना हो चुकी |
| Repository | Collection-like store of aggregates | aggregates का संग्रह |

---

## ⚡ 3-Line Summary
English: Model the business in code using the experts' own words. Protect rules inside small aggregates with immutable value objects. Let events carry facts between bounded contexts.
Hindi: Business को experts के अपने शब्दों में code में model करो। Rules को छोटे aggregates और immutable value objects के अंदर सुरक्षित रखो। Events से bounded contexts के बीच तथ्य भेजो।

---

## ➡️ Next Topic
**436. Deploying FastAPI on VPS** — design is done; now we put the app on a real server with systemd and a firewall.
